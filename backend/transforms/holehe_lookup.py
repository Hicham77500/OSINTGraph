"""Holehe Lookup Transform — Email → Registered Accounts (120+ services)"""
import asyncio
from transforms.base import Transform, register


@register
class HoleheLookup(Transform):
    name = "holehe_lookup"
    display_name = "Holehe — Email Accounts"
    input_type = "email"
    output_type = "username"
    description = "Find accounts registered with this email across 120+ services (holehe)"

    async def run(self, value: str, options: dict = {}) -> dict:
        log = [f"[Holehe] Checking email '{value}' across 120+ services..."]
        nodes = []
        edges = []

        try:
            import httpx
            from holehe.core import get_functions, import_submodules
            import holehe.modules as holehe_modules

            modules = import_submodules(holehe_modules)
            functions = get_functions(modules)

            log.append(f"[Holehe] Testing {len(functions)} services...")

            # Run all checks concurrently with a shared httpx client
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(10.0),
                follow_redirects=True,
            ) as client:

                async def _check(fn):
                    out: list[dict] = []
                    try:
                        await fn(value, client, out)
                    except Exception:
                        pass
                    return out

                # Batch concurrency to avoid overwhelming the network
                batch_size = options.get("batch_size", 30)
                all_results: list[dict] = []
                for i in range(0, len(functions), batch_size):
                    batch = functions[i : i + batch_size]
                    batch_out = await asyncio.gather(*[_check(fn) for fn in batch])
                    for r_list in batch_out:
                        all_results.extend(r_list)

            # Parse results
            for result in all_results:
                if result.get("exists"):
                    site_name = result.get("name", "unknown")
                    domain    = result.get("domain", "")
                    others    = result.get("others") or {}

                    props: dict = {
                        "platform":  site_name,
                        "domain":    domain,
                        "source":    "holehe",
                        "email":     value,
                    }
                    if result.get("emailrecovery"):
                        props["email_recovery"] = result["emailrecovery"]
                    if result.get("phoneNumber"):
                        props["phone"] = result["phoneNumber"]
                    if others:
                        for k, v in others.items():
                            props[f"extra_{k}"] = str(v)

                    nodes.append({
                        "type":  "username",
                        "label": f"[{site_name}] {value}",
                        "properties": props,
                    })
                    log.append(f"[+] {site_name} ({domain}): account found")
                elif result.get("rateLimit"):
                    log.append(f"[~] {result.get('name', '?')}: rate-limited")

            log.append(f"[Holehe] Done — {len(nodes)} account(s) found")

        except ImportError as e:
            log.append(f"[Holehe] ERROR: missing dependency — {e}")
            log.append("  Run: pip install holehe httpx")
        except Exception as e:
            log.append(f"[Holehe] ERROR: {e}")

        return {"nodes": nodes, "edges": edges, "log": log}
