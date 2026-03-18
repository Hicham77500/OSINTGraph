"""Shodan Transform — IP → Open Ports / Services"""
import os
import asyncio
from transforms.base import Transform, register


@register
class ShodanLookup(Transform):
    name = "shodan_lookup"
    display_name = "Shodan Lookup"
    input_type = "ip"
    output_type = "organization"
    description = "Discover open ports and services on an IP via Shodan"

    async def run(self, value: str, options: dict = {}) -> dict:
        log = [f"[Shodan] Looking up {value}..."]
        nodes = []
        api_key = os.getenv("SHODAN_API_KEY", "")

        if not api_key:
            log.append("[Shodan] Warning: no SHODAN_API_KEY — using demo data")
            demo_ports = [80, 443, 22]
            for port in demo_ports:
                nodes.append({
                    "type": "organization",
                    "label": f"{value}:{port}",
                    "properties": {"port": str(port), "ip": value, "source": "shodan_demo"},
                })
            return {"nodes": nodes, "edges": [], "log": log}

        try:
            import shodan
            api = shodan.Shodan(api_key)
            host = await asyncio.to_thread(api.host, value)

            if host.get("org"):
                nodes.append({
                    "type": "organization",
                    "label": host["org"],
                    "properties": {"asn": host.get("asn", ""), "isp": host.get("isp", ""), "source": "shodan"},
                })
                log.append(f"[Shodan] Org: {host['org']}")

            for service in host.get("data", [])[:10]:
                port_label = f"{value}:{service['port']}/{service.get('transport','tcp')}"
                nodes.append({
                    "type": "ip",
                    "label": port_label,
                    "properties": {
                        "port": str(service["port"]),
                        "banner": str(service.get("data", ""))[:200],
                        "product": service.get("product", ""),
                        "source": "shodan",
                    },
                })
                log.append(f"[Shodan] Port: {service['port']} ({service.get('product','')})")

        except Exception as e:
            log.append(f"[Shodan] Error: {e}")

        log.append(f"[Shodan] Done — {len(nodes)} entities found")
        return {"nodes": nodes, "edges": [], "log": log}
