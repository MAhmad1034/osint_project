from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List

import typer
from rich import print

from osint_tool.config import load_config
from osint_tool.utils.logging import configure_logging, get_logger
from osint_tool.collectors.web_search import search_web, search_images, to_dicts
from osint_tool.collectors.image_downloader import download_images, write_metadata_jsonl
from osint_tool.analysis.network import summarize_subject, build_overlap_graph, graph_overlaps, export_graphml
from collections import Counter


app = typer.Typer(add_completion=False, help="Compliant OSINT link analysis toolkit")
logger = get_logger(__name__)


@app.callback()
def _init_logging(verbose: bool = typer.Option(False, "--verbose", help="Enable verbose logging")):
    configure_logging()
    if verbose:
        import logging
        logger.setLevel(logging.DEBUG)


@app.command()
def init(subject_a: str = typer.Option(..., help="Folder-friendly ID for subject A"),
         subject_b: str = typer.Option(..., help="Folder-friendly ID for subject B")):
    cfg = load_config()
    for subject in [subject_a, subject_b]:
        (cfg.data_dir / "raw" / subject / "images").mkdir(parents=True, exist_ok=True)
        (cfg.data_dir / "raw" / subject / "metadata").mkdir(parents=True, exist_ok=True)
    print(f"Initialized data folders under {cfg.data_dir}")


@app.command()
def collect(subject: str = typer.Option(..., help="Subject folder-friendly ID"),
            query: str = typer.Option(..., help="Public search query (quotes, keywords, handles)"),
            limit: int = typer.Option(30, help="Max results to fetch for links and images"),
            save_images: bool = typer.Option(True, help="Download discovered images"),
            provider: str = typer.Option("ddg", help="Search provider: ddg|bing|serpapi|brave")):
    cfg = load_config()

    web_results = []
    image_results = []

    p = provider.lower()
    if p == "bing":
        from osint_tool.collectors.bing import bing_web_search, bing_image_search
        try:
            web_results = bing_web_search(cfg, query, max_results=limit)
        except Exception as e:
            print(f"[yellow]Warning:[/yellow] Bing web search failed ({e}). Proceeding with zero results.")
        try:
            image_results = bing_image_search(cfg, query, max_results=limit)
        except Exception as e:
            print(f"[yellow]Warning:[/yellow] Bing image search failed ({e}). Proceeding with zero images.")
    elif p == "serpapi":
        from osint_tool.collectors.serpapi import serpapi_web_search, serpapi_image_search
        try:
            web_results = serpapi_web_search(cfg, query, max_results=limit)
        except Exception as e:
            print(f"[yellow]Warning:[/yellow] SerpAPI web search failed ({e}). Proceeding with zero results.")
        try:
            image_results = serpapi_image_search(cfg, query, max_results=limit)
        except Exception as e:
            print(f"[yellow]Warning:[/yellow] SerpAPI image search failed ({e}). Proceeding with zero images.")
    elif p == "brave":
        from osint_tool.collectors.brave import brave_web_search, brave_image_search
        try:
            web_results = brave_web_search(cfg, query, max_results=limit)
        except Exception as e:
            print(f"[yellow]Warning:[/yellow] Brave web search failed ({e}). Proceeding with zero results.")
        try:
            image_results = brave_image_search(cfg, query, max_results=limit)
        except Exception as e:
            print(f"[yellow]Warning:[/yellow] Brave image search failed ({e}). Proceeding with zero images.")
    else:
        try:
            web_results = search_web(query, max_results=limit)
        except Exception as e:
            print(f"[yellow]Warning:[/yellow] web search failed ({e}). Proceeding with zero results.")
        try:
            image_results = search_images(query, max_results=limit)
        except Exception as e:
            print(f"[yellow]Warning:[/yellow] image search failed ({e}). Proceeding with zero images.")

    links = [r.href for r in web_results if r.href]
    meta_out = cfg.data_dir / "raw" / subject / "metadata" / "search_results.jsonl"
    write_metadata_jsonl(to_dicts(web_results), meta_out)

    print(f"Saved {len(web_results)} web result metadata to {meta_out}")

    if save_images and image_results:
        images_dir = cfg.data_dir / "raw" / subject / "images"
        saved = download_images([i.__dict__ for i in image_results], images_dir, max_images=limit)
        img_meta_out = cfg.data_dir / "raw" / subject / "metadata" / "images.jsonl"
        write_metadata_jsonl([{
            "title": i.title,
            "url": i.url,
            "image": i.image,
            "thumbnail": i.thumbnail,
            "source": i.source,
        } for i in image_results], img_meta_out)
        print(f"Downloaded {len(saved)} images to {images_dir}")
    elif save_images:
        print("No images to download.")


