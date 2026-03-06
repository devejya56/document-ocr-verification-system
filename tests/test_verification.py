"""Unit tests for the VerificationEngine."""

import pytest
from backend.verification import VerificationEngine


@pytest.fixture
def engine():
    return VerificationEngine()


class TestNormalize:
    def test_lowercase_and_strip(self, engine):
        assert engine._normalize("  Hello WORLD  ") == "hello world"
    
    def test_remove_special_chars(self, engine):
        assert engine._normalize("john-doe's") == "johndoes"
    
    def test_collapse_whitespace(self, engine):
        assert engine._normalize("a   b   c") == "a b c"


class TestSimilarity:
    def test_identical_strings(self, engine):
        assert engine._calculate_similarity("hello", "hello") == 1.0
    
    def test_completely_different(self, engine):
        score = engine._calculate_similarity("abc", "xyz")
        assert score < 0.5
    
    def test_empty_strings(self, engine):
        assert engine._calculate_similarity("", "") == 0.0
    
    def test_similar_strings(self, engine):
        score = engine._calculate_similarity("john smith", "john smth")
        assert score > 0.8


class TestNumericMatch:
    def test_exact_numeric_match(self, engine):
        assert engine._numeric_match("100", "100") is True
    
    def test_within_tolerance(self, engine):
        assert engine._numeric_match("100", "103") is True  # 3% < 5%
    
    def test_outside_tolerance(self, engine):
        assert engine._numeric_match("100", "110") is False  # 10% > 5%
    
    def test_zero_value(self, engine):
        assert engine._numeric_match("0", "0") is True
        assert engine._numeric_match("0", "1") is False


class TestVerifyFields:
    """Test the main verify_fields method."""
    
    def test_exact_match_with_dicts(self, engine):
        """Fields as dicts (from .dict() serialization)."""
        extracted = {"name": {"value": "John", "confidence": 0.9}}
        form_data = {"name": "John"}
        results = engine.verify_fields(extracted, form_data)
        assert len(results) == 1
        assert results[0].status == "MATCH"
    
    def test_exact_match_with_objects(self, engine):
        """Fields as FieldValueSchema objects (direct from OCR engine)."""
        from backend.models import FieldValueSchema
        extracted = {"name": FieldValueSchema(value="John", confidence=0.9)}
        form_data = {"name": "John"}
        results = engine.verify_fields(extracted, form_data)
        assert len(results) == 1
        assert results[0].status == "MATCH"
    
    def test_fuzzy_match(self, engine):
        extracted = {"name": {"value": "John Smith", "confidence": 0.9}}
        form_data = {"name": "John Smth"}
        results = engine.verify_fields(extracted, form_data)
        assert results[0].status == "MATCH"
        assert results[0].match_type == "fuzzy"
    
    def test_mismatch(self, engine):
        extracted = {"name": {"value": "John", "confidence": 0.9}}
        form_data = {"name": "Jane Doe"}
        results = engine.verify_fields(extracted, form_data)
        assert results[0].status == "MISMATCH"
    
    def test_missing_extracted(self, engine):
        extracted = {"name": {"value": "NOT_FOUND", "confidence": 0.0}}
        form_data = {"name": "John"}
        results = engine.verify_fields(extracted, form_data)
        assert results[0].status == "MISSING"
    
    def test_missing_submitted(self, engine):
        extracted = {"name": {"value": "John", "confidence": 0.9}}
        form_data = {}
        results = engine.verify_fields(extracted, form_data)
        assert results[0].status == "MISSING"
    
    def test_multiple_fields(self, engine):
        extracted = {
            "name": {"value": "John", "confidence": 0.9},
            "dob": {"value": "01/01/1990", "confidence": 0.8},
        }
        form_data = {"name": "John", "dob": "01/01/1990"}
        results = engine.verify_fields(extracted, form_data)
        assert len(results) == 2
        assert all(r.status == "MATCH" for r in results)
