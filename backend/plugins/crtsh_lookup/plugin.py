"""crt.sh — Domain → subdomains via public Certificate Transparency search."""
from __future__ import annotations

import httpx

from plugins.base import PluginContext, TransformPlugin
from plugins.helpers import build_observation


def _normalize_domain(value: str) -> str:
    v = value.strip().lower()
    if v.startswith("http://") or v.startswith("https://"):
        v = v.split("://", 1)[-1]
    return v.split("/")[0].split(":")[0]


class CrtShLookupPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        domain = _normalize_domain(context.entity.label)
        context.log(f"[crt.sh] CT search for {domain}…")

        log: list[str] = []
        nodes: list[dict] = []
        edges: list[dict] = []
        observations: list[dict] = []
        seen: set[str] = set()

        url = "https://crt.sh/"
        params = {"q": f"%.{domain}", "output": "json"}

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.get(url, params=params)
                if res.status_code != 200:
                    log.append(f"[crt.sh] HTTP {res.status_code}")
                    return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}

                rows = res.json()
                if not isinstance(rows, list):
                    log.append("[crt.sh] Réponse inattendue")
                    return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}

                for row in rows:
                    name_value = row.get("name_value") or ""
                    for part in name_value.split("\n"):
                        sub = part.strip().lower().lstrip("*.")
                        if not sub or sub == domain or not sub.endswith(domain):
                            continue
                        if sub in seen:
                            continue
                        seen.add(sub)
                        nodes.append({
                            "type": "DOMAIN",
                            "label": sub,
                            "properties": {"source": "crt.sh", "parent_domain": domain},
                        })
                        edges.append({
                            "source": domain,
                            "target": sub,
                            "type": "OWNS",
                        })
                        observations.append(build_observation(
                            "crt.sh",
                            {"field": "subdomain", "value": sub, "domain": domain},
                            confidence=0.75,
                            url=f"https://crt.sh/?q={domain}",
                        ))

                log.append(f"[crt.sh] {len(nodes)} sous-domaine(s) unique(s)")
        except httpx.HTTPError as e:
            log.append(f"[crt.sh] Erreur réseau: {type(e).__name__}")

        return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}
