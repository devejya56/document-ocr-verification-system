"""FastAPI application for OCR extraction and verification system."""

import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from loguru import logger

from .models import (
    OCRExtractionRequest,
    OCRExtractionResponse,
    FieldValueSchema,
    VerificationRequest,
    VerificationResponse,
    FieldVerificationResult,
    DocumentType,
    ErrorResponse
)
from .ocr_engine import OCREngine
from .verification import VerificationEngine

# Initialize FastAPI app
app = FastAPI(
    title="Document OCR & Verification System",
    description="REST API for OCR-based document extraction and data verification",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
ocr_engine = OCREngine(languages=["en", "hi"])
verification_engine = VerificationEngine()

# In-memory storage for extractions and verifications
extractions_store = {}
verifications_store = {}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Document OCR & Verification System API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "extract": "/api/extract",
            "verify": "/api/verify",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/extract", response_model=OCRExtractionResponse)
async def extract_document(file: UploadFile = File(...), document_type: str = "form"):
    """Extract text and fields from uploaded document.
    
    Args:
        file: Uploaded document file (image or PDF)
        document_type: Type of document (id_card, passport, form, etc)
        
    Returns:
        OCRExtractionResponse with extracted fields
    """
    start_time = time.time()
    extraction_id = str(uuid.uuid4())
    
    try:
        # Validate document type
        try:
            doc_type = DocumentType(document_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document type. Supported: {[dt.value for dt in DocumentType]}"
            )
        
        # Read file
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file uploaded"
            )
        
        # Perform OCR extraction
        extraction_result = ocr_engine.extract_text_from_image(file_bytes)
        
        # Extract fields based on document type
        fields_dict = ocr_engine.extract_fields(
            extraction_result["text_blocks"],
            document_type
        )
        
        processing_time = time.time() - start_time
        
        # Prepare response
        response = OCRExtractionResponse(
            extraction_id=extraction_id,
            document_type=doc_type,
            fields=fields_dict,
            total_pages=1,
            overall_confidence=extraction_result["overall_confidence"],
            processing_time=processing_time,
            timestamp=datetime.utcnow(),
            status="success"
        )
        
        # Store extraction for later verification
        extractions_store[extraction_id] = response.dict()
        
        logger.info(f"Extraction successful: {extraction_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in extraction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}"
        )


@app.post("/api/verify", response_model=VerificationResponse)
async def verify_data(request: VerificationRequest):
    """Verify user-submitted data against OCR extraction.
    
    Args:
        request: VerificationRequest with form data and extraction ID
        
    Returns:
        VerificationResponse with field-by-field comparison
    """
    start_time = time.time()
    verification_id = str(uuid.uuid4())
    
    try:
        # Retrieve extraction
        if request.extraction_id not in extractions_store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Extraction not found: {request.extraction_id}"
            )
        
        extraction = extractions_store[request.extraction_id]
        
        # Perform verification
        field_results = verification_engine.verify_fields(
            extraction["fields"],
            request.form_data
        )
        
        # Calculate statistics
        matched_count = sum(1 for f in field_results if f.status == "MATCH")
        processing_time = time.time() - start_time
        overall_match_score = matched_count / len(field_results) if field_results else 0.0
        
        # Determine overall status
        if overall_match_score == 1.0:
            overall_status = "ALL_MATCH"
        elif overall_match_score > 0.5:
            overall_status = "PARTIAL_MATCH"
        else:
            overall_status = "MISMATCH"
        
        response = VerificationResponse(
            verification_id=verification_id,
            extraction_id=request.extraction_id,
            document_type=DocumentType(extraction["document_type"]),
            fields=field_results,
            overall_match_score=overall_match_score,
            overall_status=overall_status,
            total_fields=len(field_results),
            matched_fields=matched_count,
            processing_time=processing_time,
            timestamp=datetime.utcnow()
        )
        
        # Store verification
        verifications_store[verification_id] = response.dict()
        
        logger.info(f"Verification successful: {verification_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification failed: {str(e)}"
        )


@app.get("/api/extraction/{extraction_id}")
async def get_extraction(extraction_id: str):
    """Retrieve a previous extraction by ID.
    
    Args:
        extraction_id: ID of the extraction to retrieve
        
    Returns:
        Stored extraction data
    """
    if extraction_id not in extractions_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Extraction not found: {extraction_id}"
        )
    return extractions_store[extraction_id]


@app.get("/api/verification/{verification_id}")
async def get_verification(verification_id: str):
    """Retrieve a previous verification by ID.
    
    Args:
        verification_id: ID of the verification to retrieve
        
    Returns:
        Stored verification data
    """
    if verification_id not in verifications_store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verification not found: {verification_id}"
        )
    return verifications_store[verification_id]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
