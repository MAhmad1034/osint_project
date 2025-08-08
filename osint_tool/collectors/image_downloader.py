from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import httpx
from PIL import Image
from io import BytesIO


@dataclass
class SavedImage:
    filepath: Path
    url: str
    source: str
    title: str


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def download_images(
    items: Iterable[Dict[str, str]],
    dest_dir: Path,
    timeout_seconds: int = 15,
    max_images: int | None = None,
) -> List[SavedImage]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    saved: List[SavedImage] = []

    headers = {"User-Agent": "osint-tool/1.0 (+compliant; public-data-only)"}

    count = 0
    with httpx.Client(headers=headers, timeout=timeout_seconds, follow_redirects=True) as client:
        for item in items:
            if max_images is not None and count >= max_images:
                break

            url = item.get("image") or item.get("url")
            if not url:
                continue

            try:
                resp = client.get(url)
                resp.raise_for_status()
                data = resp.content
                img = Image.open(BytesIO(data))
                img_format = (img.format or "jpg").lower()
                name = _hash_bytes(data)
                out_path = dest_dir / f"{name}.{img_format}"
                img.save(out_path)
                saved.append(
                    SavedImage(
                        filepath=out_path,
                        url=url,
                        source=item.get("source", ""),
                        title=item.get("title", ""),
                    )
                )
                count += 1
            except Exception:
                continue

    return saved


def write_metadata_jsonl(items: Iterable[Dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for item in items:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")