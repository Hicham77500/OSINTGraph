"""DNS Lookup Transform — Domain → IP"""
import dns.resolver
from transforms.base import Transform, register


@register
class DNSLookup(Transform):
    name = "dns_lookup"
    display_name = "DNS Lookup"
    input_type = "domain"
    output_type = "ip"
    description = "Resolve domain to IP addresses via DNS"

    async def run(self, value: str, options: dict = {}) -> dict:
        log = [f"[DNS] Resolving {value}..."]
        nodes = []
        try:
            answers = dns.resolver.resolve(value, "A")
            for rdata in answers:
                ip = str(rdata)
                nodes.append({"type": "ip", "label": ip, "properties": {"source": "dns", "domain": value}})
                log.append(f"[DNS] Found A record: {ip}")

            # Try AAAA
            try:
                answers6 = dns.resolver.resolve(value, "AAAA")
                for rdata in answers6:
                    ip6 = str(rdata)
                    nodes.append({"type": "ip", "label": ip6, "properties": {"source": "dns", "record": "AAAA"}})
                    log.append(f"[DNS] Found AAAA record: {ip6}")
            except Exception:
                pass

        except Exception as e:
            log.append(f"[DNS] Error: {e}")

        log.append(f"[DNS] Done — {len(nodes)} records found")
        return {"nodes": nodes, "edges": [], "log": log}
