"""Have I Been Pwned — Email → breach domains (official API v3, no demo data)."""
from __future__ import annotations

import httpx

from plugins.base import PluginContext, TransformPlugin
from plugins.helpers import build_observation


class HIBPLookupPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        value = context.entity.label.strip().lower()
        context.log(f"[HIBP] Checking breach disclosures for email…")

        api_key = await context.api_manager.get_key_and_check_quota("hibp")
        log: list[str] = []
        nodes: list[dict] = []
        edges: list[dict] = []
        observations: list[dict] = []

        if not api_key:
            log.append("[HIBP] HIBP_API_KEY manquante — configurez la clé API officielle.")
            return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.get(
                    f"https://haveibeenpwned.com/api/v3/breachedaccount/{value}",
                    headers={
                        "hibp-api-key": api_key,
                        "user-agent": "OSINTGraph/1.0",
                    },
                    params={"truncateResponse": "false"},
                )
                if res.status_code == 200:
                    breaches = res.json()
                    for b in breaches:
                        domain_label = b.get("Domain") or b.get("Name") or "unknown"
                        nodes.append({
                            "type": "DOMAIN",
                            "label": domain_label,
                            "properties": {
                                "breach_name": b.get("Name", ""),
                                "breach_date": b.get("BreachDate", ""),
                                "source": "hibp",
                            },
                        })
                        edges.append({
                            "source": value,
                            "target": domain_label,
                            "type": "LINKED_TO",
                        })
                        observations.append(build_observation(
                            "hibp",
                            {
                                "field": "breach",
                                "breach_name": b.get("Name", ""),
                                "breach_date": b.get("BreachDate", ""),
                                "domain": domain_label,
                            },
                            confidence=0.85,
                            status="LIKELY",
                            url="https://haveibeenpwned.com/",
                        ))
                        log.append(f"[HIBP] Breach: {b.get('Name')}")
                elif res.status_code == 404:
                    log.append("[HIBP] Aucune violation publique référencée pour cet e-mail.")
                else:
                    log.append(f"[HIBP] API HTTP {res.status_code}")
            await context.api_manager.register_usage("hibp")
        except httpx.HTTPError as e:
            log.append(f"[HIBP] Erreur réseau: {type(e).__name__}")

        log.append(f"[HIBP] Terminé — {len(nodes)} entrée(s)")
        return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}
