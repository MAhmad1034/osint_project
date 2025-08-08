from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any
import networkx as nx


@dataclass
class NodeTypes:
    SUBJECT: str = "subject"
    ACCOUNT: str = "account"
    IMAGE: str = "image"
    URL: str = "url"


class GraphBuilder:
    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_subject(self, subject_id: str, label: str):
        self.graph.add_node(f"subject:{subject_id}", type=NodeTypes.SUBJECT, label=label)

    def add_account(self, subject_id: str, platform: str, handle: str):
        node_id = f"account:{platform}:{handle}"
        self.graph.add_node(node_id, type=NodeTypes.ACCOUNT, platform=platform, handle=handle)
        self.graph.add_edge(f"subject:{subject_id}", node_id, type="owns")

    def add_image(self, subject_id: str, path: str, source_url: str, is_match: bool, confidence: float):
        node_id = f"image:{path}"
        self.graph.add_node(node_id, type=NodeTypes.IMAGE, path=path, match=is_match, confidence=confidence)
        self.graph.add_edge(f"subject:{subject_id}", node_id, type="appears_in")
        if source_url:
            self.add_url(source_url)
            self.graph.add_edge(node_id, f"url:{source_url}", type="hosted_at")

    def add_url(self, url: str):
        self.graph.add_node(f"url:{url}", type=NodeTypes.URL, url=url)

    def export_graphml(self, path: str):
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        nx.write_graphml(self.graph, p)