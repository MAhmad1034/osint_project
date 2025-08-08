from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image
import imagehash
import exifread
import json
from .utils import ensure_dir, get_logger, sanitize_filename


logger = get_logger("image_store")


@dataclass
class StoredImage:
    path: Path
    source_url: str
    title: Optional[str]
    meta: Dict[str, Any]
    phash: str


class ImageStore:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        ensure_dir(self.base_dir)

    def _subject_dir(self, subject_id: str) -> Path:
        return ensure_dir(self.base_dir / "images" / subject_id)

    def compute_phash(self, image_path: Path) -> str:
        with Image.open(image_path) as img:
            return str(imagehash.phash(img))

    def read_exif(self, image_path: Path) -> Dict[str, Any]:
        try:
            with open(image_path, "rb") as f:
                tags = exifread.process_file(f, details=False)
            simple = {str(k): str(v) for k, v in tags.items()}
            return simple
        except Exception:
            return {}

    def save_image(self, subject_id: str, image_bytes: bytes, filename_hint: str, source_url: str, title: Optional[str] = None, extra_meta: Optional[Dict[str, Any]] = None) -> Optional[StoredImage]:
        subject_dir = self._subject_dir(subject_id)
        filename = sanitize_filename(filename_hint) or "image"
        ext = ".jpg" if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")) else ""
        path = subject_dir / f"{filename}{ext}"
        # Prevent overwriting by adding suffixes
        counter = 1
        while path.exists():
            path = subject_dir / f"{filename}_{counter}{ext}"
            counter += 1
        path.write_bytes(image_bytes)

        try:
            phash = self.compute_phash(path)
        except Exception as e:
            logger.warning("Failed to compute pHash for %s: %s", path, e)
            phash = ""

        meta = {
            "source_url": source_url,
            "title": title,
            "exif": self.read_exif(path),
        }
        if extra_meta:
            meta.update(extra_meta)

        info = StoredImage(path=path, source_url=source_url, title=title, meta=meta, phash=phash)

        # Write sidecar metadata
        sidecar = path.with_suffix(path.suffix + ".json")
        sidecar.write_text(json.dumps({
            "path": str(path),
            "source_url": source_url,
            "title": title,
            "meta": meta,
            "phash": phash,
        }, indent=2))

        return info