@app.command("analyze")
def analyze(subject_a: str = typer.Option(..., help="Subject A ID"),
            subject_b: str = typer.Option(..., help="Subject B ID")):
    cfg = load_config()

    def _load_links(subject: str) -> List[str]:
        path = cfg.data_dir / "raw" / subject / "metadata" / "search_results.jsonl"
        if not path.exists():
            return []
        links: List[str] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    href = obj.get("href")
                    if href:
                        links.append(href)
                except Exception:
                    continue
        return links

    links_a = _load_links(subject_a)
    links_b = _load_links(subject_b)

    summary_a = summarize_subject(subject_a, links_a)
    summary_b = summarize_subject(subject_b, links_b)

    graph = build_overlap_graph(summary_a, summary_b)
    overlaps = graph_overlaps(graph)

    out_graph = cfg.data_dir / "processed" / "graphs" / f"{subject_a}_{subject_b}.graphml"
    export_graphml(graph, out_graph)

    # Save quick summary JSON for report
    processed_dir = cfg.data_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    summary_json = {
        "subject_a": {
            "total_links": len(summary_a.links),
            "top_domains": summary_a.domains.most_common(15),
            "links": summary_a.links,
        },
        "subject_b": {
            "total_links": len(summary_b.links),
            "top_domains": summary_b.domains.most_common(15),
            "links": summary_b.links,
        },
    }
    (processed_dir / f"summary_{subject_a}_{subject_b}.json").write_text(
        json.dumps(summary_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Overlaps (domains with both subjects present): {overlaps}")
    print(f"Graph exported to: {out_graph}")


@app.command("report")
def report(subject_a: str = typer.Option(..., help="Subject A ID"),
          subject_b: str = typer.Option(..., help="Subject B ID"),
          out: Path = typer.Option(..., help="Output markdown path, e.g., reports/case_001.md")):
    cfg = load_config()

    summary_path = cfg.data_dir / "processed" / f"summary_{subject_a}_{subject_b}.json"
    if not summary_path.exists():
        raise typer.BadParameter("Run analyze before report")

    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    # Compute overlaps from saved graph? Quick recompute from summaries
    domains_a = dict(summary["subject_a"]["top_domains"]) if isinstance(summary["subject_a"]["top_domains"], dict) else dict(summary["subject_a"]["top_domains"])
    domains_b = dict(summary["subject_b"]["top_domains"]) if isinstance(summary["subject_b"]["top_domains"], dict) else dict(summary["subject_b"]["top_domains"])
    overlaps = sorted(set(domains_a.keys()) & set(domains_b.keys()))

    from osint_tool.reporting.report import render_markdown_report
    templates_dir = Path(__file__).parent / "reporting" / "templates"

    out.parent.mkdir(parents=True, exist_ok=True)

    render_markdown_report(
        templates_dir=templates_dir,
        subject_a=subject_a,
        subject_b=subject_b,
        summary=summary,
        overlaps=overlaps,
        out_path=out,
    )

    print(f"Report written to {out}")


@app.command("face-search")
def face_search(subject: str = typer.Option(..., help="Subject ID to run face search on")):
    cfg = load_config()
    if not cfg.allow_facial_recognition:
        print("Facial recognition is disabled. Set ALLOW_FACIAL_RECOGNITION=true in .env and provide API keys.")
        raise typer.Exit(code=2)

    if not (cfg.facecheck_api_key or (cfg.azure_face_endpoint and cfg.azure_face_key)):
        print("No facial recognition provider configured. Set FACECHECK_API_KEY or AZURE_FACE_* in .env.")
        raise typer.Exit(code=2)

    print("Facial recognition step is intentionally not implemented in this scaffold.\n"
          "Integrate your authorized provider in a separate module under osint_tool/facial/ and ensure lawful, consented use.")


if __name__ == "__main__":
    app()