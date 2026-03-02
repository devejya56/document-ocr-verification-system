"""Data models and schemas for OCR extraction and verification."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class DocumentType(str, Enum):
    """Supported document types."""
    ID_CARD = "id_card"
    PASSPORT = "passport"
    DRIVING_LICENSE = "driving_license"
    FORM = "form"
    CERTIFICATE = "certificate"
    BANK_STATEMENT = "bank_statement"


class FieldValueSchema(BaseModel):
    """Schema for a single extracted field."""
    value: str = Field(..., description="Extracted value from document")
    confidence: float = Field(ge=0, le=1, description="Confidence score between 0 and 1")
    bbox: Optional[List[float]] = Field(None, description="Bounding box coordinates [x1, y1, x2, y2]")
    page_index: Optional[int] = Field(None, description="Page number if multi-page document")


class OCRExtractionRequest(BaseModel):
    """Request model for OCR extraction."""
    document_type: DocumentType = Field(..., description="Type of document to extract")
    language: str = Field(default="en", description="Language code (en, hi, etc)")


class OCRExtractionResponse(BaseModel):
    """Response model for OCR extraction."""
    extraction_id: str
    document_type: DocumentType
    fields: Dict[str, FieldValueSchema]
    total_pages: int
    overall_confidence: float
    processing_time: float
    timestamp: datetime
    status: str = "success"


class VerificationRequest(BaseModel):
    """Request model for data verification."""
    extraction_id: str
    form_data: Dict[str, Any] = Field(..., description="User-submitted form data")
    language: str = Field(default="en")


class FieldVerificationResult(BaseModel):
    """Verification result for a single field."""
    field_name: str
    expected_value: str
    actual_value: Optional[str]
    status: str = Field(..., description="MATCH, MISMATCH, or MISSING")
    similarity_score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    match_type: str = Field(default="exact", description="Type of match (exact, fuzzy, numeric, etc)")


class VerificationResponse(BaseModel):
    """Response model for verification."""
    verification_id: str
    extraction_id: str
    document_type: DocumentType
    fields: List[FieldVerificationResult]
    overall_match_score: float
    overall_status: str = Field(..., description="ALL_MATCH, PARTIAL_MATCH, or MISMATCH")
    total_fields: int
    matched_fields: int
    processing_time: float
    timestamp: datetime


class ImageQualityMetrics(BaseModel):
    """Image quality assessment metrics."""
    blur_score: float = Field(ge=0, le=1, description="Image sharpness (0=blurry, 1=sharp)")
    brightness: float = Field(ge=0, le=255, description="Average brightness")
    contrast: float = Field(ge=0, le=1, description="Image contrast ratio")
    overall_quality: float = Field(ge=0, le=1, description="Overall quality score")


class ExtractionWithQuality(BaseModel):
    """OCR extraction response with quality metrics."""
    extraction: OCRExtractionResponse
    quality_metrics: ImageQualityMetrics


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    details: Optional[str] = None
    timestamp: datetime
    request_id: Optional[str] = None
