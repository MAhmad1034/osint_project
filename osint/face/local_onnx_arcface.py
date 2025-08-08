from __future__ import annotations

from typing import Optional, Tuple
from pathlib import Path
import numpy as np
import cv2
import onnxruntime as ort


class LocalOnnxArcFace:
    def __init__(self, model_path: str | None = None):
        # Default expected model location
        self.model_path = model_path or str(Path("data/models/arcfaceresnet100-8.onnx"))
        if not Path(self.model_path).exists():
            raise FileNotFoundError(
                f"ArcFace ONNX model not found at {self.model_path}. Please download arcfaceresnet100-8.onnx and place it there."
            )
        self.session = ort.InferenceSession(self.model_path, providers=["CPUExecutionProvider"])  # type: ignore
        self.input_name = self.session.get_inputs()[0].name
        # Haar cascade for face detection (bundled with OpenCV)
        cascade_path = str(Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml")
        self.detector = cv2.CascadeClassifier(cascade_path)

    def _detect_largest_face(self, img_bgr: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, flags=cv2.CASCADE_SCALE_IMAGE)
        if len(faces) == 0:
            return None
        # faces: (x, y, w, h); pick largest area
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        # Add a small margin
        margin = int(0.1 * max(w, h))
        x0 = max(0, x - margin)
        y0 = max(0, y - margin)
        x1 = min(img_bgr.shape[1], x + w + margin)
        y1 = min(img_bgr.shape[0], y + h + margin)
        return x0, y0, x1 - x0, y1 - y0

    def _preprocess_arcface(self, img_bgr: np.ndarray) -> np.ndarray:
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        img_rgb = cv2.resize(img_rgb, (112, 112), interpolation=cv2.INTER_LINEAR)
        img = img_rgb.astype("float32") / 255.0
        img = (img - 0.5) / 0.5  # normalize to [-1, 1]
        img = np.transpose(img, (2, 0, 1))  # CHW
        img = np.expand_dims(img, axis=0)   # NCHW
        return img

    def best_embedding(self, image_path: str) -> Optional[np.ndarray]:
        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            return None
        rect = self._detect_largest_face(img_bgr)
        if rect is not None:
            x, y, w, h = rect
            face = img_bgr[y:y+h, x:x+w]
        else:
            face = img_bgr
        inp = self._preprocess_arcface(face)
        outputs = self.session.run(None, {self.input_name: inp})
        emb = outputs[0].squeeze()
        if emb is None or emb.size == 0:
            return None
        emb = emb.astype(np.float32)
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