# 📄 Document OCR Verification System

<div align="center">

![Project: Document OCR Verification System](https://img.shields.io/badge/project-document--ocr--verification--system-blue)
![Python](https://img.shields.io/badge/language-Python%20%26%20JavaScript-yellow)
![FastAPI](https://img.shields.io/badge/framework-FastAPI-009688)
![Docker](https://img.shields.io/badge/docker-supported-2496ED)
![License: MIT](https://img.shields.io/badge/license-MIT-lightgrey)

</div>

A modern, modular OCR-based document extraction and verification system with REST APIs, multi-document support, a web UI, and optional MOSIP integration for identity verification workflows.

---

## ✨ Highlights

- Pluggable OCR pipelines (EasyOCR / Tesseract / commercial engines)
- Document-type extractors (passports, national IDs, driver licenses)
- Verification engine (rules, confidence scoring, human-in-the-loop reviews)
- REST API for programmatic integration and a web UI for reviewers
- Optional MOSIP adapter for identity provider integration
- Container-ready (Docker / docker-compose)

---

## 🔍 Demo & Screenshots

_Add screenshots or an animated GIF here to show the upload flow, extraction output and review UI._

<p align="center">[Screenshot placeholder]</p>

---

## 📦 Quick links

- Repository: `ZenDev-arc/document-ocr-verification-system`
- Languages: Python, JavaScript, HTML, CSS

---

## 📚 Table of contents

- Overview
- Features
- Architecture
- Quickstart (Docker)
- Quickstart (Local)
- Configuration
- API examples
- MOSIP integration
- Security & privacy
- Contributing
- License

---

## Overview

This repository provides everything needed to run an OCR-driven document extraction and verification service. It's designed to be modular, extensible, and production-friendly with clear separation between OCR workers, the API layer, and UI components.

---

## Features

- Multi-format OCR processing for images and PDFs
- Field-level extraction with confidence scores
- Rules-based and fuzzy verification logic
- Human-in-the-loop review dashboard
- Configurable pipelines per document type
- MOSIP adapter for optional identity verification
- Docker support for reproducible deployments

---

## Architecture (high level)

```
 Client (Web/Mobile)
      |
      v
  FastAPI REST API  <->  Database (Postgres / SQLite)
      |
      v
  Task Queue (Redis / Celery)  ->  OCR Workers (EasyOCR/Tesseract)
      |
      v
  Verification Engine  ->  Audit Logs / Reviewer UI
      |
      v
  Optional: MOSIP Integration
```

---

## Docker Quickstart (recommended)

1. Copy the example environment file and edit values:

```bash
cp .env.example .env
# Edit .env with your values (DB connection, MOSIP keys, OCR engine)
```

2. Start services with docker-compose:

```bash
docker-compose up --build
```

3. Open the services:

- API: http://localhost:8000
- API docs (if FastAPI): http://localhost:8000/docs
- Frontend: http://localhost:3000 (if a frontend service exists)

---

## Local Development (Python + Frontend)

Backend (Python):

```bash
# Create venv and install
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run the API (example)
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Frontend (if present):

```bash
cd frontend
npm install
npm run dev
```

---

## Configuration

Create a `.env` file with the important environment variables (example):

```env
# Server
HOST=0.0.0.0
PORT=8000
SECRET_KEY=change-me

# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/ocrdb

# OCR
OCR_ENGINE=easyocr
OCR_LANGUAGES=en
OCR_GPU=false

# MOSIP (optional)
MOSIP_ENABLED=false
MOSIP_BASE_URL=
MOSIP_CLIENT_ID=
MOSIP_CLIENT_SECRET=
```

Document type mappings, extraction rules and verification thresholds can be adjusted in the backend configuration modules (search for `config`, `settings`, or `.env` usage).

---

## API examples

Upload a document (multipart/form-data):

```bash
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@/path/to/document.jpg" \
  -F "document_type=passport"
```

Check job status / result:

```bash
curl "http://localhost:8000/api/documents/result/<JOB_ID>"
```

Basic health check:

```bash
curl "http://localhost:8000/health"
```

---

## MOSIP Integration (optional)

If you want to connect to MOSIP for identity verification:

1. Set `MOSIP_ENABLED=true` and configure the base URL and credentials.
2. Ensure any required certificate or trust material for MOSIP endpoints is available to the container / service.
3. Review the adapter implementation under `integrations/mosip` (if present) for request/response mappings and endpoints.

---

## Security & Privacy

This project may process sensitive PII. Follow best practices:

- Use TLS for all network traffic
- Store secrets in a secret manager (do not commit to git)
- Encrypt sensitive fields at rest
- Log redaction: avoid logging full PII values
- Role-based access control for reviewer UI and API
- Audit trail for approvals and manual overrides

---

## Testing

Run backend tests:

```bash
pytest tests/ -v
```

Run frontend tests (if applicable):

```bash
cd frontend && npm test
```

---

## Contributing

Contributions are welcome. A suggested workflow:

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes with clear messages
4. Open a Pull Request with a description and tests

Please follow the code style (PEP 8 for Python) and include tests for new behavior.

---

## License

This project is released under the MIT License. See LICENSE for details.

---

## Maintainers & Contact

Maintainer: ZenDev-arc

For bugs or feature requests, please open an issue in this repository.

---

*I updated README.md to a polished, visually appealing layout with clear quickstart instructions, architecture overview, and security notes. If you'd like, I can include screenshots, performance tips, or automatically generated API docs links after inspecting the codebase.*
