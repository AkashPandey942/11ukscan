# BankScan — PDF Bank Statement Parser

**Enterprise-grade PDF bank statement parser built with FastAPI + Next.js.**

> Upload a Monzo Business PDF statement → Get structured CSV & Excel exports instantly.

---

## Architecture

```
BankScan uses Clean Architecture + SOLID Principles:

PDF Upload → FileService (validate) → PDFReaderAdapter (extract)
→ BankParserRegistry (detect) → MonzoParser (parse)
→ ExportService (CSV + Excel) → InMemoryRepository (store)
→ JSON API Response → Next.js Dashboard
```

---

## Prerequisites

| Tool | Version |
|---|---|
| Python | 3.11+ |
| Node.js | 18+ |
| npm | 9+ |

---

## Quick Start

### 1. Clone the Repository

```bash
git clone <repo-url>
cd 11ukscan
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows PowerShell:
.venv\Scripts\Activate.ps1

# macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your settings

# Start the API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API will be available at: **http://localhost:8000**

> **Note for Windows users**: `python-magic` requires `libmagic`.
> Install via: `pip install python-magic-bin` (includes binary)
> or download from https://gnuwin32.sourceforge.net/packages/file.htm

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
copy .env.local.example .env.local
# Set NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Start development server
npm run dev
```

Frontend will be available at: **http://localhost:3000**

---

## API Documentation

With `DEBUG=true` in `.env`, interactive docs are at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc:       http://localhost:8000/api/redoc

### Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/upload` | Upload & process a PDF statement |
| `GET` | `/api/v1/download/csv/{job_id}` | Download CSV export |
| `GET` | `/api/v1/download/excel/{job_id}` | Download Excel export |
| `GET` | `/api/v1/health` | Health check |

---

## Running Tests

```bash
cd backend

# Run all unit tests
pytest tests/unit/ -v

# Run with coverage report
pytest tests/ --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html
```

---

## Docker Deployment

```bash
# Build and start all services
docker compose up --build

# Run in background
docker compose up -d --build

# View logs
docker compose logs -f backend

# Stop all services
docker compose down
```

---

## Adding a New Bank Parser

1. Create `backend/app/parsers/hsbc_parser.py`
2. Inherit from `AbstractBankStatementParser`
3. Set `bank_name` and `fingerprints` class attributes
4. Implement `extract_header()` and `extract_transactions()`
5. Decorate with `@BankParserRegistry.register`

```python
from app.parsers.base_parser import AbstractBankStatementParser
from app.parsers.parser_registry import BankParserRegistry

@BankParserRegistry.register
class HSBCParser(AbstractBankStatementParser):
    bank_name = "HSBC"
    fingerprints = ["HSBC Bank plc", "HSBC Statement"]

    def extract_header(self, pages): ...
    def extract_transactions(self, pages): ...
```

**That's it.** Import in `main.py` and the auto-detector will use it.

---

## Project Structure

```
11ukscan/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # FastAPI route handlers
│   │   ├── core/            # Config, logging, exceptions, middleware
│   │   ├── models/          # Domain models (Transaction, ParsedStatement)
│   │   ├── parsers/         # PDF reading + bank parser abstractions
│   │   ├── services/        # Business logic orchestration
│   │   ├── exporters/       # CSV + Excel export engines
│   │   ├── repositories/    # Data persistence layer
│   │   └── utils/           # Currency, date, sanitize helpers
│   ├── tests/               # Unit + integration tests
│   └── requirements.txt
├── frontend/                # Next.js 14 + TypeScript + Tailwind
└── docker-compose.yml
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DEBUG` | `false` | Enables API docs and dev formatter |
| `LOG_LEVEL` | `INFO` | Python log level |
| `MAX_UPLOAD_SIZE_MB` | `50` | Max PDF upload size |
| `MAX_PDF_PAGES` | `60` | Max pages per PDF |
| `UPLOAD_DIR` | `uploads` | Temp upload directory |
| `OUTPUT_DIR` | `outputs` | Export file directory |
| `ALLOWED_ORIGINS` | `["http://localhost:3000"]` | CORS allowed origins |

---

## Security Notes

- All uploaded filenames are sanitized before disk writes.
- UUID-prefixed paths prevent path traversal attacks.
- MIME type + magic bytes checked before file is accepted.
- API docs disabled in production (DEBUG=false).
- Non-root Docker user in production image.
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.) on all responses.

---

## Roadmap

- [ ] MongoDB persistence layer
- [ ] JWT authentication
- [ ] HSBC, Barclays, Lloyds parsers
- [ ] OCR support (Tesseract / Google Document AI)
- [ ] Bulk PDF upload
- [ ] Transaction categorisation (AI)
- [ ] AWS S3 / Cloud Storage integration
- [ ] Background processing (Celery)

---

## License

MIT License — see LICENSE file for details.
