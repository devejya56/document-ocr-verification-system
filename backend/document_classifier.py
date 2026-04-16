"""Auto document type classification from OCR text.

Detects document type based on keyword matching in extracted text.
Supports: Aadhaar, PAN, Passport, Driving License, Voter ID,
          Bank Statement, Certificate, and generic Form.
"""

import re
from typing import Dict, List, Tuple
from loguru import logger


# Document type keywords with weights
DOCUMENT_SIGNATURES = {
    "aadhaar": {
        "keywords": [
            ("aadhaar", 12), ("आधार", 12), ("unique identification", 10),
            ("uidai", 10), ("vid", 5), ("enrollment", 6),
            ("government of india", 5), ("भारत सरकार", 10),
        ],
        "patterns": [
            (r'\d{4}\s+\d{4}\s+\d{4}', 12),   # Aadhaar format
        ],
    },
    "pan_card": {
        "keywords": [
            ("pan", 10), ("permanent account number", 12), ("income tax", 10),
            ("department", 5), ("govt. of india", 5), ("income-tax", 10),
        ],
        "patterns": [
            (r'[A-Z]{5}\d{4}[A-Z]', 12),        # PAN format
        ],
    },
    "voter_id": {
        "keywords": [
            ("voter", 12), ("election commission", 10), ("electors", 10),
            ("identity card", 8), ("epic", 8), ("electoral", 10),
        ],
        "patterns": [
            (r'[A-Z]{3}\d{7}', 10),            # EPIC number format
        ],
    },
    "id_card": {
        "keywords": [
            ("identity card", 5), ("photo id", 4), ("national id", 5),
        ],
        "patterns": [],
    },
    "passport": {
        "keywords": [
            ("passport", 10), ("republic of india", 6), ("nationality", 5),
            ("surname", 5), ("given name", 5), ("place of birth", 6),
            ("date of issue", 4), ("date of expiry", 4), ("type p", 7),
            ("machine readable", 5), ("mrz", 6),
        ],
        "patterns": [
            (r'[A-Z]\d{7,8}', 8),              # Passport number
        ],
    },
    "driving_license": {
        "keywords": [
            ("driving", 8), ("licence", 9), ("license", 9),
            ("transport", 6), ("motor vehicle", 8), ("rto", 7),
            ("class of vehicle", 7), ("non-transport", 6), ("mcwg", 5),
            ("lmv", 5), ("validity", 4),
        ],
        "patterns": [
            (r'[A-Z]{2}\d{2}\s?\d{4,11}', 10),  # License number
        ],
    },
    "bank_statement": {
        "keywords": [
            ("bank", 10), ("statement", 8), ("account", 6),
            ("balance", 8), ("transaction", 8), ("debit", 6), ("credit", 6),
            ("ifsc", 10), ("branch", 5), ("savings", 6), ("current account", 8),
            ("opening balance", 8), ("closing balance", 8), ("neft", 6), ("upi", 6),
        ],
        "patterns": [
            (r'\bIFSC\s*[:\-]?\s*[A-Z]{4}0\w{6}\b', 12),  # IFSC code
        ],
    },
    "certificate": {
        "keywords": [
            ("certificate", 8), ("certify", 7), ("hereby", 5),
            ("awarded", 6), ("conferred", 6), ("qualification", 5),
            ("degree", 6), ("diploma", 6), ("board of", 5),
            ("university", 6), ("institution", 4), ("registrar", 5),
            ("marks", 4), ("grade", 4), ("examination", 5),
        ],
        "patterns": [],
    },
    "form": {
        "keywords": [
            ("form", 5), ("application", 5), ("fill", 3),
            ("signature", 4), ("declaration", 5), ("submit", 3),
            ("date", 2), ("name", 2), ("address", 2),
        ],
        "patterns": [],
    },
}


class DocumentClassifier:
    """Automatically classifies document type from OCR-extracted text."""
    
    def __init__(self):
        logger.info("DocumentClassifier initialized with Indian Document support")
    
    def classify(self, text: str, text_blocks: List[Dict] = None) -> Dict:
        """Classify a document based on its text content.
        
        Args:
            text: Combined OCR text
            text_blocks: Optional list of OCR text blocks
            
        Returns:
            Classification result with predicted type and confidence
        """
        text_lower = text.lower()
        scores = {}
        match_details = {}
        
        for doc_type, signatures in DOCUMENT_SIGNATURES.items():
            type_score = 0
            matched = []
            
            # Keyword matching
            for keyword, weight in signatures["keywords"]:
                if keyword.lower() in text_lower:
                    type_score += weight
                    matched.append(keyword)
            
            # Pattern matching
            for pattern, weight in signatures.get("patterns", []):
                if re.search(pattern, text, re.IGNORECASE):
                    type_score += weight
                    matched.append(f"pattern:{pattern[:20]}")
            
            scores[doc_type] = type_score
            match_details[doc_type] = matched
        
        # Determine best match
        if not scores or max(scores.values()) == 0:
            return {
                "predicted_type": "form",
                "confidence": 0.3,
                "all_scores": {k: 0.0 for k in scores},
                "matched_keywords": {},
                "detail": "No strong document type indicators found. Defaulting to 'form'.",
            }
        
        # Normalize scores
        max_score = max(scores.values())
        normalized = {k: round(v / max_score, 3) if max_score > 0 else 0 for k, v in scores.items()}
        
        # Sort by score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_type = ranked[0][0]
        best_score = ranked[0][1]
        
        # Confidence: based on score magnitude and margin over second-best
        second_score = ranked[1][1] if len(ranked) > 1 else 0
        margin = (best_score - second_score) / max(best_score, 1)
        confidence = min(0.98, max(0.3, 0.6 + margin * 0.3 + min(best_score, 40) / 80))
        
        logger.info(f"Document classified as '{best_type}' (confidence={confidence:.2f}, score={best_score})")
        
        return {
            "predicted_type": best_type,
            "confidence": round(confidence, 3),
            "all_scores": normalized,
            "matched_keywords": {k: v for k, v in match_details.items() if v},
            "detail": f"Classified as '{best_type}' based on {len(match_details.get(best_type, []))} indicators.",
        }
