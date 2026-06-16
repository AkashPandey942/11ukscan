"""
Unit tests for CSVExporter.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from app.exporters.csv_exporter import CSVExporter


class TestCSVExporter:
    """Tests for CSVExporter output format and content correctness."""

    @pytest.fixture
    def exporter(self):
        return CSVExporter()

    def test_export_creates_file(self, exporter, sample_parsed_statement, temp_output_dir):
        output_path = temp_output_dir / "test.csv"
        result = exporter.export(sample_parsed_statement, output_path)
        assert result.exists()

    def test_extension_is_csv(self):
        assert CSVExporter.extension == ".csv"

    def test_correct_row_count(self, exporter, sample_parsed_statement, temp_output_dir):
        output_path = temp_output_dir / "test.csv"
        exporter.export(sample_parsed_statement, output_path)

        with open(output_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == len(sample_parsed_statement.transactions)

    def test_correct_headers(self, exporter, sample_parsed_statement, temp_output_dir):
        output_path = temp_output_dir / "test.csv"
        exporter.export(sample_parsed_statement, output_path)

        with open(output_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            assert set(reader.fieldnames) == {"Date", "Description", "Amount", "Balance"}

    def test_first_row_values(self, exporter, sample_parsed_statement, temp_output_dir):
        output_path = temp_output_dir / "test.csv"
        exporter.export(sample_parsed_statement, output_path)

        with open(output_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            first_row = next(reader)

        first_tx = sample_parsed_statement.transactions[0]
        assert first_row["Date"] == first_tx.date.isoformat()
        assert first_row["Description"] == first_tx.description

    def test_bom_encoding_for_excel(self, exporter, sample_parsed_statement, temp_output_dir):
        """Verify UTF-8 BOM is present for Windows Excel compatibility."""
        output_path = temp_output_dir / "test.csv"
        exporter.export(sample_parsed_statement, output_path)

        raw_bytes = output_path.read_bytes()
        assert raw_bytes[:3] == b"\xef\xbb\xbf", "Missing UTF-8 BOM"
