"""OCR Engine for document text extraction using transformer models."""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
from PIL import Image
import io
from pathlib import Path
from datetime import datetime
import uuid
import easyocr
from .models import FieldValueSchema, ImageQualityMetrics
from loguru import logger


class OCREngine:
    """Main OCR engine using EasyOCR for text extraction."""
    
    def __init__(self, languages: List[str] = ["en"]):
        """Initialize OCR engine with specified languages.
        
        Args:
            languages: List of language codes to load (e.g., ['en', 'hi'])
        """
        self.languages = languages
        self.reader = easyocr.Reader(languages, gpu=False)
        logger.info(f"OCR Engine initialized with languages: {languages}")
    
    def extract_text_from_image(self, image_path_or_bytes) -> Dict:
        """Extract text from an image using OCR.
        
        Args:
            image_path_or_bytes: Path to image or image bytes
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            if isinstance(image_path_or_bytes, bytes):
                image = Image.open(io.BytesIO(image_path_or_bytes))
                image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                image_cv = cv2.imread(str(image_path_or_bytes))
                if image_cv is None:
                    raise ValueError(f"Could not read image: {image_path_or_bytes}")
            
            results = self.reader.readtext(image_cv)
            extracted_data = self._process_ocr_results(results, image_cv)
            
            return extracted_data
        except Exception as e:
            logger.error(f"Error in OCR extraction: {str(e)}")
            raise
    
    def _process_ocr_results(self, results: List, image) -> Dict:
        """Process raw OCR results into structured format.
        
        Args:
            results: List of OCR detection results
            image: Original image
            
        Returns:
            Processed extraction dictionary
        """
        text_data = []
        
        for result in results:
            bbox = result[0]
            text = result[1]
            confidence = result[2]
            
            text_data.append({
                "text": text,
                "confidence": float(confidence),
                "bbox": [[float(p[0]), float(p[1])] for p in bbox]
            })
        
        quality_metrics = self._calculate_image_quality(image)
        overall_confidence = np.mean([t["confidence"] for t in text_data]) if text_data else 0.0
        
        return {
            "extraction_id": str(uuid.uuid4()),
            "text_blocks": text_data,
            "overall_confidence": float(overall_confidence),
            "quality_metrics": quality_metrics,
            "timestamp": datetime.utcnow().isoformat(),
            "total_blocks": len(text_data)
        }
    
    def _calculate_image_quality(self, image) -> dict:
        """Calculate image quality metrics.
        
        Args:
            image: OpenCV image
            
        Returns:
            Dictionary with quality metrics
        """
        # Blur detection using Laplacian variance
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        blur_score = min(laplacian.var() / 500.0, 1.0)  # Normalize
        
        # Brightness
        brightness = np.mean(gray)
        
        # Contrast
        contrast = np.std(gray) / 128.0
        contrast = min(contrast, 1.0)
        
        # Overall quality
        overall_quality = (blur_score * 0.5 + contrast * 0.5)
        
        return {
            "blur_score": float(blur_score),
            "brightness": float(brightness),
            "contrast": float(contrast),
            "overall_quality": float(overall_quality)
        }
    
    def extract_fields(self, text_blocks: List[Dict], document_type: str) -> Dict[str, FieldValueSchema]:
        """Extract structured fields from text blocks based on document type.
        
        Args:
            text_blocks: List of OCR text blocks
            document_type: Type of document (id_card, passport, etc)
            
        Returns:
            Dictionary of extracted fields
        """
        # Combine all text
        full_text = " ".join([block["text"] for block in text_blocks])
        
        # Field extraction based on document type
        fields = self._parse_document_fields(full_text, document_type, text_blocks)
        
        return fields
    
    def _parse_document_fields(self, text: str, doc_type: str, text_blocks: List) -> Dict:
        """Parse document-specific fields from extracted text.
        
        Args:
            text: Combined extracted text
            doc_type: Document type
            text_blocks: Original text blocks with positions
            
        Returns:
            Dictionary of parsed fields
        """
        fields = {}
        text_lower = text.lower()
        
        # ID Card fields
        if doc_type == "id_card":
            fields["name"] = self._extract_field(text, text_blocks, "name")
            fields["id_number"] = self._extract_field(text, text_blocks, "id")
            fields["dob"] = self._extract_field(text, text_blocks, "dob")
            fields["address"] = self._extract_field(text, text_blocks, "address")
        
        # Passport fields
        elif doc_type == "passport":
            fields["surname"] = self._extract_field(text, text_blocks, "surname")
            fields["given_names"] = self._extract_field(text, text_blocks, "given")
            fields["passport_number"] = self._extract_field(text, text_blocks, "passport")
            fields["dob"] = self._extract_field(text, text_blocks, "dob")
        
        return fields
    
    def _extract_field(self, text: str, text_blocks: List, field_type: str) -> FieldValueSchema:
        """Extract a specific field from text.
        
        Args:
            text: Full text
            text_blocks: Text blocks with confidence
            field_type: Type of field to extract
            
        Returns:
            FieldValueSchema with extracted value
        """
        # Simple heuristic extraction
        value = ""
        confidence = 0.0
        
        # This is a placeholder - actual implementation would use regex/NLP
        if field_type in text.lower():
            value = text.split(field_type)[-1].split()
            if value:
                value = value[0][:20]  # Limit length
                confidence = 0.85
        
        return FieldValueSchema(
            value=value or "NOT_FOUND",
            confidence=confidence
        )
