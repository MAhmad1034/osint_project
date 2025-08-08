from __future__ import annotations

from typing import Optional, Tuple
import numpy as np
from insightface.app import FaceAnalysis
from ..utils import get_logger


logger = get_logger("face.local_insightface")


class LocalInsightFace:
    def __init__(self, det_size: tuple[int, int] = (640, 640)):
        self.app = FaceAnalysis(name="buffalo_l")
        # ctx_id = 0 for CPU-only with onnxruntime; InsightFace handles provider selection
        self.app.prepare(ctx_id=0, det_size=det_size)

    def best_embedding(self, image_path: str) -> Optional[np.ndarray]:
        faces = self.app.get(image_path)
        if not faces:
            return None
        # pick face with largest bbox area
        def area(face):
            box = face.bbox
            return max(0.0, (box[2] - box[0]) * (box[3] - box[1]))
        best = max(faces, key=area)
        emb = best.embedding
        if emb is None:
            return None
        # Ensure L2 normalization
        norm = np.linalg.norm(emb)
        if norm == 0:
            return None
        return emb / norm

    def similarity(self, emb_a: np.ndarray, emb_b: np.ndarray) -> float:
        # Cosine similarity on normalized embeddings
        return float(np.clip(np.dot(emb_a, emb_b), -1.0, 1.0))

    def verify_image_against_reference(self, candidate_image_path: str, reference_embedding: np.ndarray) -> Tuple[bool, float]:
        emb = self.best_embedding(candidate_image_path)
        if emb is None:
            return False, 0.0
        sim = self.similarity(reference_embedding, emb)
        # Return similarity as confidence proxy
        return sim > 0.35, sim