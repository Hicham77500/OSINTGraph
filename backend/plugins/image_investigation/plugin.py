"""Image → official reverse-search assistant links (no fake hits)."""
from __future__ import annotations

import os
import re

from plugins.base import PluginContext, TransformPlugin
from plugins.helpers import build_observation
from services.investigation_assets import get_asset_path
from services.visual_search import build_search_assistants


def _resolve_public_url(label: str, api_base: str | None) -> str | None:
    label = label.strip()
    if label.startswith("http://") or label.startswith("https://"):
        return label
    if re.fullmatch(r"[a-f0-9]{32}", label) and api_base:
        if get_asset_path(label):
            return f"{api_base.rstrip('/')}/api/v1/investigation/assets/{label}"
    return None


class ImageInvestigationPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        label = context.entity.label.strip()
        context.log("[Visual] Preparing search assistants…")

        api_base = os.getenv("OSINTGRAPH_PUBLIC_API_URL", "").strip() or None
        public_url = _resolve_public_url(label, api_base)
        assistants = build_search_assistants(public_url)

        nodes: list[dict] = []
        edges: list[dict] = []
        observations: list[dict] = []
        log: list[str] = []

        for item in assistants:
            name = item["name"]
            url = item["url"]
            nodes.append({
                "type": "URL",
                "label": name,
                "properties": {
                    "url": url,
                    "source": "visual_search",
                    "method": item.get("method", "MANUAL"),
                    "asset": label,
                },
            })
            edges.append({"source": label, "target": name, "type": "LINKED_TO"})
            observations.append(build_observation(
                item["id"],
                {
                    "field": "search_assistant",
                    "name": name,
                    "url": url,
                    "hint": item.get("hint", ""),
                    "image_ref": label,
                },
                collection_method=item.get("method", "MANUAL"),
                confidence=0.5,
                status="UNVERIFIED",
                url=url,
            ))
            log.append(f"[Visual] {name}")

        if not public_url:
            log.append("[Visual] Tip: set OSINTGRAPH_PUBLIC_API_URL for URL-based Google/Bing/Yandex links.")

        log.append(f"[Visual] {len(nodes)} assistant link(s) — open manually and record findings.")
        return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}
