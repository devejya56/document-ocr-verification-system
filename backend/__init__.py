"""Backend package for Document OCR & Verification System."""

__version__ = "2.0.0"
__author__ = "Devejya Pandey"

from .main import app
from .ocr_engine import OCREngine
from .verification import VerificationEngine
from .config import settings
from .models import (
    DocumentType,
    OCRExtractionRequest,
    OCRExtractionResponse,
    VerificationRequest,
    VerificationResponse
)

__all__ = [
    "app",
    "OCREngine",
    "VerificationEngine",
    "settings",
    "DocumentType",
    "OCRExtractionRequest",
    "OCRExtractionResponse",
    "VerificationRequest",
    "VerificationResponse"
]
