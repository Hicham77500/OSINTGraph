"""DNS Lookup — Domain → IP addresses."""
import asyncio

import dns.resolver

from plugins.base import PluginContext, TransformPlugin
from plugins.helpers import build_observation


class DNSLookupPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        value = context.entity.label.strip()
        context.log(f"[DNS] Resolving {value}...")

        nodes: list[dict] = []
        edges: list[dict] = []
        observations: list[dict] = []
        log: list[str] = []

        async def _resolve(record_type: str):
            try:
                answers = await asyncio.to_thread(dns.resolver.resolve, value, record_type)
                return [str(rdata) for rdata in answers]
            except Exception:
                return []

        try:
            for record_type in ("A", "AAAA"):
                for ip in await _resolve(record_type):
                    nodes.append({
                        "type": "IP",
                        "label": ip,
                        "properties": {"source": "dns", "domain": value, "record": record_type},
                    })
                    edges.append({
                        "source": value,
                        "target": ip,
                        "type": "RESOLVES_TO",
                    })
                    observations.append(build_observation(
                        "dns",
                        {"field": "ip", "value": ip, "record": record_type, "domain": value},
                        confidence=0.9,
                    ))
                    log.append(f"[DNS] Found {record_type} record")

            log.append(f"[DNS] Done — {len(nodes)} record(s) found")
        except Exception as e:
            log.append(f"[DNS] Error: {type(e).__name__}")

        return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}
