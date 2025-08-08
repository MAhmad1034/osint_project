from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any, Tuple
import json
from .config import AppConfig, SubjectConfig
from .utils import get_logger, ensure_dir, download_file
from .image_store import ImageStore, StoredImage
from .scrapers.web_search import duckduckgo_image_search
from .scrapers.instagram_public import fetch_public_profile
from .face.azure_face import AzureFaceClient
from .graph.graph_builder import GraphBuilder
from .report.report_builder import ReportBuilder, ReportImage


logger = get_logger("pipeline")


class Pipeline:
    def __init__(self, config: AppConfig):
        self.config = config
        self.store = ImageStore(base_dir=self.config.storage.base_dir)
        self.graph = GraphBuilder()

        self.face_client = None
        if self.config.face.provider == "azure" and self.config.face.azure_endpoint and self.config.face.azure_key:
            self.face_client = AzureFaceClient(self.config.face.azure_endpoint, self.config.face.azure_key)

    def _collect_duckduckgo_images(self, subject: SubjectConfig) -> List[StoredImage]:
        images: List[StoredImage] = []
        queries = list(subject.names) + list(subject.usernames)
        for q in queries:
            results = duckduckgo_image_search(q, max_results=self.config.search.image_results_per_query)
            for r in results:
                url = r.get("image")
                title = r.get("title")
                if not url:
                    continue
                filename_hint = f"{q}_{Path(url).name[:50]}"
                try:
                    image_bytes = self._download_bytes(url)
                    si = self.store.save_image(subject.id, image_bytes, filename_hint, source_url=r.get("source") or url, title=title, extra_meta={"query": q, "scraper": "ddg"})
                    if si:
                        images.append(si)
                except Exception:
                    continue
        return images

    def _download_bytes(self, url: str) -> bytes:
        # Use temp path then read back to bytes (reuse existing util)
        tmp = ensure_dir(Path(self.config.storage.base_dir) / "tmp") / Path(url).name
        try:
            download_file(url, str(tmp))
            data = Path(tmp).read_bytes()
            return data
        finally:
            try:
                tmp.unlink(missing_ok=True)  # type: ignore[attr-defined]
            except Exception:
                pass

    def _collect_instagram(self, subject: SubjectConfig) -> Dict[str, Any]:
        meta = {}
        for handle in subject.usernames:
            m = fetch_public_profile(handle, str(ensure_dir(Path(self.config.storage.base_dir) / "instagram")))
            meta[handle] = m
        return meta

    def _pick_reference_face_id(self, subject_images: List[StoredImage]) -> str | None:
        if not self.face_client:
            return None
        for si in subject_images:
            fid = self.face_client.best_face_id(str(si.path))
            if fid:
                return fid
        return None

    def _verify_images(self, subject_id: str, reference_face_id: str | None, images: List[StoredImage]) -> List[Tuple[StoredImage, bool, float]]:
        results: List[Tuple[StoredImage, bool, float]] = []
        for si in images:
            is_match = False
            score = 0.0
            if reference_face_id and self.face_client:
                match, conf = self.face_client.verify_image_against_reference(str(si.path), reference_face_id)
                is_match = bool(match) or conf >= self.config.face.confidence_threshold
                score = conf
            results.append((si, is_match, score))
        return results

    def run(self, output_dir: str) -> Dict[str, Any]:
        ensure_dir(output_dir)

        all_results: Dict[str, Any] = {"subjects": [], "images": []}
        platforms = set(self.config.search.platforms or [])

        for subject in self.config.subjects:
            logger.info("Collecting for subject %s", subject.id)
            self.graph.add_subject(subject.id, label=", ".join(subject.names) or subject.id)

            ddg_images: List[StoredImage] = []
            insta_meta: Dict[str, Any] = {}

            if "duckduckgo_images" in platforms:
                ddg_images = self._collect_duckduckgo_images(subject)
            if "instagram_public" in platforms:
                insta_meta = self._collect_instagram(subject)

            ref_face_id = self._pick_reference_face_id(ddg_images) if ddg_images else None
            verified = self._verify_images(subject.id, ref_face_id, ddg_images) if ddg_images else []

            subject_record = {
                "id": subject.id,
                "names": subject.names,
                "usernames": subject.usernames,
                "instagram": insta_meta,
                "reference_face_available": bool(ref_face_id),
            }
            all_results["subjects"].append(subject_record)

            for si, is_match, conf in verified:
                self.graph.add_image(subject.id, str(si.path), si.source_url, is_match=is_match, confidence=conf)
                all_results["images"].append({
                    "subject_id": subject.id,
                    "path": str(si.path),
                    "source_url": si.source_url,
                    "title": si.title,
                    "is_match": is_match,
                    "confidence": conf,
                })

        # Export graph
        graphml_path = str(Path(output_dir) / "graph.graphml")
        self.graph.export_graphml(graphml_path)

        # Build report
        report_images = [
            ReportImage(
                subject_id=im["subject_id"], path=im["path"], source_url=im["source_url"], is_match=im["is_match"], confidence=im["confidence"], title=im.get("title")
            ) for im in all_results["images"]
        ]
        rb = ReportBuilder(templates_dir=str(Path(__file__).parent / "report" / "templates"))
        html_path = str(Path(output_dir) / "report.html")
        rb.build(self.config.report.title, all_results["subjects"], report_images, html_path)

        # Save json
        Path(Path(output_dir) / "results.json").write_text(json.dumps(all_results, indent=2), encoding="utf-8")

        logger.info("Done. Report at %s, GraphML at %s", html_path, graphml_path)
        return {"report": html_path, "graphml": graphml_path, "json": str(Path(output_dir) / "results.json")}