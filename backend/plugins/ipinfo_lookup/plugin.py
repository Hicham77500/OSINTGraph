"""IPinfo — IP → org and location metadata."""
from __future__ import annotations

import httpx

from plugins.base import PluginContext, TransformPlugin
from plugins.helpers import build_observation


class IpinfoLookupPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        ip = context.entity.label.strip()
        context.log(f"[IPinfo] Lookup {ip}…")

        token = await context.api_manager.get_key_and_check_quota("ipinfo")
        log: list[str] = []
        nodes: list[dict] = []
        edges: list[dict] = []
        observations: list[dict] = []

        url = f"https://ipinfo.io/{ip}/json"
        params = {"token": token} if token else {}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.get(url, params=params, headers={"User-Agent": "OSINTGraph/1.0"})
                if res.status_code != 200:
                    log.append(f"[IPinfo] HTTP {res.status_code}")
                    return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}

                data = res.json()
                org = data.get("org")
                if org:
                    nodes.append({
                        "type": "ORGANIZATION",
                        "label": org,
                        "properties": {"source": "ipinfo", "asn": data.get("org", "")},
                    })
                    edges.append({"source": ip, "target": org, "type": "LINKED_TO"})

                loc = data.get("city") or data.get("region") or data.get("country")
                if loc:
                    parts = [p for p in (data.get("city"), data.get("region"), data.get("country")) if p]
                    label = ", ".join(parts)
                    nodes.append({
                        "type": "LOCATION",
                        "label": label,
                        "properties": {"source": "ipinfo", "loc": data.get("loc", "")},
                    })
                    edges.append({"source": ip, "target": label, "type": "LINKED_TO"})

                observations.append(build_observation(
                    "ipinfo",
                    {
                        "field": "network",
                        "org": org,
                        "city": data.get("city"),
                        "country": data.get("country"),
                    },
                    confidence=0.75,
                    url="https://ipinfo.io/",
                ))
                if token:
                    await context.api_manager.register_usage("ipinfo")
                log.append(f"[IPinfo] {len(nodes)} nœud(s)")
        except httpx.HTTPError as e:
            log.append(f"[IPinfo] Erreur réseau: {type(e).__name__}")

        return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}
