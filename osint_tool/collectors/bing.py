from __future__ import annotations

from typing import List, Optional

import httpx

from osint_tool.config import AppConfig
from osint_tool.collectors.web_search import SearchResult, ImageResult


def _headers(api_key: str) -> dict:
    return {
        "Ocp-Apim-Subscription-Key": api_key,
        "Accept": "application/json",
        "User-Agent": "osint-tool/1.0 (+compliant; public-data-only)",
    }


def bing_web_search(cfg: AppConfig, query: str, max_results: int = 30) -> List[SearchResult]:
    if not cfg.bing_api_key:
        raise RuntimeError("Bing API key not configured")
    endpoint = (cfg.bing_endpoint or "https://api.bing.microsoft.com/v7.0").rstrip("/")
    url = f"{endpoint}/search"

    params = {
        "q": query,
        "count": max(1, min(max_results, 50)),
        "responseFilter": "Webpages",
        "safeSearch": "Moderate",
        "textDecorations": False,
    }

    results: List[SearchResult] = []
    with httpx.Client(timeout=20) as client:
        resp = client.get(url, headers=_headers(cfg.bing_api_key), params=params)
        resp.raise_for_status()
        data = resp.json()
        web_pages = (data or {}).get("webPages", {}).get("value", [])
        for item in web_pages:
            results.append(
                SearchResult(
                    title=item.get("name", ""),
                    href=item.get("url", ""),
                    body=item.get("snippet", ""),
                    source="bing",
                )
            )
    return results


def bing_image_search(cfg: AppConfig, query: str, max_results: int = 30) -> List[ImageResult]:
    if not cfg.bing_api_key:
        raise RuntimeError("Bing API key not configured")
    endpoint = (cfg.bing_endpoint or "https://api.bing.microsoft.com/v7.0").rstrip("/")
    url = f"{endpoint}/images/search"

    params = {
        "q": query,
        "count": max(1, min(max_results, 50)),
        "safeSearch": "Moderate",
    }

    items: List[ImageResult] = []
    with httpx.Client(timeout=20) as client:
        resp = client.get(url, headers=_headers(cfg.bing_api_key), params=params)
        resp.raise_for_status()
        data = resp.json()
        values = (data or {}).get("value", [])
        for item in values:
            items.append(
                ImageResult(
                    title=item.get("name", ""),
                    image=item.get("contentUrl", ""),
                    thumbnail=(item.get("thumbnailUrl") or ""),
                    url=item.get("hostPageUrl", ""),
                    source="bing",
                )
            )
    return items