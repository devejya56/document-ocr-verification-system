"""SQLite database setup with SQLAlchemy."""

import json
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
from loguru import logger

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite specific
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ExtractionRecord(Base):
    """Database model for OCR extraction results."""
    __tablename__ = "extractions"
    
    extraction_id = Column(String, primary_key=True, index=True)
    document_type = Column(String, nullable=False)
    fields_json = Column(Text, nullable=False)  # JSON serialized fields
    total_pages = Column(Integer, default=1)
    overall_confidence = Column(Float, default=0.0)
    processing_time = Column(Float, default=0.0)
    status = Column(String, default="success")
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, nullable=True)  # For auth integration
    
    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "extraction_id": self.extraction_id,
            "document_type": self.document_type,
            "fields": json.loads(self.fields_json),
            "total_pages": self.total_pages,
            "overall_confidence": self.overall_confidence,
            "processing_time": self.processing_time,
            "status": self.status,
            "timestamp": self.created_at.isoformat() if self.created_at else None,
        }


class VerificationRecord(Base):
    """Database model for verification results."""
    __tablename__ = "verifications"
    
    verification_id = Column(String, primary_key=True, index=True)
    extraction_id = Column(String, nullable=False, index=True)
    document_type = Column(String, nullable=False)
    fields_json = Column(Text, nullable=False)  # JSON serialized field results
    overall_match_score = Column(Float, default=0.0)
    overall_status = Column(String, default="MISMATCH")
    total_fields = Column(Integer, default=0)
    matched_fields = Column(Integer, default=0)
    processing_time = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, nullable=True)
    
    def to_dict(self) -> dict:
        """Convert record to dictionary."""
        return {
            "verification_id": self.verification_id,
            "extraction_id": self.extraction_id,
            "document_type": self.document_type,
            "fields": json.loads(self.fields_json),
            "overall_match_score": self.overall_match_score,
            "overall_status": self.overall_status,
            "total_fields": self.total_fields,
            "matched_fields": self.matched_fields,
            "processing_time": self.processing_time,
            "timestamp": self.created_at.isoformat() if self.created_at else None,
        }


class UserRecord(Base):
    """Database model for user accounts."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Integer, default=1)  # SQLite doesn't have boolean
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def get_db():
    """Get database session (FastAPI dependency)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
