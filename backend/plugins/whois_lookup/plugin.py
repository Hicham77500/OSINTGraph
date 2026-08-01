"""Whois Lookup — Domain → registrant / org / emails."""
import asyncio

import whois

from plugins.base import PluginContext, TransformPlugin
from plugins.helpers import build_observation


class WhoisLookupPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        value = context.entity.label.strip()
        context.log(f"[Whois] Querying {value}...")

        nodes: list[dict] = []
        edges: list[dict] = []
        observations: list[dict] = []
        log: list[str] = []

        try:
            result = await asyncio.to_thread(whois.whois, value)

            registrant = result.get("registrant_name") or result.get("name")
            if registrant and isinstance(registrant, str):
                nodes.append({
                    "type": "PERSON",
                    "label": registrant,
                    "properties": {"role": "registrant", "domain": value, "source": "whois"},
                })
                edges.append({"source": value, "target": registrant, "type": "OWNS"})
                observations.append(build_observation(
                    "whois", {"field": "registrant", "value": registrant}, confidence=0.6
                ))
                log.append("[Whois] Registrant found")

            org = result.get("org") or result.get("registrant_org")
            if org and isinstance(org, str):
                nodes.append({
                    "type": "ORGANIZATION",
                    "label": org,
                    "properties": {"source": "whois", "domain": value},
                })
                edges.append({"source": value, "target": org, "type": "LINKED_TO"})
                observations.append(build_observation(
                    "whois", {"field": "organization", "value": org}, confidence=0.7
                ))
                log.append("[Whois] Organization found")

            emails = result.get("emails") or []
            if isinstance(emails, str):
                emails = [emails]
            for email in sorted(set(e for e in emails if isinstance(e, str) and "@" in e)):
                nodes.append({
                    "type": "EMAIL",
                    "label": email,
                    "properties": {"source": "whois", "domain": value},
                })
                edges.append({"source": value, "target": email, "type": "LINKED_TO"})
                observations.append(build_observation(
                    "whois", {"field": "email", "value": email}, confidence=0.65
                ))
                log.append("[Whois] Email found")

            log.append(f"[Whois] Done — {len(nodes)} entit(y/ies) found")
        except Exception as e:
            log.append(f"[Whois] Error: {type(e).__name__}")

        return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}
