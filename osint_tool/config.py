from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv


@dataclass
class AppConfig:
    env_name: str
    data_dir: Path
    reports_dir: Path
    allow_facial_recognition: bool

    # Optional providers
    bing_api_key: Optional[str] = None
    bing_endpoint: Optional[str] = None
    serpapi_api_key: Optional[str] = None
    facecheck_api_key: Optional[str] = None
    azure_face_endpoint: Optional[str] = None
    azure_face_key: Optional[str] = None
    # Optional Brave
    brave_api_key: Optional[str] = None


def load_config(config_path: Optional[Path] = None) -> AppConfig:
    load_dotenv(override=False)

    if config_path and config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            cfg_yaml = yaml.safe_load(f) or {}
    else:
        cfg_yaml = {}

    env_name = os.getenv("ENV_NAME", cfg_yaml.get("env_name", "dev"))
    data_dir = Path(os.getenv("DATA_DIR", cfg_yaml.get("data_dir", "data"))).resolve()
    reports_dir = Path(os.getenv("REPORTS_DIR", cfg_yaml.get("reports_dir", "reports"))).resolve()
    allow_fr = os.getenv("ALLOW_FACIAL_RECOGNITION", str(cfg_yaml.get("allow_facial_recognition", False))).lower() == "true"

    cfg = AppConfig(
        env_name=env_name,
        data_dir=data_dir,
        reports_dir=reports_dir,
        allow_facial_recognition=allow_fr,
        bing_api_key=os.getenv("BING_SEARCH_API_KEY", cfg_yaml.get("bing_api_key")),
        bing_endpoint=os.getenv("BING_SEARCH_ENDPOINT", cfg_yaml.get("bing_endpoint")),
        serpapi_api_key=os.getenv("SERPAPI_API_KEY", cfg_yaml.get("serpapi_api_key")),
        facecheck_api_key=os.getenv("FACECHECK_API_KEY", cfg_yaml.get("facecheck_api_key")),
        azure_face_endpoint=os.getenv("AZURE_FACE_ENDPOINT", cfg_yaml.get("azure_face_endpoint")),
        azure_face_key=os.getenv("AZURE_FACE_KEY", cfg_yaml.get("azure_face_key")),
        brave_api_key=os.getenv("BRAVE_SEARCH_API_KEY", cfg_yaml.get("brave_api_key")),
    )

    cfg.data_dir.mkdir(parents=True, exist_ok=True)
    cfg.reports_dir.mkdir(parents=True, exist_ok=True)

    return cfg