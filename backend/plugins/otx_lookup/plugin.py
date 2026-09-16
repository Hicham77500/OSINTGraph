"""AlienVault OTX — Domain or IP → pulse / indicator context."""
from __future__ import annotations

import ipaddress
import httpx

from plugins.base import PluginContext, TransformPlugin
from plugins.helpers import build_observation


def _otx_section(value: str) -> tuple[str, str]:
    v = value.strip()
    try:
        ipaddress.ip_address(v)
        return "IPv4", v
    except ValueError:
        host = v.lower().split("://")[-1].split("/")[0].split(":")[0]
        return "domain", host


class OtxLookupPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        value = context.entity.label.strip()
        section, id_value = _otx_section(value)
        context.log(f"[OTX] Indicator {section}/{id_value}…")

        api_key = await context.api_manager.get_key_and_check_quota("otx")
        log: list[str] = []
        nodes: list[dict] = []
        edges: list[dict] = []
        observations: list[dict] = []

        if not api_key:
            log.append("[OTX] OTX_API_KEY manquante (compte gratuit otx.alienvault.com).")
            return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}

        headers = {"X-OTX-API-KEY": api_key, "User-Agent": "OSINTGraph/1.0"}
        base = f"https://otx.alienvault.com/api/v1/indicators/{section}/{id_value}"

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                general = await client.get(f"{base}/general", headers=headers)
                if general.status_code != 200:
                    log.append(f"[OTX] general HTTP {general.status_code}")
                    return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}

                g = general.json()
                pulse_count = int(g.get("pulse_info", {}).get("count") or 0)
                observations.append(build_observation(
                    "otx",
                    {"field": "pulse_count", "value": pulse_count, "indicator": id_value},
                    confidence=0.8 if pulse_count else 0.5,
                    status="LIKELY" if pulse_count else "UNVERIFIED",
                    url=f"https://otx.alienvault.com/indicator/{section}/{id_value}",
                ))
                log.append(f"[OTX] {pulse_count} pulse(s) public(s)")

                pulses = await client.get(f"{base}/pulses", headers=headers, params={"limit": 10})
                if pulses.status_code == 200:
                    for pulse in (pulses.json().get("results") or []):
                        name = pulse.get("name") or "OTX pulse"
                        label = name if len(name) <= 80 else name[:77] + "…"
                        nodes.append({
                            "type": "DOMAIN",
                            "label": label,
                            "properties": {
                                "source": "otx",
                                "pulse_id": pulse.get("id", ""),
                                "indicator": id_value,
                            },
                        })
                        edges.append({
                            "source": value,
                            "target": label,
                            "type": "LINKED_TO",
                        })

                await context.api_manager.register_usage("otx")
                log.append(f"[OTX] {len(nodes)} pulse(s) listé(s)")
        except httpx.HTTPError as e:
            log.append(f"[OTX] Erreur réseau: {type(e).__name__}")

        return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}
