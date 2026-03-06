"""Face detection and matching for ID document verification.

Uses DeepFace library with neural network models for accurate
face verification. This replaces the basic OpenCV histogram/ORB
approach with proper face embeddings that understand facial geometry.

Models used:
- VGG-Face (default): Deep CNN for face recognition embeddings
- OpenCV Haar Cascade: Fast face detection as fallback
"""

import cv2
import numpy as np
from PIL import Image
import io
import tempfile
import os
from typing import Dict, Optional
from loguru import logger


class FaceMatcher:
    """Detect faces in documents and match against selfie photos
    using deep learning face recognition."""
    
    def __init__(self):
        """Initialize face matcher."""
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        # Lazy-load DeepFace to avoid slow startup
        self._deepface = None
        logger.info("FaceMatcher initialized")
    
    @property
    def deepface(self):
        """Lazy-load DeepFace on first use."""
        if self._deepface is None:
            from deepface import DeepFace
            self._deepface = DeepFace
            logger.info("DeepFace loaded successfully")
        return self._deepface
    
    def detect_faces(self, image_bytes: bytes) -> Dict:
        """Detect faces in an image.
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Dictionary with face detection results
        """
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
            
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=4,
                minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            face_data = []
            for i, (x, y, w, h) in enumerate(faces):
                face_data.append({
                    "face_id": i,
                    "bbox": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                    "area": int(w * h),
                })
            
            logger.info(f"Detected {len(face_data)} face(s)")
            return {
                "faces_detected": len(face_data),
                "faces": face_data,
                "has_face": len(face_data) > 0,
            }
        except Exception as e:
            logger.error(f"Face detection failed: {str(e)}")
            raise
    
    def match_faces(self, document_bytes: bytes, selfie_bytes: bytes) -> Dict:
        """Compare face on a document against a selfie photo.
        
        Uses DeepFace with neural network embeddings for accurate
        face verification regardless of lighting, angle, or expression.
        
        Args:
            document_bytes: Document image containing a face
            selfie_bytes: Selfie/reference photo
            
        Returns:
            Dictionary with match results
        """
        tmp_doc = None
        tmp_selfie = None
        
        try:
            # Save to temp files (DeepFace works with file paths)
            tmp_doc = tempfile.NamedTemporaryFile(
                suffix='.jpg', delete=False
            )
            tmp_selfie = tempfile.NamedTemporaryFile(
                suffix='.jpg', delete=False
            )
            
            # Save document image
            doc_image = Image.open(io.BytesIO(document_bytes)).convert("RGB")
            doc_image.save(tmp_doc.name, format="JPEG", quality=95)
            tmp_doc.close()
            
            # Save selfie image
            selfie_image = Image.open(io.BytesIO(selfie_bytes)).convert("RGB")
            selfie_image.save(tmp_selfie.name, format="JPEG", quality=95)
            tmp_selfie.close()
            
            # Run DeepFace verification with multiple models for robustness
            results = {}
            models_to_try = ["VGG-Face", "Facenet", "ArcFace"]
            successful_results = []
            
            for model_name in models_to_try:
                try:
                    result = self.deepface.verify(
                        img1_path=tmp_doc.name,
                        img2_path=tmp_selfie.name,
                        model_name=model_name,
                        enforce_detection=False,  # Don't fail if face not clearly detected
                        detector_backend="opencv",
                    )
                    
                    # DeepFace returns distance (lower = more similar)
                    distance = result.get("distance", 1.0)
                    threshold = result.get("threshold", 0.4)
                    verified = result.get("verified", False)
                    
                    # Convert distance to similarity score (0-1)
                    # Piecewise linear: verified matches (distance <= threshold) get 70-100%
                    # Unverified (distance > threshold) decay from 70% toward 0%
                    if threshold > 0:
                        ratio = distance / threshold
                        if ratio <= 1.0:
                            # Verified range: distance=0 → 100%, distance=threshold → 70%
                            similarity = 1.0 - 0.3 * ratio
                        else:
                            # Unverified range: threshold → 70%, 2*threshold → 0%
                            similarity = max(0.0, 0.7 * (2.0 - ratio))
                    else:
                        similarity = 1.0 if verified else 0.0
                    
                    results[model_name] = {
                        "similarity": round(float(similarity), 3),
                        "distance": round(float(distance), 4),
                        "threshold": round(float(threshold), 4),
                        "verified": bool(verified),
                    }
                    successful_results.append({
                        "similarity": similarity,
                        "verified": verified,
                        "model": model_name,
                    })
                    
                    logger.info(
                        f"  {model_name}: distance={distance:.4f}, "
                        f"threshold={threshold:.4f}, verified={verified}"
                    )
                    
                except Exception as e:
                    logger.warning(f"  {model_name} failed: {e}")
                    results[model_name] = {
                        "similarity": 0.0,
                        "error": str(e)[:100],
                    }
            
            if not successful_results:
                return {
                    "match_score": 0.0,
                    "verdict": "ERROR",
                    "detail": "No face recognition models could process the images. "
                              "Ensure both images contain clearly visible faces.",
                    "methods": results,
                }
            
            # Overall score: average similarity from all successful models
            avg_similarity = sum(r["similarity"] for r in successful_results) / len(successful_results)
            
            # Voting: how many models say "verified"?
            votes_match = sum(1 for r in successful_results if r["verified"])
            total_votes = len(successful_results)
            
            # Determine verdict based on model consensus
            if votes_match >= 2 or (votes_match == 1 and avg_similarity >= 0.55):
                verdict = "MATCH"
                detail = (f"Faces verified as the same person. "
                          f"{votes_match}/{total_votes} models confirm a match.")
            elif votes_match == 1 or avg_similarity >= 0.4:
                verdict = "POSSIBLE_MATCH"
                detail = (f"Faces show similarity but results are mixed. "
                          f"{votes_match}/{total_votes} models confirm. Manual review recommended.")
            else:
                verdict = "MISMATCH"
                detail = (f"Faces do not appear to match. "
                          f"{votes_match}/{total_votes} models confirm a match.")
            
            logger.info(
                f"Face match result: {verdict} "
                f"(score={avg_similarity:.3f}, votes={votes_match}/{total_votes})"
            )
            
            return {
                "match_score": round(float(avg_similarity), 3),
                "verdict": verdict,
                "detail": detail,
                "votes": f"{votes_match}/{total_votes} models agree",
                "methods": results,
            }
            
        except Exception as e:
            logger.error(f"Face matching failed: {str(e)}")
            return {
                "match_score": 0.0,
                "verdict": "ERROR",
                "detail": f"Face matching error: {str(e)}",
                "methods": {},
            }
        finally:
            # Clean up temp files
            for tmp in [tmp_doc, tmp_selfie]:
                if tmp:
                    try:
                        os.unlink(tmp.name)
                    except Exception:
                        pass
