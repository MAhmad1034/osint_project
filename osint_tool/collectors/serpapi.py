from __future__ import annotations

from typing import List
import httpx

from osint_tool.config import AppConfig
from osint_tool.collectors.web_search import SearchResult, ImageResult


BASE_URL = "https://serpapi.com/search.json"


def serpapi_web_search(cfg: AppConfig, query: str, max_results: int = 30) -> List[SearchResult]:
    if not cfg.serpapi_api_key:
        raise RuntimeError("SerpAPI API key not configured")

    params = {
        "engine": "google",
        "q": query,
        "num": max(1, min(max_results, 100)),
        "api_key": cfg.serpapi_api_key,
        "safe": "active",
        "hl": "en",
        "gl": "us",
    }

    results: List[SearchResult] = []
    with httpx.Client(timeout=25) as client:
        resp = client.get(BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json() or {}
        organic = data.get("organic_results", [])
        for item in organic:
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    href=item.get("link", ""),
                    body=item.get("snippet", ""),
                    source="serpapi",
                )
            )
    return results


def serpapi_image_search(cfg: AppConfig, query: str, max_results: int = 30) -> List[ImageResult]:
    if not cfg.serpapi_api_key:
        raise RuntimeError("SerpAPI API key not configured")

    params = {
        "engine": "google_images",
        "q": query,
        "ijn": 0,
        "api_key": cfg.serpapi_api_key,
        "safe": "active",
        "hl": "en",
        "gl": "us",
        "num": max(1, min(max_results, 100)),
    }

    items: List[ImageResult] = []
    with httpx.Client(timeout=25) as client:
        resp = client.get(BASE_URL, params=params)
        resp.raise_for_status()
        data = resp.json() or {}
        imgs = data.get("images_results", [])
        for item in imgs[:max_results]:
            items.append(
                ImageResult(
                    title=item.get("title", ""),
                    image=item.get("original", "") or item.get("thumbnail", ""),
                    thumbnail=item.get("thumbnail", ""),
                    url=item.get("link", "") or item.get("source", ""),
                    source="serpapi",
                )
            )
    return items