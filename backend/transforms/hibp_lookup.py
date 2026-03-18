"""HaveIBeenPwned Transform — Email → Breach Data"""
import httpx
import os
from transforms.base import Transform, register


@register
class HIBPLookup(Transform):
    name = "hibp_lookup"
    display_name = "HaveIBeenPwned"
    input_type = "email"
    output_type = "domain"
    description = "Check if email appears in known breach databases"

    async def run(self, value: str, options: dict = {}) -> dict:
        log = [f"[HIBP] Checking {value}..."]
        nodes = []
        api_key = os.getenv("HIBP_API_KEY", "")

        if not api_key:
            log.append("[HIBP] Warning: no HIBP_API_KEY set — using demo mode")
            # Demo fallback
            nodes.append({
                "type": "domain",
                "label": "example-breach.com",
                "properties": {"breach_name": "ExampleBreach", "source": "hibp_demo", "email": value}
            })
            return {"nodes": nodes, "edges": [], "log": log}

        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(
                    f"https://haveibeenpwned.com/api/v3/breachedaccount/{value}",
                    headers={"hibp-api-key": api_key, "user-agent": "OSINTGraph/0.1"},
                    params={"truncateResponse": "false"},
                )
                if res.status_code == 200:
                    breaches = res.json()
                    for b in breaches:
                        nodes.append({
                            "type": "domain",
                            "label": b.get("Domain", b.get("Name", "unknown")),
                            "properties": {
                                "breach_name": b.get("Name", ""),
                                "breach_date": b.get("BreachDate", ""),
                                "pwn_count": str(b.get("PwnCount", 0)),
                                "source": "hibp",
                                "email": value,
                            }
                        })
                        log.append(f"[HIBP] Breach: {b.get('Name')}")
                elif res.status_code == 404:
                    log.append("[HIBP] No breaches found for this email ✓")
                else:
                    log.append(f"[HIBP] API returned {res.status_code}")
        except Exception as e:
            log.append(f"[HIBP] Error: {e}")

        log.append(f"[HIBP] Done — {len(nodes)} breaches found")
        return {"nodes": nodes, "edges": [], "log": log}
