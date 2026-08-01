"""Holehe Lookup — Email → registered accounts (inspired by knwldgbox)."""
import asyncio

import httpx

from plugins.base import PluginContext, TransformPlugin
from plugins.helpers import build_observation


class HoleheLookupPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        value = context.entity.label.strip().lower()
        context.log(f"[Holehe] Checking email across 120+ services...")

        nodes: list[dict] = []
        edges: list[dict] = []
        observations: list[dict] = []
        log: list[str] = []

        try:
            from holehe.core import get_functions, import_submodules
            import holehe.modules as holehe_modules

            modules = import_submodules(holehe_modules)
            functions = get_functions(modules)
            total = len(functions)
            log.append(f"[Holehe] Testing {total} services...")
            context.report_progress(f"[Holehe] Testing {total} services...", 0, total)

            batch_size = context.config.get("batch_size", 30)
            all_results: list[dict] = []

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

                for i in range(0, len(functions), batch_size):
                    batch = functions[i : i + batch_size]
                    batch_out = await asyncio.gather(*[_check(fn) for fn in batch])
                    for r_list in batch_out:
                        all_results.extend(r_list)
                    done = min(i + batch_size, total)
                    context.report_progress(
                        f"[Holehe] Checked {done}/{total} services...",
                        done,
                        total,
                    )

            for result in all_results:
                if not result.get("exists"):
                    if result.get("rateLimit"):
                        log.append(f"[~] {result.get('name', '?')}: rate-limited")
                    continue

                site_name = result.get("name", "unknown")
                domain = result.get("domain", "")
                props: dict = {
                    "platform": site_name,
                    "domain": domain,
                    "source": "holehe",
                }
                if result.get("emailrecovery"):
                    props["email_recovery"] = "present"
                if result.get("phoneNumber"):
                    props["phone_hint"] = "present"
                for k, v in (result.get("others") or {}).items():
                    props[f"extra_{k}"] = str(v)

                label = f"[{site_name}] account"
                nodes.append({
                    "type": "SOCIAL_ACCOUNT",
                    "label": label,
                    "properties": props,
                })
                edges.append({
                    "source": value,
                    "target": label,
                    "type": "LINKED_TO",
                })
                observations.append(build_observation(
                    "holehe",
                    {"field": "registered_account", "platform": site_name, "domain": domain},
                    collection_method="PUBLIC_SEARCH",
                    confidence=0.75,
                ))
                line = f"[+] {site_name}: account found"
                log.append(line)
                context.report_progress(line, len(nodes), total)

            done_line = f"[Holehe] Done — {len(nodes)} account(s) found"
            log.append(done_line)
            context.report_progress(done_line, total, total)

        except ImportError:
            log.append("[Holehe] ERROR: holehe not installed. Run: pip install holehe httpx")
        except Exception as e:
            log.append(f"[Holehe] ERROR: {type(e).__name__}")

        return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}
