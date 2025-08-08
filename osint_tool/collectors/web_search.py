from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Dict, Any

from duckduckgo_search import DDGS


@dataclass
class SearchResult:
    title: str
    href: str
    body: str
    source: str


@dataclass
class ImageResult:
    title: str
    image: str
    thumbnail: str
    url: str
    source: str


def search_web(query: str, max_results: int = 30) -> List[SearchResult]:
    results: List[SearchResult] = []
    with DDGS() as ddgs:
        for item in ddgs.text(query, max_results=max_results):
            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    href=item.get("href", ""),
                    body=item.get("body", ""),
                    source=item.get("source", "duckduckgo"),
                )
            )
    return results


def search_images(query: str, max_results: int = 30, safesearch: str = "moderate") -> List[ImageResult]:
    items: List[ImageResult] = []
    with DDGS() as ddgs:
        for item in ddgs.images(query, max_results=max_results, safesearch=safesearch):
            items.append(
                ImageResult(
                    title=item.get("title", ""),
                    image=item.get("image", ""),
                    thumbnail=item.get("thumbnail", ""),
                    url=item.get("url", ""),
                    source=item.get("source", "duckduckgo"),
                )
            )
    return items


def to_dicts(items: Iterable) -> List[Dict[str, Any]]:
    return [item.__dict__ for item in items]