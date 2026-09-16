"""Place name → coordinates via OpenStreetMap Nominatim (official public API)."""
from __future__ import annotations

import httpx

from plugins.base import PluginContext, TransformPlugin
from plugins.helpers import build_observation


class NominatimGeocodePlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        query = (context.config.get("place_query") or context.entity.label).strip()
        context.log(f"[Nominatim] Geocoding {query}…")

        nodes: list[dict] = []
        edges: list[dict] = []
        observations: list[dict] = []
        log: list[str] = []

        headers = {
            "User-Agent": "OSINTGraph/1.0 (OSINT investigation; contact: local-analyst)",
            "Accept-Language": "fr,en",
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": query, "format": "json", "limit": 5},
                    headers=headers,
                )
                if res.status_code != 200:
                    log.append(f"[Nominatim] HTTP {res.status_code}")
                    return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}

                results = res.json()
                if not results:
                    log.append("[Nominatim] No public match — refine place name.")
                    return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}

                for hit in results[:3]:
                    display = hit.get("display_name") or query
                    label = display if len(display) <= 100 else display[:97] + "…"
                    lat = hit.get("lat")
                    lon = hit.get("lon")
                    nodes.append({
                        "type": "LOCATION",
                        "label": label,
                        "properties": {
                            "source": "nominatim",
                            "lat": str(lat or ""),
                            "lon": str(lon or ""),
                            "osm_type": hit.get("type", ""),
                            "class": hit.get("class", ""),
                        },
                    })
                    edges.append({
                        "source": context.entity.label,
                        "target": label,
                        "type": "LINKED_TO",
                    })
                    observations.append(build_observation(
                        "openstreetmap",
                        {
                            "field": "geocode",
                            "query": query,
                            "display_name": display,
                            "lat": lat,
                            "lon": lon,
                            "importance": hit.get("importance"),
                        },
                        collection_method="OFFICIAL_API",
                        confidence=0.7,
                        status="UNVERIFIED",
                        url="https://nominatim.openstreetmap.org/",
                    ))
                    log.append(f"[Nominatim] Match: {label}")

        except httpx.HTTPError as e:
            log.append(f"[Nominatim] Network error: {type(e).__name__}")

        log.append(f"[Nominatim] Done — {len(nodes)} candidate location(s)")
        return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}
