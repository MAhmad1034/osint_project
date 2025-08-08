from __future__ import annotations

from typing import List
import httpx
import os

from osint_tool.config import AppConfig
from osint_tool.collectors.web_search import SearchResult, ImageResult


BASE_URL = "https://api.search.brave.com/res/v1"


def _headers(api_key: str) -> dict:
    return {
        "Accept": "application/json",
        "X-Subscription-Token": api_key,
        "User-Agent": "osint-tool/1.0 (+compliant; public-data-only)",
    }


def brave_web_search(cfg: AppConfig, query: str, max_results: int = 30) -> List[SearchResult]:
    api_key = cfg.__dict__.get("brave_api_key") or os.getenv("BRAVE_SEARCH_API_KEY")
    if not api_key:
        raise RuntimeError("Brave API key not configured")

    url = f"{BASE_URL}/web/search"
    params = {
        "q": query,
        "count": max(1, min(max_results, 20)),
        "search_lang": "en",
        "safesearch": "moderate",
    }

    results: List[SearchResult] = []
    with httpx.Client(timeout=25) as client:
        resp = client.get(url, headers=_headers(api_key), params=params)
        resp.raise_for_status()
        data = resp.json() or {}
        web = data.get("web", {})
        for item in web.get("results", []):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    href=item.get("url", ""),
                    body=item.get("description", ""),
                    source="brave",
                )
            )
    return results


def brave_image_search(cfg: AppConfig, query: str, max_results: int = 30) -> List[ImageResult]:
    api_key = cfg.__dict__.get("brave_api_key") or os.getenv("BRAVE_SEARCH_API_KEY")
    if not api_key:
        raise RuntimeError("Brave API key not configured")

    url = f"{BASE_URL}/images/search"
    params = {
        "q": query,
        "count": max(1, min(max_results, 20)),
        "search_lang": "en",
        "safesearch": "moderate",
    }

    items: List[ImageResult] = []
    with httpx.Client(timeout=25) as client:
        resp = client.get(url, headers=_headers(api_key), params=params)
        resp.raise_for_status()
        data = resp.json() or {}
        for item in data.get("results", []):
            items.append(
                ImageResult(
                    title=item.get("title", ""),
                    image=item.get("properties", {}).get("url", ""),
                    thumbnail=item.get("thumbnail", {}).get("src", ""),
                    url=item.get("url", ""),
                    source="brave",
                )
            )
    return items