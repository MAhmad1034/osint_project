from __future__ import annotations

from typing import Optional, Tuple
import numpy as np
from deepface import DeepFace


class LocalDeepFace:
    def __init__(self, model_name: str = "Facenet512", detector_backend: str = "opencv"):
        self.model_name = model_name
        self.detector_backend = detector_backend

    def best_embedding(self, image_path: str) -> Optional[np.ndarray]:
        reps = DeepFace.represent(
            img_path=image_path,
            model_name=self.model_name,
            detector_backend=self.detector_backend,
            enforce_detection=False,
        )
        if not reps:
            return None
        # reps is a list of dicts with 'embedding'
        best = reps[0]
        emb = np.array(best["embedding"], dtype=np.float32)
        norm = np.linalg.norm(emb)
        if norm == 0:
            return None
        return emb / norm

    def similarity(self, emb_a: np.ndarray, emb_b: np.ndarray) -> float:
        return float(np.clip(np.dot(emb_a, emb_b), -1.0, 1.0))

    def verify_image_against_reference(self, candidate_image_path: str, reference_embedding: np.ndarray) -> Tuple[bool, float]:
        emb = self.best_embedding(candidate_image_path)
        if emb is None:
            return False, 0.0
        sim = self.similarity(reference_embedding, emb)
        return sim > 0.35, sim