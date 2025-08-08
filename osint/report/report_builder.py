from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
from ..utils import ensure_dir


@dataclass
class ReportImage:
    subject_id: str
    path: str
    source_url: str
    is_match: bool
    confidence: float
    title: str | None


class ReportBuilder:
    def __init__(self, templates_dir: str):
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(["html", "xml"]) 
        )

    def build(self, title: str, subjects: List[Dict[str, Any]], images: List[ReportImage], output_html: str):
        ensure_dir(Path(output_html).parent)
        template = self.env.get_template("report.html.j2")
        html = template.render(title=title, subjects=subjects, images=images)
        Path(output_html).write_text(html, encoding="utf-8")
        return output_html