"""FastAPI application for OCR extraction and verification system."""

import uuid
import json
import os
import sys
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
from loguru import logger

from .config import settings
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
from .database import init_db, get_db, ExtractionRecord, VerificationRecord
from .auth import (
    UserCreate, UserResponse, Token,
    create_user, authenticate_user, get_user_by_username,
    create_access_token, get_current_user, require_auth,
)
from .tamper_detection import TamperDetector
from .face_matching import FaceMatcher
from .document_classifier import DocumentClassifier


# --- Logging Setup ---
logger.remove()  # Remove default handler
logger.add(sys.stderr, level=settings.LOG_LEVEL, format="{time} | {level} | {message}")
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
logger.add(
    settings.LOG_FILE,
    level=settings.LOG_LEVEL,
    rotation=settings.LOG_ROTATION,
    retention=settings.LOG_RETENTION,
    format="{time} | {level} | {name}:{function}:{line} | {message}",
)

# --- Rate Limiter ---
limiter = Limiter(key_func=get_remote_address)

# --- FastAPI App ---
app = FastAPI(
    title="Document OCR & Verification System",
    description="REST API for OCR-based document extraction and data verification",
    version="2.0.0"
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
ocr_engine = OCREngine(languages=settings.ocr_languages_list)
verification_engine = VerificationEngine()

# Mount frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend-new", "dist")
# Serve static assets (Vite build)
assets_dir = os.path.join(frontend_dir, "assets")
if os.path.isdir(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
# Mount root for other files like favicon.svg, icons.svg
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


# --- Startup ---
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    logger.info("Application started successfully")


# --- Helper: validate uploaded file ---
def _validate_upload(file: UploadFile, file_bytes: bytes):
    """Validate file size and extension."""
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Empty file uploaded")
    
    if len(file_bytes) > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE_MB} MB"
        )
    
    if file.filename:
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
        if ext and ext not in settings.allowed_extensions_list:
            raise HTTPException(
                status_code=400,
                detail=f"File type '.{ext}' not allowed. Supported: {settings.allowed_extensions_list}"
            )


