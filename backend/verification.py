"""Verification Engine for comparing OCR extraction with user-submitted data."""

from typing import Dict, List, Any
from difflib import SequenceMatcher
import re
from .models import FieldVerificationResult
from loguru import logger


class VerificationEngine:
    """Engine for verifying extracted data against user-submitted form data."""
    
    def __init__(self):
        """Initialize the verification engine."""
        self.fuzzy_threshold = 0.85
        logger.info("Verification Engine initialized")
    
    def verify_fields(self, extracted_fields: Dict, form_data: Dict[str, Any]) -> List[FieldVerificationResult]:
        """Verify extracted fields against form data.
        
        Args:
            extracted_fields: Dictionary of extracted field values from OCR
            form_data: Dictionary of user-submitted form data
            
        Returns:
            List of FieldVerificationResult objects
        """
        results = []
        
        # Get all field names from both sources
        all_fields = set(extracted_fields.keys()) | set(form_data.keys())
        
        for field_name in all_fields:
            extracted_value = extracted_fields.get(field_name)
            submitted_value = form_data.get(field_name)
            
            # Extract value and confidence from various formats
            # After .dict() serialization, fields come as plain dicts
            if extracted_value is None:
                ext_val = None
                ext_conf = 0.0
            elif isinstance(extracted_value, dict):
                ext_val = extracted_value.get("value")
                ext_conf = extracted_value.get("confidence", 0.5)
            elif hasattr(extracted_value, 'value'):
                ext_val = extracted_value.value
                ext_conf = extracted_value.confidence if hasattr(extracted_value, 'confidence') else 0.5
            else:
                ext_val = str(extracted_value)
                ext_conf = 0.5
            
            # Handle extraction not found
            if ext_val is None or ext_val == "NOT_FOUND":
                result = FieldVerificationResult(
                    field_name=field_name,
                    expected_value="NOT_EXTRACTED",
                    actual_value=str(submitted_value) if submitted_value else None,
                    status="MISSING",
                    similarity_score=0.0,
                    confidence=0.0,
                    match_type="missing"
                )
                results.append(result)
                continue
            
            # Get submitted value
            extracted_val = ext_val
            extracted_conf = ext_conf
            submitted_val = str(submitted_value) if submitted_value else ""
            
            if not submitted_val:
                result = FieldVerificationResult(
                    field_name=field_name,
                    expected_value=extracted_val,
                    actual_value=None,
                    status="MISSING",
                    similarity_score=0.0,
                    confidence=extracted_conf,
                    match_type="missing_submission"
                )
                results.append(result)
                continue
            
            # Determine match type and calculate similarity
            match_result = self._determine_match(
                field_name,
                extracted_val,
                submitted_val,
                extracted_conf
            )
            
            results.append(match_result)
        
        logger.info(f"Verification completed for {len(results)} fields")
        return results
    
    def _determine_match(self, field_name: str, extracted: str, submitted: str, confidence: float) -> FieldVerificationResult:
        """Determine if two field values match.
        
        Args:
            field_name: Name of the field
            extracted: Extracted value from OCR
            submitted: Submitted value from user
            confidence: OCR confidence for this field
            
        Returns:
            FieldVerificationResult with match status
        """
        # Normalize values for comparison
        extracted_norm = self._normalize(extracted)
        submitted_norm = self._normalize(submitted)
        
        # Try exact match
        if extracted_norm == submitted_norm:
            return FieldVerificationResult(
                field_name=field_name,
                expected_value=extracted,
                actual_value=submitted,
                status="MATCH",
                similarity_score=1.0,
                confidence=confidence,
                match_type="exact"
            )
        
        # Try fuzzy match
        similarity = self._calculate_similarity(extracted_norm, submitted_norm)
        
        if similarity >= self.fuzzy_threshold:
            return FieldVerificationResult(
                field_name=field_name,
                expected_value=extracted,
                actual_value=submitted,
                status="MATCH",
                similarity_score=similarity,
                confidence=confidence,
                match_type="fuzzy"
            )
        
        # Try numeric comparison for numeric fields
        if self._is_numeric(extracted_norm) and self._is_numeric(submitted_norm):
            numeric_match = self._numeric_match(extracted_norm, submitted_norm)
            if numeric_match:
                return FieldVerificationResult(
                    field_name=field_name,
                    expected_value=extracted,
                    actual_value=submitted,
                    status="MATCH",
                    similarity_score=similarity,
                    confidence=confidence,
                    match_type="numeric"
                )
        
        # Mismatch
        return FieldVerificationResult(
            field_name=field_name,
            expected_value=extracted,
            actual_value=submitted,
            status="MISMATCH",
            similarity_score=similarity,
            confidence=confidence,
            match_type="none"
        )
    
    def _normalize(self, value: str) -> str:
        """Normalize a string value for comparison.
        
        Args:
            value: Value to normalize
            
        Returns:
            Normalized string
        """
        # Convert to lowercase
        value = value.lower().strip()
        # Remove special characters and extra spaces
        value = re.sub(r'[^\w\s]', '', value)
        value = re.sub(r'\s+', ' ', value)
        return value
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            Similarity score between 0 and 1
        """
        if not str1 or not str2:
            return 0.0
        
        matcher = SequenceMatcher(None, str1, str2)
        return matcher.ratio()
    
    def _is_numeric(self, value: str) -> bool:
        """Check if a value is numeric.
        
        Args:
            value: Value to check
            
        Returns:
            True if numeric, False otherwise
        """
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    def _numeric_match(self, extracted: str, submitted: str, tolerance: float = 0.05) -> bool:
        """Check if numeric values match within tolerance.
        
        Args:
            extracted: Extracted numeric value
            submitted: Submitted numeric value
            tolerance: Tolerance percentage (default 5%)
            
        Returns:
            True if match within tolerance
        """
        try:
            ext_num = float(extracted)
            sub_num = float(submitted)
            
            if ext_num == 0:
                return ext_num == sub_num
            
            diff_percent = abs(ext_num - sub_num) / abs(ext_num)
            return diff_percent <= tolerance
        except (ValueError, ZeroDivisionError):
            return False
