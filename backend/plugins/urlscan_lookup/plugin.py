"""urlscan.io — Domain/URL → public scan result URLs."""
from __future__ import annotations

import httpx

from plugins.base import PluginContext, TransformPlugin
from plugins.helpers import build_observation


def _host_from_value(value: str) -> str:
    v = value.strip()
    if "://" in v:
        v = v.split("://", 1)[-1]
    return v.split("/")[0].split(":")[0].lower()


class UrlscanLookupPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        raw = context.entity.label.strip()
        host = _host_from_value(raw)
        context.log(f"[urlscan] Search for {host}…")

        api_key = await context.api_manager.get_key_and_check_quota("urlscan")
        log: list[str] = []
        nodes: list[dict] = []
        edges: list[dict] = []
        observations: list[dict] = []

        headers = {"User-Agent": "OSINTGraph/1.0"}
        if api_key:
            headers["API-Key"] = api_key
        else:
            log.append("[urlscan] URLSCAN_API_KEY absente — quotas publics stricts.")

        query = f"domain:{host}" if host else f"page.url:{raw}"
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.get(
                    "https://urlscan.io/api/v1/search/",
                    params={"q": query, "size": 20},
                    headers=headers,
                )
                if res.status_code == 401:
                    log.append("[urlscan] Authentification requise — ajoutez URLSCAN_API_KEY.")
                    return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}
                if res.status_code != 200:
                    log.append(f"[urlscan] HTTP {res.status_code}")
                    return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}

                payload = res.json()
                results = payload.get("results") or []
                for item in results:
                    page = item.get("page") or {}
                    result_url = item.get("result") or ""
                    page_url = page.get("url") or result_url
                    if not page_url:
                        continue
                    label = page_url if len(page_url) <= 120 else page_url[:117] + "…"
                    nodes.append({
                        "type": "URL",
                        "label": label,
                        "properties": {
                            "source": "urlscan.io",
                            "scan_uuid": item.get("_id", ""),
                            "result": result_url,
                        },
                    })
                    edges.append({
                        "source": raw,
                        "target": label,
                        "type": "LINKED_TO",
                    })
                    observations.append(build_observation(
                        "urlscan.io",
                        {"field": "scan", "url": page_url, "domain": host},
                        confidence=0.8,
                        url=result_url or "https://urlscan.io/",
                    ))

                if api_key:
                    await context.api_manager.register_usage("urlscan")
                log.append(f"[urlscan] {len(nodes)} résultat(s) public(s)")
        except httpx.HTTPError as e:
            log.append(f"[urlscan] Erreur réseau: {type(e).__name__}")

        return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}