# ==================== PUBLIC ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint — serves frontend if available, else API info."""
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.isfile(index_path):
        from fastapi.responses import FileResponse
        return FileResponse(index_path)
    return {
        "message": "Document OCR & Verification System API",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "extract": "/api/extract",
            "verify": "/api/verify",
            "health": "/health",
            "auth_register": "/api/auth/register",
            "auth_login": "/api/auth/login",
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ==================== AUTH ENDPOINTS ====================

@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing = get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    db_user = create_user(db, user)
    return UserResponse(id=db_user.id, username=db_user.username, full_name=db_user.full_name)


@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and receive a JWT token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(data={"sub": user.username})
    return Token(access_token=token)


# ==================== PROTECTED API ENDPOINTS ====================

@app.post("/api/extract", response_model=OCRExtractionResponse)
@limiter.limit(settings.RATE_LIMIT)
async def extract_document(
    request: Request,
    file: UploadFile = File(...),
    document_type: str = "form",
    db: Session = Depends(get_db),
    # Temporarily disabled auth for UI testing
    # current_user=Depends(get_current_user),
):
    """Extract text and fields from uploaded document.
    
    Args:
        file: Uploaded document file (image or PDF)
        document_type: Type of document (id_card, passport, form, etc)
        
    Returns:
        OCRExtractionResponse with extracted fields
    """
    start_time = time.time()
    extraction_id = str(uuid.uuid4())
    
    current_user = None # Mock user for record traceability
    
    try:
        # Validate document type
        try:
            doc_type = DocumentType(document_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid document type. Supported: {[dt.value for dt in DocumentType]}"
            )
        
        # Read and validate file
        file_bytes = await file.read()
        _validate_upload(file, file_bytes)
        
        # Perform OCR extraction
        extraction_result = ocr_engine.extract_text_from_image(file_bytes)
        
        # Handle Auto-Classification
        if doc_type == DocumentType.AUTO:
            full_text = " ".join([b["text"] for b in extraction_result["text_blocks"]])
            classification = doc_classifier.classify(full_text, extraction_result["text_blocks"])
            # Update doc_type to predicted type
            try:
                doc_type = DocumentType(classification["predicted_type"])
                logger.info(f"Auto-classification resolved '{document_type}' to '{doc_type}'")
            except ValueError:
                # Default to id_card if unknown type predicted
                doc_type = DocumentType.ID_CARD
                logger.warning(f"Classification returned unsupported type '{classification['predicted_type']}'. Defaulting to 'id_card'.")
        
        # Extract fields based on document type (use resolved doc_type)
        fields_dict = ocr_engine.extract_fields(
            extraction_result["text_blocks"],
            doc_type.value
        )
        
        processing_time = time.time() - start_time
        total_pages = extraction_result.get("total_pages", 1)
        
        # Prepare response
        response = OCRExtractionResponse(
            extraction_id=extraction_id,
            document_type=doc_type,
            fields=fields_dict,
            total_pages=total_pages,
            overall_confidence=extraction_result["overall_confidence"],
            processing_time=processing_time,
            timestamp=datetime.utcnow(),
            status="success"
        )
        
        # Store in database
        record = ExtractionRecord(
            extraction_id=extraction_id,
            document_type=document_type,
            fields_json=json.dumps({k: v.dict() for k, v in fields_dict.items()}),
            total_pages=total_pages,
            overall_confidence=extraction_result["overall_confidence"],
            processing_time=processing_time,
            user_id=current_user.id if current_user else None,
        )
        db.add(record)
        db.commit()
        
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
@limiter.limit(settings.RATE_LIMIT)
async def verify_data(
    request: Request,
    body: VerificationRequest,
    db: Session = Depends(get_db),
    # Temporarily disabled auth for UI testing
    # current_user=Depends(get_current_user),
):
    """Verify user-submitted data against OCR extraction.
    
    Args:
        body: VerificationRequest with form data and extraction ID
        
    Returns:
        VerificationResponse with field-by-field comparison
    """
    start_time = time.time()
    verification_id = str(uuid.uuid4())
    current_user = None
    
    try:
        # Retrieve extraction from DB
        extraction_record = db.query(ExtractionRecord).filter(
            ExtractionRecord.extraction_id == body.extraction_id
        ).first()
        
        if not extraction_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Extraction not found: {body.extraction_id}"
            )
        
        extracted_fields = json.loads(extraction_record.fields_json)
        
        # Perform verification
        field_results = verification_engine.verify_fields(
            extracted_fields,
            body.form_data
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
            extraction_id=body.extraction_id,
            document_type=DocumentType(extraction_record.document_type),
            fields=field_results,
            overall_match_score=overall_match_score,
            overall_status=overall_status,
            total_fields=len(field_results),
            matched_fields=matched_count,
            processing_time=processing_time,
            timestamp=datetime.utcnow()
        )
        
        # Store in database
        record = VerificationRecord(
            verification_id=verification_id,
            extraction_id=body.extraction_id,
            document_type=extraction_record.document_type,
            fields_json=json.dumps([f.dict() for f in field_results]),
            overall_match_score=overall_match_score,
            overall_status=overall_status,
            total_fields=len(field_results),
            matched_fields=matched_count,
            processing_time=processing_time,
            user_id=current_user.id if current_user else None,
        )
        db.add(record)
        db.commit()
        
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
async def get_extraction(extraction_id: str, db: Session = Depends(get_db)):
    """Retrieve a previous extraction by ID."""
    record = db.query(ExtractionRecord).filter(
        ExtractionRecord.extraction_id == extraction_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Extraction not found: {extraction_id}")
    return record.to_dict()


@app.get("/api/verification/{verification_id}")
async def get_verification(verification_id: str, db: Session = Depends(get_db)):
    """Retrieve a previous verification by ID."""
    record = db.query(VerificationRecord).filter(
        VerificationRecord.verification_id == verification_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Verification not found: {verification_id}")
    return record.to_dict()


# --- Advanced Feature Instances ---
tamper_detector = TamperDetector()
face_matcher = FaceMatcher()
doc_classifier = DocumentClassifier()


# ==================== TAMPER DETECTION ====================

@app.post("/api/tamper-check")
@limiter.limit(settings.RATE_LIMIT)
async def check_tamper(
    request: Request,
    file: UploadFile = File(...),
):
    """Analyze a document image for signs of tampering."""
    contents = await file.read()
    if len(contents) > settings.max_file_size_bytes:
        raise HTTPException(status_code=413, detail="File too large")
    
    start = time.time()
    try:
        result = tamper_detector.analyze(contents)
        result["processing_time"] = round(time.time() - start, 3)
        result["filename"] = file.filename
        logger.info(f"Tamper check: {result['verdict']} (score={result['overall_trust_score']})")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tamper analysis failed: {str(e)}")


# ==================== FACE MATCHING ====================

@app.post("/api/face-detect")
@limiter.limit(settings.RATE_LIMIT)
async def detect_faces(
    request: Request,
    file: UploadFile = File(...),
):
    """Detect faces in a document image."""
    contents = await file.read()
    if len(contents) > settings.max_file_size_bytes:
        raise HTTPException(status_code=413, detail="File too large")
    
    try:
        result = face_matcher.detect_faces(contents)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Face detection failed: {str(e)}")


@app.post("/api/face-match")
@limiter.limit(settings.RATE_LIMIT)
async def match_faces(
    request: Request,
    document: UploadFile = File(...),
    selfie: UploadFile = File(...),
):
    """Compare face on document against selfie photo."""
    doc_bytes = await document.read()
    selfie_bytes = await selfie.read()
    
    if len(doc_bytes) > settings.max_file_size_bytes or len(selfie_bytes) > settings.max_file_size_bytes:
        raise HTTPException(status_code=413, detail="File too large")
    
    start = time.time()
    try:
        result = face_matcher.match_faces(doc_bytes, selfie_bytes)
        result["processing_time"] = round(time.time() - start, 3)
        logger.info(f"Face match: {result['verdict']} (score={result['match_score']})")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Face matching failed: {str(e)}")


# ==================== AUTO CLASSIFICATION ====================

@app.post("/api/classify")
@limiter.limit(settings.RATE_LIMIT)
async def classify_document(
    request: Request,
    file: UploadFile = File(...),
):
    """Auto-detect document type from image."""
    contents = await file.read()
    if len(contents) > settings.max_file_size_bytes:
        raise HTTPException(status_code=413, detail="File too large")
    
    start = time.time()
    try:
        # Run OCR first to get text
        ocr_result = ocr_engine.extract_text_from_image(contents)
        full_text = " ".join([b["text"] for b in ocr_result["text_blocks"]])
        
        # Classify
        classification = doc_classifier.classify(full_text, ocr_result["text_blocks"])
        classification["processing_time"] = round(time.time() - start, 3)
        
        logger.info(f"Classification: {classification['predicted_type']} (conf={classification['confidence']})")
        return classification
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
