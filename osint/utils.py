from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Optional
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        logger.addHandler(handler)
    return logger


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


class DownloadError(Exception):
    pass


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8), reraise=True,
       retry=retry_if_exception_type(DownloadError))
def download_file(url: str, dest_path: str, timeout: int = 15, user_agent: Optional[str] = None) -> str:
    headers = {"User-Agent": user_agent or "Mozilla/5.0 (compatible; OSINT/1.0)"}
    try:
        with requests.get(url, headers=headers, timeout=timeout, stream=True) as r:
            if r.status_code != 200:
                raise DownloadError(f"HTTP {r.status_code} for {url}")
            total = 0
            Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total += len(chunk)
            if total == 0:
                raise DownloadError("Downloaded zero bytes")
    except requests.RequestException as e:
        raise DownloadError(str(e))
    return dest_path


def sanitize_filename(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in ("-", "_", ".")).rstrip()