# 📄 Document OCR Verification System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.68%2B-009688?style=flat-square&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Supported-2496ED?style=flat-square&logo=docker)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

**A comprehensive OCR-based document extraction and verification system with REST APIs, supporting multiple document types and optional MOSIP integration for identity verification workflows.**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [API Docs](#-api-documentation) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 📚 Table of Contents

- [Overview](#overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Configuration](#-configuration)
- [Docker Deployment](#-docker-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## Overview

This is a production-ready OCR-based document processing system that extracts, validates, and verifies information from various document types. It provides REST APIs for seamless integration with other applications and supports optional MOSIP integration for identity verification workflows.

### Key Use Cases

- ✅ **Document Digitization**: Convert physical documents into structured digital data
- ✅ **Identity Verification**: Extract and verify identity information from government documents
- ✅ **Data Extraction**: Automated extraction of key information from multiple document types
- ✅ **Workflow Integration**: Easy integration with existing systems via REST APIs
- ✅ **Quality Assurance**: Built-in verification and validation mechanisms

---

## 🌟 Features

### Core Features
- 📷 **Multi-Format OCR Processing** - Support for various document types (Passports, IDs, Driver Licenses, etc.)
- 🔍 **Advanced Field Extraction** - Intelligent extraction of key fields with high accuracy
- ✔️ **Verification Engine** - Built-in field comparison and validation
- 🔗 **MOSIP Integration** - Optional integration with MOSIP for identity verification
- 📡 **REST API** - Easy-to-use REST endpoints for document processing
- 📊 **Detailed Response** - Structured JSON responses with confidence scores
- ⚙️ **Configurable Pipeline** - Customizable processing workflow
- 🐳 **Docker Support** - Ready-to-deploy Docker containers

### Technical Features
- Fast and efficient processing using EasyOCR
- Pydantic data models for robust validation
- FastAPI framework for high-performance APIs
- Comprehensive error handling
- Extensible architecture for custom document types

---

## 🏗️ Architecture

The system follows a modular architecture with three main components:

```
┌─────────────────────────────────────────┐
│     FastAPI Application (main.py)       │
│     - REST Endpoints                    │
│     - Request/Response Handling         │
└────────────────────────────────────────┬┘
                    │
         ┌──────────┼──────────┐
         │          │          │
    ┌────▼──┐  ┌───▼────┐  ┌──▼───────┐
    │ OCR   │  │ Models │  │Verification│
    │Engine │  │(Pydantic)│ │Engine      │
    └───────┘  └────────┘  └────────────┘
```

### Components

| Component | Description |
|-----------|-------------|
| **OCR Engine** | EasyOCR-based text extraction from documents |
| **Models** | Pydantic schemas for data validation and serialization |
| **Verification Engine** | Field validation and comparison logic |
| **API Layer** | FastAPI endpoints for request handling |

---

## 📂 Project Structure

```
document-ocr-verification-system/
├── backend/                          # Backend application
│   ├── __init__.py                  # Package initialization
│   ├── main.py                      # FastAPI application entry point
│   ├── models.py                    # Pydantic data models and schemas
│   ├── ocr_engine.py                # OCR processing logic with EasyOCR
│   └── verification.py              # Document verification logic
├── Dockerfile                        # Docker configuration
├── requirements.txt                  # Python dependencies
├── .gitignore                        # Git ignore rules
└── README.md                         # This file
```

### Backend Module Details

- **main.py**: Contains FastAPI application with routes for document processing
- **models.py**: Defines Pydantic models for document data and API responses
- **ocr_engine.py**: Implements OCR extraction using EasyOCR
- **verification.py**: Implements field validation and verification logic

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- (Optional) Docker and Docker Compose for containerized deployment

### Step 1: Clone the Repository

```bash
git clone https://github.com/devejya56/document-ocr-verification-system.git
cd document-ocr-verification-system
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python -c "import fastapi; import easyocr; print('Installation successful!')"
```

---

## ⚡ Quick Start

### Running the Application

```bash
# Make sure virtual environment is activated
cd backend

# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Access the Application

- **API Server**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### First API Request

```bash
curl -X POST "http://localhost:8000/api/extract" \
  -H "Content-Type: application/json" \
  -d '{"document_path": "/path/to/document.jpg", "document_type": "passport"}'
```

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000/api
```

### Endpoints

#### 1. Extract Document Information

**Endpoint:** `POST /extract`

**Description:** Extract text and structured information from a document

**Request Body:**
```json
{
  "document_path": "string (required)",
  "document_type": "string (optional) - e.g., 'passport', 'id', 'license'"
}
```

**Response:**
```json
{
  "status": "success",
  "document_type": "passport",
  "extracted_data": {
    "name": "John Doe",
    "date_of_birth": "1990-01-15",
    "passport_number": "A12345678",
    "nationality": "US"
  },
  "confidence_score": 0.92,
  "raw_text": "full extracted text..."
}
```

#### 2. Verify Document

**Endpoint:** `POST /verify`

**Description:** Verify extracted data against provided information

**Request Body:**
```json
{
  "document_path": "string (required)",
  "provided_data": {
    "name": "string",
    "date_of_birth": "string"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "matches": {
    "name": true,
    "date_of_birth": true
  },
  "overall_match": true,
  "confidence_score": 0.95
}
```

#### 3. Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# OCR Configuration
OCR_LANGUAGES=en
OCR_GPU=False

# MOSIP Integration (Optional)
MOSIP_ENABLED=False
MOSIP_API_URL=https://your-mosip-instance.com
MOSIP_API_KEY=your_api_key_here
```

### Configuration in Code

Edit `backend/main.py` to customize:
- Supported document types
- OCR parameters
- Field extraction rules
- Verification thresholds

---

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t document-ocr-system:latest .
```

### Run Docker Container

```bash
docker run -p 8000:8000 \
  -e PYTHONUNBUFFERED=1 \
  document-ocr-system:latest
```

### Docker Compose (Recommended)

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - DEBUG=False
    volumes:
      - ./documents:/app/documents
```

Run:
```bash
docker-compose up
```

---

## 🔧 Development

### Project Dependencies

```
fastapi==0.68+          # Web framework
uvicorn==0.15+          # ASGI server
easyocr==1.6+           # OCR engine
pydantic==1.9+          # Data validation
python-multipart==0.0.5 # File upload support
```

### Adding New Document Types

1. Define schema in `models.py`:
```python
class PassportData(BaseModel):
    name: str
    passport_number: str
    # Add other fields
```

2. Add extraction logic in `ocr_engine.py`
3. Create endpoint in `main.py`

---

## 📋 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/document-ocr-verification-system.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes** and commit
   ```bash
   git commit -m 'Add amazing feature'
   ```

4. **Push to branch**
   ```bash
   git push origin feature/amazing-feature
   ```

5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions
- Write unit tests for new features
- Update documentation accordingly
- Ensure all tests pass before submitting PR

### Running Tests

```bash
pytest tests/ -v
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📧 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/devejya56/document-ocr-verification-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/devejya56/document-ocr-verification-system/discussions)
- **Author**: [Devejya Pandey](https://github.com/devejya56)

---

## 🙏 Acknowledgments

- [EasyOCR](https://github.com/JaidedAI/EasyOCR) - OCR Engine
- [FastAPI](https://fastapi.tiangolo.com/) - Web Framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data Validation

---

<div align="center">

**[⬆ back to top](#-document-ocr-verification-system)**

</div>
