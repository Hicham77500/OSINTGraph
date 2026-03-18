"""Whois Lookup Transform — Domain → Person / Organization"""
import asyncio
import whois
from transforms.base import Transform, register


@register
class WhoisLookup(Transform):
    name = "whois_lookup"
    display_name = "Whois Lookup"
    input_type = "domain"
    output_type = "organization"
    description = "Retrieve Whois registration data for a domain"

    async def run(self, value: str, options: dict = {}) -> dict:
        log = [f"[Whois] Querying {value}..."]
        nodes = []
        try:
            result = await asyncio.to_thread(whois.whois, value)

            if result.get("registrant_name") or result.get("name"):
                name = result.get("registrant_name") or result.get("name")
                nodes.append({
                    "type": "person",
                    "label": name,
                    "properties": {"role": "registrant", "domain": value, "source": "whois"},
                })
                log.append(f"[Whois] Registrant: {name}")

            if result.get("org") or result.get("registrant_org"):
                org = result.get("org") or result.get("registrant_org")
                nodes.append({
                    "type": "organization",
                    "label": org,
                    "properties": {"source": "whois", "domain": value},
                })
                log.append(f"[Whois] Organization: {org}")

            if result.get("emails"):
                emails = result["emails"]
                if isinstance(emails, str):
                    emails = [emails]
                for email in set(emails):
                    nodes.append({
                        "type": "email",
                        "label": email,
                        "properties": {"source": "whois", "domain": value},
                    })
                    log.append(f"[Whois] Email: {email}")

        except Exception as e:
            log.append(f"[Whois] Error: {e}")

        log.append(f"[Whois] Done — {len(nodes)} entities found")
        return {"nodes": nodes, "edges": [], "log": log}
