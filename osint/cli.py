from __future__ import annotations

import argparse
from pathlib import Path
from .config import load_config
from .pipeline import Pipeline
from .utils import ensure_dir


def main():
    parser = argparse.ArgumentParser(description="OSINT Connection Analysis Pipeline")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    parser.add_argument("--output-dir", required=False, default="outputs", help="Where to write report and graph")
    args = parser.parse_args()

    cfg = load_config(args.config)
    ensure_dir(args.output_dir)

    pipeline = Pipeline(cfg)
    pipeline.run(args.output_dir)


if __name__ == "__main__":
    main()