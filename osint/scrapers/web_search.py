from __future__ import annotations

from typing import List, Dict, Any
from duckduckgo_search import DDGS
from ..utils import get_logger


logger = get_logger("scrapers.web_search")


def duckduckgo_image_search(query: str, max_results: int = 25) -> List[Dict[str, Any]]:
    """Search DuckDuckGo Images and return a list of dicts with url, title, source."""
    results: List[Dict[str, Any]] = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.images(keywords=query, max_results=max_results, safesearch="moderate"):  # type: ignore
                results.append({
                    "image": r.get("image"),
                    "thumbnail": r.get("thumbnail"),
                    "title": r.get("title"),
                    "source": r.get("source"),
                    "height": r.get("height"),
                    "width": r.get("width"),
                })
    except Exception as e:
        logger.error("DuckDuckGo search failed for '%s': %s", query, e)
    return results