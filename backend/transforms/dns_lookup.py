"""DNS Lookup Transform — Domain → IP"""
import dns.resolver
from transforms.base import Transform, register, build_observation


@register
class DNSLookup(Transform):
    name = "dns_lookup"
    display_name = "DNS Lookup"
    input_type = "domain"
    output_type = "ip"
    description = "Resolve domain to IP addresses via DNS"
    platform = "dns"

    async def run(self, value: str, options: dict | None = None) -> dict:
        log = ["[DNS] Resolving domain..."]
        nodes = []
        observations = []
        try:
            answers = dns.resolver.resolve(value, "A")
            for rdata in answers:
                ip = str(rdata)
                nodes.append({"type": "ip", "label": ip, "properties": {"source": "dns", "domain": value}})
                observations.append(
                    build_observation("dns", {"field": "ip", "value": ip, "record": "A"}, confidence=0.9)
                )
                log.append(f"[DNS] Found A record")

            try:
                answers6 = dns.resolver.resolve(value, "AAAA")
                for rdata in answers6:
                    ip6 = str(rdata)
                    nodes.append({"type": "ip", "label": ip6, "properties": {"source": "dns", "record": "AAAA"}})
                    observations.append(
                        build_observation("dns", {"field": "ip", "value": ip6, "record": "AAAA"}, confidence=0.9)
                    )
                    log.append("[DNS] Found AAAA record")
            except Exception:
                pass

        except Exception as e:
            log.append(f"[DNS] Error: {type(e).__name__}")

        log.append(f"[DNS] Done — {len(nodes)} records found")
        return {"nodes": nodes, "edges": [], "observations": observations, "log": log}
