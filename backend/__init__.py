"""Backend package for Document OCR & Verification System."""

__version__ = "1.0.0"
__author__ = "Devejya Pandey"

from .main import app
from .ocr_engine import OCREngine
from .verification import VerificationEngine
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
    "DocumentType",
    "OCRExtractionRequest",
    "OCRExtractionResponse",
    "VerificationRequest",
    "VerificationResponse"
]
