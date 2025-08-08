from __future__ import annotations

import requests
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from ..utils import get_logger


logger = get_logger("face.azure")


class AzureFaceClient:
    def __init__(self, endpoint: str, key: str):
        self.endpoint = endpoint.rstrip("/")
        self.key = key
        self.headers_json = {"Ocp-Apim-Subscription-Key": self.key, "Content-Type": "application/json"}
        self.headers_bin = {"Ocp-Apim-Subscription-Key": self.key, "Content-Type": "application/octet-stream"}

    def detect(self, image_path: str) -> List[Dict[str, Any]]:
        url = f"{self.endpoint}/detect?returnFaceId=true&returnFaceAttributes=qualityForRecognition"
        data = Path(image_path).read_bytes()
        resp = requests.post(url, headers=self.headers_bin, data=data, timeout=20)
        if resp.status_code != 200:
            logger.error("Azure Detect failed %s: %s", resp.status_code, resp.text)
            return []
        return resp.json()

    def verify(self, face_id1: str, face_id2: str) -> Dict[str, Any]:
        url = f"{self.endpoint}/verify"
        payload = {"faceId1": face_id1, "faceId2": face_id2}
        resp = requests.post(url, headers=self.headers_json, json=payload, timeout=20)
        if resp.status_code != 200:
            logger.error("Azure Verify failed %s: %s", resp.status_code, resp.text)
            return {"isIdentical": False, "confidence": 0.0}
        return resp.json()

    def best_face_id(self, image_path: str) -> Optional[str]:
        faces = self.detect(image_path)
        if not faces:
            return None
        # Pick largest face by rectangle area
        def area(f):
            rect = f.get("faceRectangle", {})
            return rect.get("width", 0) * rect.get("height", 0)
        best = max(faces, key=area)
        return best.get("faceId")

    def verify_image_against_reference(self, candidate_image_path: str, reference_face_id: str) -> Tuple[bool, float]:
        cand_id = self.best_face_id(candidate_image_path)
        if not cand_id:
            return False, 0.0
        result = self.verify(reference_face_id, cand_id)
        return bool(result.get("isIdentical", False)), float(result.get("confidence", 0.0))