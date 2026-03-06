"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""
    
    # Database
    DATABASE_URL: str = "sqlite:///./ocr_system.db"
    
    # Authentication
    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # OCR
    OCR_LANGUAGES: str = "en,hi"
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 20
    ALLOWED_EXTENSIONS: str = "png,jpg,jpeg,bmp,tiff,tif,pdf"
    
    # Rate Limiting
    RATE_LIMIT: str = "10/minute"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/ocr_system.log"
    LOG_ROTATION: str = "10 MB"
    LOG_RETENTION: str = "7 days"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    @property
    def ocr_languages_list(self) -> List[str]:
        return [lang.strip() for lang in self.OCR_LANGUAGES.split(",")]
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
