"""Document tamper detection using image forensics techniques.

Detects potential image manipulation through:
1. Error Level Analysis (ELA) — detects JPEG re-compression artifacts
2. Noise Analysis — detects inconsistent noise patterns
3. Edge Density Analysis — detects copy-paste regions
"""

import cv2
import numpy as np
from PIL import Image
import io
import tempfile
from typing import Dict, List, Tuple
from loguru import logger


class TamperDetector:
    """Analyzes document images for signs of tampering or editing."""
    
    def __init__(self, ela_quality: int = 90):
        self.ela_quality = ela_quality
        logger.info("TamperDetector initialized")
    
    def analyze(self, image_bytes: bytes) -> Dict:
        """Run full tamper analysis on an image.
        
        Args:
            image_bytes: Raw image file bytes
            
        Returns:
            Dictionary with tamper analysis results
        """
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Run all analyses
            ela_result = self._error_level_analysis(image)
            noise_result = self._noise_analysis(image_cv)
            edge_result = self._edge_density_analysis(image_cv)
            metadata_result = self._metadata_analysis(image)
            
            # Calculate overall trust score (0-100)
            scores = [
                ela_result["score"],      # 0-100, higher = more trusted
                noise_result["score"],
                edge_result["score"],
                metadata_result["score"],
            ]
            overall_score = sum(scores) / len(scores)
            
            # Determine verdict
            if overall_score >= 75:
                verdict = "AUTHENTIC"
                verdict_detail = "No significant signs of tampering detected."
            elif overall_score >= 50:
                verdict = "SUSPICIOUS"
                verdict_detail = "Some anomalies detected. Manual review recommended."
            else:
                verdict = "LIKELY_TAMPERED"
                verdict_detail = "Multiple indicators of potential manipulation found."
            
            # Collect flags
            flags = []
            flags.extend(ela_result.get("flags", []))
            flags.extend(noise_result.get("flags", []))
            flags.extend(edge_result.get("flags", []))
            flags.extend(metadata_result.get("flags", []))
            
            result = {
                "overall_trust_score": round(overall_score, 1),
                "verdict": verdict,
                "verdict_detail": verdict_detail,
                "analyses": {
                    "error_level_analysis": {
                        "score": ela_result["score"],
                        "description": ela_result["description"],
                    },
                    "noise_analysis": {
                        "score": noise_result["score"],
                        "description": noise_result["description"],
                    },
                    "edge_density": {
                        "score": edge_result["score"],
                        "description": edge_result["description"],
                    },
                    "metadata": {
                        "score": metadata_result["score"],
                        "description": metadata_result["description"],
                    },
                },
                "flags": flags,
            }
            
            logger.info(f"Tamper analysis complete: {verdict} (score={overall_score:.1f})")
            return result
            
        except Exception as e:
            logger.error(f"Tamper analysis failed: {str(e)}")
            raise
    
    def _error_level_analysis(self, image: Image.Image) -> Dict:
        """Error Level Analysis — detects JPEG re-compression artifacts.
        
        Re-saves the image at a known JPEG quality, then computes the difference.
        Heavily edited regions show higher error levels.
        """
        try:
            # Re-save at known quality
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=self.ela_quality)
            buffer.seek(0)
            resaved = Image.open(buffer)
            
            # Compute pixel-level difference
            original = np.array(image, dtype=np.float64)
            compressed = np.array(resaved, dtype=np.float64)
            
            diff = np.abs(original - compressed)
            ela_image = diff.astype(np.uint8)
            
            # Statistics
            mean_error = float(np.mean(diff))
            max_error = float(np.max(diff))
            std_error = float(np.std(diff))
            
            # High standard deviation in ELA = inconsistent compression = suspicious
            flags = []
            
            # Check for hotspots — regions with much higher error than average
            threshold = mean_error + 2.5 * std_error
            hotspot_pixels = np.sum(diff > threshold)
            total_pixels = diff.shape[0] * diff.shape[1]
            hotspot_ratio = hotspot_pixels / total_pixels if total_pixels > 0 else 0
            
            if hotspot_ratio > 0.05:
                flags.append("ELA hotspots detected — possible localized editing")
                score = max(20, 70 - hotspot_ratio * 500)
            elif std_error > 15:
                flags.append("High ELA variance — inconsistent compression levels")
                score = max(30, 80 - std_error * 2)
            elif mean_error > 20:
                flags.append("Elevated compression artifacts")
                score = max(40, 90 - mean_error)
            else:
                score = min(95, 80 + (20 - mean_error))
            
            return {
                "score": round(min(100, max(0, score)), 1),
                "description": f"Mean error: {mean_error:.1f}, Std: {std_error:.1f}, Hotspot ratio: {hotspot_ratio:.4f}",
                "flags": flags,
            }
        except Exception as e:
            logger.warning(f"ELA analysis failed: {e}")
            return {"score": 50, "description": "Analysis could not be completed", "flags": []}
    
    def _noise_analysis(self, image_cv: np.ndarray) -> Dict:
        """Analyze noise consistency across the image.
        
        Tampered images often have inconsistent noise patterns —
        pasted regions may have different noise characteristics.
        """
        try:
            gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
            
            # Split image into grid blocks and measure noise in each
            h, w = gray.shape
            block_size = max(32, min(h, w) // 8)
            
            noise_levels = []
            for y in range(0, h - block_size, block_size):
                for x in range(0, w - block_size, block_size):
                    block = gray[y:y+block_size, x:x+block_size].astype(np.float64)
                    # High-pass filter to isolate noise
                    blurred = cv2.GaussianBlur(block, (5, 5), 0)
                    noise = np.std(block - blurred)
                    noise_levels.append(noise)
            
            if not noise_levels:
                return {"score": 50, "description": "Image too small for analysis", "flags": []}
            
            noise_array = np.array(noise_levels)
            mean_noise = float(np.mean(noise_array))
            std_noise = float(np.std(noise_array))
            
            # Coefficient of variation — high = inconsistent noise
            cv = std_noise / mean_noise if mean_noise > 0 else 0
            
            flags = []
            if cv > 0.8:
                flags.append("Highly inconsistent noise patterns across regions")
                score = max(20, 60 - cv * 30)
            elif cv > 0.5:
                flags.append("Moderate noise inconsistency detected")
                score = max(40, 75 - cv * 20)
            else:
                score = min(95, 80 + (0.5 - cv) * 30)
            
            return {
                "score": round(min(100, max(0, score)), 1),
                "description": f"Noise CV: {cv:.3f}, Mean: {mean_noise:.2f}, Std: {std_noise:.2f}",
                "flags": flags,
            }
        except Exception as e:
            logger.warning(f"Noise analysis failed: {e}")
            return {"score": 50, "description": "Analysis could not be completed", "flags": []}
    
    def _edge_density_analysis(self, image_cv: np.ndarray) -> Dict:
        """Analyze edge density for copy-paste artifacts.
        
        Pasted regions often create unnatural edge boundaries.
        """
        try:
            gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            h, w = edges.shape
            block_size = max(32, min(h, w) // 6)
            
            densities = []
            for y in range(0, h - block_size, block_size):
                for x in range(0, w - block_size, block_size):
                    block = edges[y:y+block_size, x:x+block_size]
                    density = np.sum(block > 0) / (block_size * block_size)
                    densities.append(density)
            
            if not densities:
                return {"score": 50, "description": "Image too small", "flags": []}
            
            density_array = np.array(densities)
            mean_density = float(np.mean(density_array))
            std_density = float(np.std(density_array))
            
            # Very high std = some regions have sharp edges while others don't
            cv = std_density / mean_density if mean_density > 0 else 0
            
            flags = []
            if cv > 1.2:
                flags.append("Unusual edge density variation — possible pasted regions")
                score = max(30, 65 - cv * 15)
            elif cv > 0.8:
                flags.append("Moderate edge density variation")
                score = max(50, 75 - cv * 10)
            else:
                score = min(95, 85 + (0.8 - cv) * 15)
            
            return {
                "score": round(min(100, max(0, score)), 1),
                "description": f"Edge density CV: {cv:.3f}, Mean: {mean_density:.4f}",
                "flags": flags,
            }
        except Exception as e:
            logger.warning(f"Edge analysis failed: {e}")
            return {"score": 50, "description": "Analysis could not be completed", "flags": []}
    
    def _metadata_analysis(self, image: Image.Image) -> Dict:
        """Analyze image metadata for editing software signatures."""
        try:
            exif = image.getexif()
            flags = []
            score = 85  # Default: neutral
            
            if exif:
                # Check for editing software tags
                software = exif.get(305, "")  # Tag 305 = Software
                if software:
                    editing_tools = ["photoshop", "gimp", "paint", "editor", "pixlr", "canva", "snapseed"]
                    if any(tool in software.lower() for tool in editing_tools):
                        flags.append(f"Editing software detected: {software}")
                        score = 35
                    else:
                        score = 80
                
                # Check for modification date != creation date
                date_original = exif.get(36867, "")
                date_modified = exif.get(306, "")
                if date_original and date_modified and date_original != date_modified:
                    flags.append("Image modification date differs from creation date")
                    score = min(score, 55)
            else:
                # No EXIF — possibly stripped (suspicious for camera photos, normal for screenshots)
                flags.append("No EXIF metadata found — may have been stripped")
                score = 65
            
            return {
                "score": round(score, 1),
                "description": f"EXIF tags: {len(exif) if exif else 0}",
                "flags": flags,
            }
        except Exception as e:
            logger.warning(f"Metadata analysis failed: {e}")
            return {"score": 50, "description": "Could not read metadata", "flags": []}
