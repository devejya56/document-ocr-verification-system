"""OCR Engine for document text extraction with robust field parsing and PDF support."""

import cv2
import numpy as np
import re
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
        """Extract text from an image or PDF using OCR.
        
        Args:
            image_path_or_bytes: Path to image/PDF or file bytes
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            if isinstance(image_path_or_bytes, bytes):
                # Check if it's a PDF
                if image_path_or_bytes[:4] == b'%PDF':
                    return self._extract_from_pdf(image_path_or_bytes)
                
                image = Image.open(io.BytesIO(image_path_or_bytes))
                image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                file_path = str(image_path_or_bytes)
                if file_path.lower().endswith('.pdf'):
                    with open(file_path, 'rb') as f:
                        return self._extract_from_pdf(f.read())
                
                image_cv = cv2.imread(file_path)
                if image_cv is None:
                    raise ValueError(f"Could not read image: {image_path_or_bytes}")
            
            # Preprocess image for better OCR
            image_cv = self._preprocess_image(image_cv)
            
            # Encode preprocessed image to bytes to bypass numpy/torch identity conflict
            # and avoid rejection of PIL images by certain EasyOCR versions.
            success, buffer = cv2.imencode('.png', image_cv)
            if not success:
                raise ValueError("Could not encode preprocessed image for OCR")
            
            results = self.reader.readtext(buffer.tobytes())
            extracted_data = self._process_ocr_results(results, image_cv)
            
            return extracted_data
        except Exception as e:
            import traceback
            logger.error(f"Error in OCR extraction: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    def _preprocess_image(self, image) -> np.ndarray:
        """Preprocess image for better OCR accuracy.
        
        Args:
            image: OpenCV image
            
        Returns:
            Preprocessed image
        """
        # Resize if too small (helps OCR accuracy)
        h, w = image.shape[:2]
        if max(h, w) < 1000:
            scale = 1500 / max(h, w)
            image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # Denoise
        image = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        
        return image
    
    def _extract_from_pdf(self, pdf_bytes: bytes) -> Dict:
        """Extract text from PDF by converting pages to images."""
        try:
            from pdf2image import convert_from_bytes
            
            images = convert_from_bytes(pdf_bytes, dpi=300)
            logger.info(f"PDF has {len(images)} page(s)")
            
            all_text_data = []
            all_quality_metrics = []
            
            for page_idx, pil_image in enumerate(images):
                # Use encoded bytes to avoid context-clash errors between libraries
                success, buffer = cv2.imencode('.png', image_cv)
                if not success:
                    continue # Skip failed page
                results = self.reader.readtext(buffer.tobytes())
                
                for result in results:
                    bbox, text, confidence = result[0], result[1], result[2]
                    all_text_data.append({
                        "text": text,
                        "confidence": float(confidence),
                        "bbox": [[float(p[0]), float(p[1])] for p in bbox],
                        "page_index": page_idx,
                    })
                
                all_quality_metrics.append(self._calculate_image_quality(image_cv))
            
            overall_confidence = np.mean([t["confidence"] for t in all_text_data]) if all_text_data else 0.0
            avg_quality = {}
            if all_quality_metrics:
                for key in all_quality_metrics[0]:
                    avg_quality[key] = float(np.mean([m[key] for m in all_quality_metrics]))
            
            return {
                "extraction_id": str(uuid.uuid4()),
                "text_blocks": all_text_data,
                "overall_confidence": float(overall_confidence),
                "quality_metrics": avg_quality,
                "timestamp": datetime.utcnow().isoformat(),
                "total_blocks": len(all_text_data),
                "total_pages": len(images),
            }
        except ImportError:
            raise ValueError("PDF support requires pdf2image and poppler.")
        except Exception as e:
            logger.error(f"Error extracting from PDF: {str(e)}")
            raise
    
    def _process_ocr_results(self, results: List, image) -> Dict:
        """Process raw OCR results into structured format."""
        text_data = []
        
        for result in results:
            bbox, text, confidence = result[0], result[1], result[2]
            text_data.append({
                "text": text,
                "confidence": float(confidence),
                "bbox": [[float(p[0]), float(p[1])] for p in bbox]
            })
        
        quality_metrics = self._calculate_image_quality(image)
        overall_confidence = np.mean([t["confidence"] for t in text_data]) if text_data else 0.0
        
        # Log all detected text for debugging
        all_text = " | ".join([t["text"] for t in text_data])
        logger.info(f"OCR detected {len(text_data)} blocks: {all_text[:500]}")
        
        return {
            "extraction_id": str(uuid.uuid4()),
            "text_blocks": text_data,
            "overall_confidence": float(overall_confidence),
            "quality_metrics": quality_metrics,
            "timestamp": datetime.utcnow().isoformat(),
            "total_blocks": len(text_data),
            "total_pages": 1,
        }
    
    def _calculate_image_quality(self, image) -> dict:
        """Calculate image quality metrics."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        blur_score = min(laplacian.var() / 500.0, 1.0)
        brightness = np.mean(gray)
        contrast = min(np.std(gray) / 128.0, 1.0)
        overall_quality = (blur_score * 0.5 + contrast * 0.5)
        
        return {
            "blur_score": float(blur_score),
            "brightness": float(brightness),
            "contrast": float(contrast),
            "overall_quality": float(overall_quality)
        }
    
    def extract_fields(self, text_blocks: List[Dict], document_type: str) -> Dict[str, FieldValueSchema]:
        """Extract structured fields from text blocks based on document type."""
        full_text = " ".join([block["text"] for block in text_blocks])
        logger.info(f"Extracting fields for doc_type={document_type}, full text: {full_text[:300]}")
        
        fields = self._parse_document_fields(full_text, document_type, text_blocks)
        
        # Log extracted fields
        for k, v in fields.items():
            logger.info(f"  Field '{k}': value='{v.value}', confidence={v.confidence}")
        
        return fields
    
    def _parse_document_fields(self, text: str, doc_type: str, text_blocks: List) -> Dict:
        """Parse document-specific fields from extracted text."""
        fields = {}
        
        if doc_type == "id_card" or doc_type == "aadhaar" or doc_type == "pan_card" or doc_type == "voter_id":
            fields = self._extract_id_card_fields(text, text_blocks)
        elif doc_type == "passport":
            fields = self._extract_passport_fields(text, text_blocks)
        elif doc_type == "driving_license":
            fields = self._extract_license_fields(text, text_blocks)
        elif doc_type == "form":
            fields = self._extract_form_fields(text, text_blocks)
        elif doc_type == "certificate":
            fields = self._extract_certificate_fields(text, text_blocks)
        elif doc_type == "bank_statement":
            fields = self._extract_bank_fields(text, text_blocks)
        
        return fields
    
    # ==================== ID CARD (Aadhaar, Voter ID, etc.) ====================
    
    def _extract_id_card_fields(self, text: str, text_blocks: List) -> Dict:
        """Extract fields from ID cards (Aadhaar, Voter ID, PAN, etc.)."""
        fields = {}
        
        # --- Aadhaar Number (12 digits, often as XXXX XXXX XXXX) ---
        aadhaar = self._find_aadhaar_number(text, text_blocks)
        fields["id_number"] = aadhaar
        
        # --- Name ---
        fields["name"] = self._find_name_in_id(text, text_blocks)
        
        # --- Date of Birth ---
        fields["dob"] = self._find_date(text, text_blocks)
        
        # --- Gender ---
        fields["gender"] = self._find_gender(text, text_blocks)
        
        # --- Address (if present, e.g. on Aadhaar back) ---
        fields["address"] = self._find_address(text, text_blocks)
        
        return fields
    
    def _find_aadhaar_number(self, text: str, text_blocks: List) -> FieldValueSchema:
        """Find 12-digit Aadhaar number in various formats."""
        # Pattern: 4 digits space 4 digits space 4 digits
        patterns = [
            r'(\d{4}\s+\d{4}\s+\d{4})',          # 1234 5678 9012
            r'(\d{4}[-]\d{4}[-]\d{4})',            # 1234-5678-9012
            r'(\d{12})',                            # 123456789012
            r'(\d{4}\s*\d{4}\s*\d{4})',            # flexible spacing
        ]
        
        # Search in individual text blocks (more accurate)
        for block in text_blocks:
            block_text = block["text"].strip()
            for pattern in patterns:
                match = re.search(pattern, block_text)
                if match:
                    value = match.group(1).strip()
                    # Verify it's 12 digits
                    digits_only = re.sub(r'\D', '', value)
                    if len(digits_only) == 12:
                        confidence = block.get("confidence", 0.8)
                        logger.info(f"Found Aadhaar number: {value}")
                        return FieldValueSchema(value=value, confidence=float(confidence))
        
        # Also search in full combined text
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = match.group(1).strip()
                digits_only = re.sub(r'\D', '', value)
                if len(digits_only) == 12:
                    return FieldValueSchema(value=value, confidence=0.7)
        
        # Try to find any long number sequence (PAN, Voter ID, etc.)
        long_nums = re.findall(r'[A-Z]{0,5}\d{5,12}[A-Z]?\d{0,2}', text)
        if long_nums:
            # Pick the longest one
            best = max(long_nums, key=len)
            return FieldValueSchema(value=best, confidence=0.5)
        
        return FieldValueSchema(value="NOT_FOUND", confidence=0.0)
    
    def _find_name_in_id(self, text: str, text_blocks: List) -> FieldValueSchema:
        """Find name from Indian ID card. Handles English and Hindi labels."""
        # Common labels before a name on Indian IDs
        name_labels = [
            r'(?:name|naam)\s*[:\-]?\s*([A-Za-z][A-Za-z\s\.]{2,50})',
            r'(?:नाम|name)\s*[:\-]?\s*(.{2,50})',
        ]
        
        # Try label-based extraction
        for pattern in name_labels:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean up: remove trailing numbers or junk
                name = re.sub(r'\d+.*$', '', name).strip()
                name = re.sub(r'\s{2,}', ' ', name).strip()
                if len(name) >= 2 and not name.isdigit():
                    return FieldValueSchema(value=name, confidence=0.8)
        
        # Strategy: On Aadhaar, the name is typically a text block containing
        # only English alphabetic words, positioned above the Aadhaar number.
        # Look for blocks that look like a person's name.
        name_candidates = []
        for idx, block in enumerate(text_blocks):
            t = block["text"].strip()
            # A name block: mostly alphabet, 2+ words, 3-50 chars
            if re.match(r'^[A-Za-z][A-Za-z\s\.]{2,50}$', t):
                words = t.split()
                if len(words) >= 2 and all(len(w) >= 1 for w in words):
                    # Skip common non-name phrases
                    lower = t.lower()
                    skip_phrases = [
                        'government', 'india', 'aadhaar', 'unique', 'identification',
                        'authority', 'male', 'female', 'date', 'birth', 'address',
                        'year', 'download', 'enrol', 'help', 'issue', 'print',
                        'vid', 'dob', 'valid', 'generated',
                    ]
                    if not any(phrase in lower for phrase in skip_phrases):
                        conf = block.get("confidence", 0.7)
                        name_candidates.append((t, float(conf), idx))
        
        if name_candidates:
            # Prefer the first candidate (usually highest on the card)
            best = name_candidates[0]
            logger.info(f"Found name candidate: '{best[0]}' (conf={best[1]})")
            return FieldValueSchema(value=best[0], confidence=best[1])
        
        # Last resort: find adjacent block after "Name" label
        result = self._find_text_near_label(text_blocks, "name")
        if result:
            return FieldValueSchema(value=result[0], confidence=result[1])
        
        return FieldValueSchema(value="NOT_FOUND", confidence=0.0)
    
    def _find_date(self, text: str, text_blocks: List) -> FieldValueSchema:
        """Find date of birth or any date in the text."""
        date_patterns = [
            r'(?:DOB|D\.O\.B|dob|Date of Birth|जन्म\s*तिथि|Birth)\s*[:\-]?\s*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4})',
            r'(?:DOB|D\.O\.B|dob|Date of Birth|जन्म\s*तिथि|Birth)\s*[:\-]?\s*(\d{1,2}\s+\d{1,2}\s+\d{2,4})',
            r'(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{4})',
            r'(\d{4}[/\-.]\d{1,2}[/\-.]\d{1,2})',
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})',
            r'(\d{2}/\d{2}/\d{4})',
        ]
        
        # Try labeled date first
        for pattern in date_patterns[:2]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                return FieldValueSchema(value=value, confidence=0.85)
        
        # Search in individual blocks for DOB label
        for idx, block in enumerate(text_blocks):
            t = block["text"].strip().upper()
            if any(label in t for label in ['DOB', 'D.O.B', 'BIRTH', 'जन्म']):
                # Check this block for a date
                for pattern in date_patterns:
                    match = re.search(pattern, block["text"], re.IGNORECASE)
                    if match:
                        return FieldValueSchema(
                            value=match.group(1).strip(),
                            confidence=float(block.get("confidence", 0.8))
                        )
                # Check the next block
                if idx + 1 < len(text_blocks):
                    next_text = text_blocks[idx + 1]["text"].strip()
                    for pattern in date_patterns:
                        match = re.search(pattern, next_text, re.IGNORECASE)
                        if match:
                            return FieldValueSchema(
                                value=match.group(1).strip(),
                                confidence=float(text_blocks[idx + 1].get("confidence", 0.8))
                            )
        
        # Fallback: find any date in full text
        for pattern in date_patterns[2:]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return FieldValueSchema(value=match.group(1).strip(), confidence=0.6)
        
        return FieldValueSchema(value="NOT_FOUND", confidence=0.0)
    
    def _find_gender(self, text: str, text_blocks: List) -> FieldValueSchema:
        """Find gender from text."""
        text_upper = text.upper()
        
        # Direct match
        gender_pattern = r'\b(MALE|FEMALE|पुरुष|महिला|TRANSGENDER)\b'
        match = re.search(gender_pattern, text_upper)
        if match:
            value = match.group(1)
            # Normalize  
            if value in ('पुरुष',):
                value = 'MALE'
            elif value in ('महिला',):
                value = 'FEMALE'
            return FieldValueSchema(value=value.title(), confidence=0.9)
        
        # Check individual blocks
        for block in text_blocks:
            t = block["text"].strip().upper()
            if t in ('MALE', 'FEMALE', 'M', 'F', 'पुरुष', 'महिला'):
                val = 'Male' if t in ('MALE', 'M', 'पुरुष') else 'Female'
                return FieldValueSchema(value=val, confidence=float(block.get("confidence", 0.85)))
        
        return FieldValueSchema(value="NOT_FOUND", confidence=0.0)
    
    def _find_address(self, text: str, text_blocks: List) -> FieldValueSchema:
        """Find address from text. Handles multi-block addresses (Aadhaar back side).
        
        Strategy:
        1. Label-based: look for 'Address'/'पता' label and grab everything after
        2. Relationship-based: look for S/O, D/O, W/O which typically precede address
        3. Multi-block assembly: collect blocks that look like address parts
        4. Pin code anchor: find 6-digit pin and grab surrounding text
        """
        # --- Strategy 1: Label-based extraction ---
        addr_labels = [
            r'(?:address|addr|पता|निवास|residential)\s*[:\-]?\s*(.{10,300})',
        ]
        for pattern in addr_labels:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                addr = match.group(1).strip()
                addr = re.sub(r'\s{2,}', ' ', addr).strip()
                if len(addr) > 5:
                    logger.info(f"Address found via label: {addr[:80]}")
                    return FieldValueSchema(value=addr[:150], confidence=0.8)
        
        # --- Strategy 2: S/O, D/O, W/O, C/O pattern (common on Aadhaar back) ---
        relation_patterns = [
            r'((?:S/O|D/O|W/O|C/O|s/o|d/o|w/o|c/o)\s*.{5,250})',
            r'((?:पुत्र|पुत्री|पत्नी)\s*.{5,200})',
        ]
        for pattern in relation_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                addr = match.group(1).strip()
                addr = re.sub(r'\s{2,}', ' ', addr).strip()
                if len(addr) > 5:
                    logger.info(f"Address found via relation pattern: {addr[:80]}")
                    return FieldValueSchema(value=addr[:150], confidence=0.75)
        
        # --- Strategy 3: Multi-block address assembly ---
        # Address blocks typically contain: numbers, commas, pin codes, state names
        # Collect blocks that look like address parts
        indian_states = {
            'andhra pradesh', 'arunachal pradesh', 'assam', 'bihar',
            'chhattisgarh', 'goa', 'gujarat', 'haryana', 'himachal pradesh',
            'jharkhand', 'karnataka', 'kerala', 'madhya pradesh', 'maharashtra',
            'manipur', 'meghalaya', 'mizoram', 'nagaland', 'odisha', 'orissa',
            'punjab', 'rajasthan', 'sikkim', 'tamil nadu', 'telangana',
            'tripura', 'uttar pradesh', 'uttarakhand', 'west bengal',
            'delhi', 'chandigarh', 'puducherry', 'jammu', 'kashmir',
            'ladakh', 'lakshadweep', 'andaman',
        }
        address_keywords = {
            'nagar', 'colony', 'street', 'road', 'lane', 'sector', 'block',
            'ward', 'dist', 'district', 'city', 'town', 'village', 'tehsil',
            'taluk', 'post', 'police', 'station', 'house', 'flat', 'floor',
            'no', 'near', 'opp', 'behind', 'main', 'cross', 'phase',
            'apartment', 'apt', 'building', 'plot', 'gali', 'mohalla',
            'marg', 'vihar', 'puram', 'pur', 'abad', 'garh', 'wadi',
        }
        
        address_blocks = []
        for block in text_blocks:
            t = block["text"].strip()
            t_lower = t.lower()
            
            is_address_part = False
            
            # Has a pin code (6 digits)
            if re.search(r'\b\d{6}\b', t):
                is_address_part = True
            
            # Contains Indian state name
            if any(state in t_lower for state in indian_states):
                is_address_part = True
            
            # Contains address keywords
            if any(kw in t_lower for kw in address_keywords):
                is_address_part = True
            
            # Contains house/plot number patterns
            if re.search(r'\b\d{1,4}[/\-]?\d{0,4}\b', t) and len(t) > 3 and not re.match(r'^\d{4}\s+\d{4}\s+\d{4}$', t):
                # Has numbers but not an Aadhaar number
                if any(kw in t_lower for kw in address_keywords) or ',' in t:
                    is_address_part = True
            
            # Contains comma (addresses often have commas)
            if ',' in t and len(t) > 5:
                is_address_part = True
            
            if is_address_part:
                address_blocks.append(t)
        
        if address_blocks:
            address = ', '.join(address_blocks)
            address = re.sub(r',\s*,', ',', address)
            address = re.sub(r'\s{2,}', ' ', address).strip()
            logger.info(f"Address assembled from {len(address_blocks)} blocks: {address[:80]}")
            return FieldValueSchema(value=address[:200], confidence=0.6)
        
        # --- Strategy 4: Pin code anchor ---
        pin_match = re.search(r'\b(\d{6})\b', text)
        if pin_match:
            pin_pos = pin_match.start()
            start = max(0, pin_pos - 120)
            end = min(len(text), pin_pos + 10)
            addr_text = text[start:end].strip()
            if len(addr_text) > 8:
                logger.info(f"Address found via pin code: {addr_text[:80]}")
                return FieldValueSchema(value=addr_text, confidence=0.5)
        
        # No address found — likely the front side of an ID card
        logger.info("No address found — document may be the front side of an ID card")
        return FieldValueSchema(value="NOT_FOUND", confidence=0.0)
    
    # ==================== PASSPORT ====================
    
    def _extract_passport_fields(self, text: str, text_blocks: List) -> Dict:
        """Extract fields from passport."""
        fields = {}
        
        # Surname
        surname_match = re.search(r'(?:surname|last\s*name)\s*[:\-]?\s*([A-Za-z\s]{2,30})', text, re.IGNORECASE)
        fields["surname"] = FieldValueSchema(
            value=surname_match.group(1).strip() if surname_match else "NOT_FOUND",
            confidence=0.8 if surname_match else 0.0
        )
        
        # Given names
        given_match = re.search(r'(?:given\s*name|first\s*name)\s*[:\-]?\s*([A-Za-z\s]{2,50})', text, re.IGNORECASE)
        fields["given_names"] = FieldValueSchema(
            value=given_match.group(1).strip() if given_match else "NOT_FOUND",
            confidence=0.8 if given_match else 0.0
        )
        
        # Passport number
        pp_match = re.search(r'([A-Z]\d{7,8})', text)
        fields["passport_number"] = FieldValueSchema(
            value=pp_match.group(1) if pp_match else "NOT_FOUND",
            confidence=0.85 if pp_match else 0.0
        )
        
        fields["dob"] = self._find_date(text, text_blocks)
        
        return fields
    
    # ==================== DRIVING LICENSE ====================
    
    def _extract_license_fields(self, text: str, text_blocks: List) -> Dict:
        """Extract fields from driving license."""
        fields = {}
        fields["name"] = self._find_name_in_id(text, text_blocks)
        
        # License number: typically XX-XXXXXXXXXX or XXDDXXXXXXXXXXXX
        lic_patterns = [
            r'([A-Z]{2}[\-\s]?\d{2}[\-\s]?\d{4,11})',
            r'(?:DL|License|licence)\s*(?:No|Number|#)?\s*[:\-]?\s*([A-Z0-9\-]{8,20})',
        ]
        for pat in lic_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                fields["license_number"] = FieldValueSchema(value=m.group(1).strip(), confidence=0.8)
                break
        else:
            fields["license_number"] = FieldValueSchema(value="NOT_FOUND", confidence=0.0)
        
        fields["dob"] = self._find_date(text, text_blocks)
        
        # Expiry
        exp_match = re.search(r'(?:valid|expiry|exp|validity)\s*[:\-]?\s*(\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4})', text, re.IGNORECASE)
        fields["expiry_date"] = FieldValueSchema(
            value=exp_match.group(1).strip() if exp_match else "NOT_FOUND",
            confidence=0.8 if exp_match else 0.0
        )
        
        fields["address"] = self._find_address(text, text_blocks)
        
        return fields
    
    # ==================== FORM ====================
    
    def _extract_form_fields(self, text: str, text_blocks: List) -> Dict:
        """Extract fields from generic form."""
        fields = {}
        fields["name"] = self._find_name_in_id(text, text_blocks)
        fields["date"] = self._find_date(text, text_blocks)
        
        ref_match = re.search(r'(?:ref|reference|application)\s*(?:no|number|#)?\s*[:\-]?\s*([A-Z0-9\-]{4,20})', text, re.IGNORECASE)
        fields["reference"] = FieldValueSchema(
            value=ref_match.group(1).strip() if ref_match else "NOT_FOUND",
            confidence=0.7 if ref_match else 0.0
        )
        
        return fields
    
    # ==================== CERTIFICATE ====================
    
    def _extract_certificate_fields(self, text: str, text_blocks: List) -> Dict:
        """Extract fields from certificate."""
        fields = {}
        fields["name"] = self._find_name_in_id(text, text_blocks)
        fields["date"] = self._find_date(text, text_blocks)
        
        cert_match = re.search(r'(?:certificate|cert)\s*(?:no|number|#)?\s*[:\-]?\s*([A-Z0-9\-]{4,20})', text, re.IGNORECASE)
        fields["certificate_number"] = FieldValueSchema(
            value=cert_match.group(1).strip() if cert_match else "NOT_FOUND",
            confidence=0.7 if cert_match else 0.0
        )
        
        issuer_match = re.search(r'(?:issued?\s*by|issuer|authority)\s*[:\-]?\s*([A-Za-z\s]{3,50})', text, re.IGNORECASE)
        fields["issuer"] = FieldValueSchema(
            value=issuer_match.group(1).strip() if issuer_match else "NOT_FOUND",
            confidence=0.7 if issuer_match else 0.0
        )
        
        return fields
    
    # ==================== BANK STATEMENT ====================
    
    def _extract_bank_fields(self, text: str, text_blocks: List) -> Dict:
        """Extract fields from bank statement."""
        fields = {}
        
        acc_match = re.search(r'(?:account|a\/c|acc)\s*(?:no|number|#)?\s*[:\-]?\s*(\d{9,18})', text, re.IGNORECASE)
        fields["account_number"] = FieldValueSchema(
            value=acc_match.group(1).strip() if acc_match else "NOT_FOUND",
            confidence=0.8 if acc_match else 0.0
        )
        
        fields["name"] = self._find_name_in_id(text, text_blocks)
        fields["date"] = self._find_date(text, text_blocks)
        
        bal_match = re.search(r'(?:balance|bal|closing)\s*[:\-]?\s*[₹$]?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
        fields["balance"] = FieldValueSchema(
            value=bal_match.group(1).strip() if bal_match else "NOT_FOUND",
            confidence=0.7 if bal_match else 0.0
        )
        
        return fields
    
    # ==================== SPATIAL HELPERS ====================
    
    def _find_text_near_label(
        self, text_blocks: List[Dict], label: str, proximity_threshold: float = 200.0
    ) -> Optional[Tuple[str, float]]:
        """Find text spatially near a label using bounding box proximity."""
        label_lower = label.lower()
        label_block = None
        label_idx = -1
        
        for idx, block in enumerate(text_blocks):
            if label_lower in block["text"].lower():
                label_block = block
                label_idx = idx
                break
        
        if label_block is None or "bbox" not in label_block:
            return None
        
        label_bbox = label_block["bbox"]
        label_right_x = max(p[0] for p in label_bbox)
        label_center_y = sum(p[1] for p in label_bbox) / len(label_bbox)
        
        best_candidate = None
        best_distance = float('inf')
        
        for idx, block in enumerate(text_blocks):
            if idx == label_idx or "bbox" not in block:
                continue
            
            bbox = block["bbox"]
            block_left_x = min(p[0] for p in bbox)
            block_center_y = sum(p[1] for p in bbox) / len(bbox)
            
            dx = block_left_x - label_right_x
            dy = abs(block_center_y - label_center_y)
            
            if dx < -50:
                continue
            
            distance = (max(0, dx) ** 2 + dy ** 2) ** 0.5
            
            if distance < proximity_threshold and distance < best_distance:
                best_distance = distance
                best_candidate = block
        
        if best_candidate:
            value = best_candidate["text"].strip()
            confidence = best_candidate.get("confidence", 0.7)
            if value and value.lower() != label_lower:
                return (value[:50], float(confidence))
        
        return None
