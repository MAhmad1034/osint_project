from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import networkx as nx
from urllib.parse import urlparse


@dataclass
class SubjectSummary:
    subject: str
    domains: Counter
    links: List[str]


def extract_domain(url: str) -> str:
    try:
        netloc = urlparse(url).netloc
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc
    except Exception:
        return ""


def summarize_subject(subject: str, links: Iterable[str]) -> SubjectSummary:
    domain_counts: Counter = Counter(extract_domain(u) for u in links if u)
    link_list = [u for u in links if u]
    return SubjectSummary(subject=subject, domains=domain_counts, links=link_list)


def build_overlap_graph(a: SubjectSummary, b: SubjectSummary) -> nx.Graph:
    graph = nx.Graph()

    graph.add_node(a.subject, type="subject")
    graph.add_node(b.subject, type="subject")

    for domain, count in a.domains.items():
        if not domain:
            continue
        graph.add_node(domain, type="domain")
        graph.add_edge(a.subject, domain, weight=int(count))

    for domain, count in b.domains.items():
        if not domain:
            continue
        graph.add_node(domain, type="domain")
        graph.add_edge(b.subject, domain, weight=int(count))

    return graph


def graph_overlaps(graph: nx.Graph) -> List[str]:
    overlaps: List[str] = []
    for node, data in graph.nodes(data=True):
        if data.get("type") == "domain":
            neighbors = list(graph.neighbors(node))
            if len(neighbors) >= 2:
                overlaps.append(node)
    return sorted(overlaps)


def export_graphml(graph: nx.Graph, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    nx.write_graphml(graph, out_path)