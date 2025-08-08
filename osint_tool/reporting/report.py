from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape


def _get_env(templates_dir: Path) -> Environment:
    return Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(enabled_extensions=("html", "xml")),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_markdown_report(
    templates_dir: Path,
    subject_a: str,
    subject_b: str,
    summary: Dict,
    overlaps: List[str],
    out_path: Path,
) -> None:
    env = _get_env(templates_dir)
    template = env.get_template("report.md.j2")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = template.render(
        subject_a=subject_a,
        subject_b=subject_b,
        summary=summary,
        overlaps=overlaps,
    )
    out_path.write_text(content, encoding="utf-8")