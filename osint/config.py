from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import os
import yaml
from dotenv import load_dotenv


@dataclass
class SubjectConfig:
    id: str
    names: List[str] = field(default_factory=list)
    usernames: List[str] = field(default_factory=list)
    seed_urls: List[str] = field(default_factory=list)


@dataclass
class SearchConfig:
    platforms: List[str] = field(default_factory=lambda: ["duckduckgo_images"])
    image_results_per_query: int = 25


@dataclass
class FaceConfig:
    provider: str = "local_deepface"  # default to free local provider with wheels on Windows
    confidence_threshold: float = 0.67     # used by Azure
    similarity_threshold: float = 0.35     # used by local providers
    azure_endpoint: Optional[str] = None
    azure_key: Optional[str] = None


@dataclass
class ReportConfig:
    title: str = "OSINT Connection Report"
    output_dir: str = "outputs"


@dataclass
class StorageConfig:
    base_dir: str = "data"
    keep_originals: bool = True


@dataclass
class AppConfig:
    subjects: List[SubjectConfig]
    search: SearchConfig = field(default_factory=SearchConfig)
    face: FaceConfig = field(default_factory=FaceConfig)
    report: ReportConfig = field(default_factory=ReportConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)


def _resolve_env(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str) and value.startswith("env:"):
        _, env_key = value.split(":", 1)
        return os.getenv(env_key)
    return value


def load_config(path: str) -> AppConfig:
    load_dotenv()
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    subjects = [SubjectConfig(**s) for s in raw.get("subjects", [])]

    search = SearchConfig(**raw.get("search", {}))

    face_dict = raw.get("face", {})
    face = FaceConfig(**face_dict)
    face.azure_endpoint = face.azure_endpoint or os.getenv("AZURE_FACE_ENDPOINT")
    face.azure_key = face.azure_key or os.getenv("AZURE_FACE_KEY")

    report = ReportConfig(**raw.get("report", {}))
    storage = StorageConfig(**raw.get("storage", {}))

    return AppConfig(
        subjects=subjects,
        search=search,
        face=face,
        report=report,
        storage=storage,
    )