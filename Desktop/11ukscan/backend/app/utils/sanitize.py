"""
File sanitization and path traversal prevention utilities.

SECURITY CRITICAL: All uploaded filenames MUST pass through
``sanitize_filename()`` before being written to disk. This prevents:
- Path traversal attacks (../../etc/passwd)
- Null byte injection
- Special character exploitation
- Filename collision via UUID prefixing

Never write files using raw user-supplied filenames.
"""

from __future__ import annotations

import re
import unicodedata
import uuid
from pathlib import Path


# Characters that are safe in filenames (alphanumerics, hyphens, underscores, dots)
_SAFE_FILENAME_PATTERN = re.compile(r"[^\w\-.]")


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a user-supplied filename to be safe for filesystem use.

    Steps applied:
    1. Unicode NFKD normalisation → strip non-ASCII characters.
    2. Replace any character that is not alphanumeric, hyphen, underscore,
       or dot with an underscore.
    3. Strip leading/trailing dots and spaces.
    4. Collapse consecutive underscores/hyphens.
    5. Truncate stem to 100 characters to prevent filesystem limits.

    Args:
        filename: Raw filename from the upload request.

    Returns:
        A sanitized filename string safe for filesystem use.

    Examples:
        >>> sanitize_filename("my statement (Jan 2024).pdf")
        'my_statement__Jan_2024_.pdf'
        >>> sanitize_filename("../../etc/passwd")
        'etc_passwd'
    """
    # NFKD normalise and drop non-ASCII
    normalized = unicodedata.normalize("NFKD", filename)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")

    # Replace unsafe characters
    safe = _SAFE_FILENAME_PATTERN.sub("_", ascii_name)

    # Build Path to separate stem and suffix reliably
    path = Path(safe)
    stem = path.stem.strip(". ") or "upload"
    suffix = path.suffix.lower()  # Normalise extension to lowercase

    # Truncate long stems
    stem = stem[:100]

    return f"{stem}{suffix}"


def build_secure_upload_path(upload_dir: Path, original_filename: str, job_id: str) -> Path:
    """
    Build a secure absolute path for storing an uploaded file.

    Prefixes the sanitized filename with the job UUID so that:
    - Two simultaneous uploads of the same filename never collide.
    - Files are trivially associated with their processing job.
    - The original filename cannot traverse the upload directory.

    Args:
        upload_dir:        Configured upload directory (absolute Path).
        original_filename: Raw filename from the upload request.
        job_id:            UUID string for this processing job.

    Returns:
        Absolute Path within ``upload_dir``. Safe for filesystem writes.

    Raises:
        ValueError: If the resolved path escapes the upload directory
                    (should never happen after sanitization, but belt-
                    and-suspenders check).

    Examples:
        >>> build_secure_upload_path(Path('/uploads'), 'stmt.pdf', 'abc-123')
        PosixPath('/uploads/abc-123_stmt.pdf')
    """
    safe_name = sanitize_filename(original_filename)
    target = upload_dir.resolve() / f"{job_id}_{safe_name}"

    # Paranoid path traversal check
    if not str(target).startswith(str(upload_dir.resolve())):
        raise ValueError(
            f"Path traversal attempt detected: resolved path {target} "
            f"escapes upload directory {upload_dir}."
        )

    return target


def build_output_path(output_dir: Path, job_id: str, extension: str) -> Path:
    """
    Build a deterministic output file path for a given job and file type.

    Args:
        output_dir: Configured output directory (absolute Path).
        job_id:     UUID string for the processing job.
        extension:  File extension including dot, e.g. ".csv" or ".xlsx".

    Returns:
        Absolute Path for the output file.

    Examples:
        >>> build_output_path(Path('/outputs'), 'abc-123', '.csv')
        PosixPath('/outputs/abc-123.csv')
    """
    return output_dir.resolve() / f"{job_id}{extension}"
