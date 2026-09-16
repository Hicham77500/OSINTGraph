"""VirusTotal v3 — Domain or IP → related indicators and metadata."""
from __future__ import annotations

import ipaddress
import httpx

from plugins.base import PluginContext, TransformPlugin
from plugins.helpers import build_observation


def _indicator_kind(value: str) -> tuple[str, str]:
    v = value.strip()
    try:
        ipaddress.ip_address(v)
        return "ip_addresses", v
    except ValueError:
        host = v.lower()
        if host.startswith("http://") or host.startswith("https://"):
            host = host.split("://", 1)[-1]
        host = host.split("/")[0].split(":")[0]
        return "domains", host


class VirusTotalLookupPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        value = context.entity.label.strip()
        kind, id_value = _indicator_kind(value)
        context.log(f"[VirusTotal] Lookup {kind} {id_value}…")

        api_key = await context.api_manager.get_key_and_check_quota("virustotal")
        log: list[str] = []
        nodes: list[dict] = []
        edges: list[dict] = []
        observations: list[dict] = []

        if not api_key:
            log.append("[VirusTotal] VIRUSTOTAL_API_KEY manquante.")
            return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}

        url = f"https://www.virustotal.com/api/v3/{kind}/{id_value}"
        headers = {"x-apikey": api_key, "User-Agent": "OSINTGraph/1.0"}

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 404:
                    log.append("[VirusTotal] Indicateur inconnu dans VT.")
                    return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}
                if res.status_code != 200:
                    log.append(f"[VirusTotal] HTTP {res.status_code}")
                    return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}

                body = res.json()
                attrs = (body.get("data") or {}).get("attributes") or {}
                stats = attrs.get("last_analysis_stats") or {}
                malicious = int(stats.get("malicious") or 0)
                observations.append(build_observation(
                    "virustotal",
                    {
                        "field": "reputation",
                        "malicious_votes": malicious,
                        "indicator": id_value,
                        "kind": kind,
                    },
                    confidence=0.85 if malicious else 0.6,
                    status="LIKELY" if malicious else "UNVERIFIED",
                    url=f"https://www.virustotal.com/gui/{kind.replace('_', '-')}/{id_value}",
                ))
                log.append(f"[VirusTotal] malicious votes: {malicious}")

                relations_url = f"{url}/relations"
                rel_res = await client.get(
                    relations_url,
                    headers=headers,
                    params={"limit": 15},
                )
                if rel_res.status_code == 200:
                    rel_body = rel_res.json()
                    for item in rel_body.get("data") or []:
                        rel_type = item.get("type") or ""
                        rel_id = item.get("id") or ""
                        if not rel_id:
                            continue
                        node_type = "IP" if "ip" in rel_type else "DOMAIN"
                        if rel_type.endswith("urls"):
                            continue
                        nodes.append({
                            "type": node_type,
                            "label": rel_id,
                            "properties": {"source": "virustotal", "relation": rel_type},
                        })
                        edges.append({
                            "source": value,
                            "target": rel_id,
                            "type": "LINKED_TO",
                        })

                await context.api_manager.register_usage("virustotal")
                log.append(f"[VirusTotal] {len(nodes)} relation(s) extraite(s)")
        except httpx.HTTPError as e:
            log.append(f"[VirusTotal] Erreur réseau: {type(e).__name__}")

        return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}
