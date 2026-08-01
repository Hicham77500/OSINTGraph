"""SpiderFoot bridge — multi-module OSINT scan via SpiderFoot HTTP API."""
import asyncio
import os
from typing import Any

import httpx

from plugins.base import PluginContext, TransformPlugin
from plugins.helpers import (
    SPIDERFOOT_TYPE_MAP,
    build_observation,
    infer_spiderfoot_target_type,
)

# Passive modules safe for public OSINT (subset of SpiderFoot footprint)
DEFAULT_PASSIVE_MODULES = (
    "sfp_dnsresolve,sfp_whois,sfp_sslcert,sfp_bingsearch,sfp_googlesearch,"
    "sfp_emailformat,sfp_accounts,sfp_social,sfp_spider,sfp_threatcrowd,"
    "sfp_crt,sfp_hunter,sfp_builtwith"
)


class SpiderFootScanPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        value = context.entity.label.strip()
        base_url = (
            context.config.get("spiderfoot_url")
            or os.getenv("SPIDERFOOT_URL", "http://127.0.0.1:5001")
        ).rstrip("/")
        timeout = int(context.config.get("timeout", 120))
        usecase = context.config.get("usecase", "passive")
        modules = context.config.get("modules") or DEFAULT_PASSIVE_MODULES
        target_type = context.config.get("target_type") or infer_spiderfoot_target_type(value)

        context.log(f"[SpiderFoot] Starting {usecase} scan...")
        log = [f"[SpiderFoot] Target type: {target_type}"]

        nodes: list[dict] = []
        edges: list[dict] = []
        observations: list[dict] = []
        seen: set[tuple[str, str]] = set()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                health = await client.get(f"{base_url}/scanlist")
                if health.status_code >= 500:
                    log.append("[SpiderFoot] ERROR: SpiderFoot server unreachable.")
                    log.append("  Install: https://github.com/smicallef/spiderfoot")
                    log.append(f"  Set SPIDERFOOT_URL (current: {base_url})")
                    return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}

                scan_name = f"osintgraph-{value[:40]}"
                resp = await client.post(
                    f"{base_url}/startscan",
                    data={
                        "scanname": scan_name,
                        "scantarget": value,
                        "modulelist": modules,
                        "typelist": target_type,
                        "usecase": usecase,
                    },
                )
                if resp.status_code != 200:
                    log.append(f"[SpiderFoot] ERROR: startscan failed ({resp.status_code})")
                    return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}

                payload = resp.json()
                if not isinstance(payload, list) or len(payload) < 2 or payload[0] != "SUCCESS":
                    log.append("[SpiderFoot] ERROR: unexpected startscan response")
                    return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}

                scan_id = payload[1]
                log.append(f"[SpiderFoot] Scan started (id={scan_id[:8]}...)")

                elapsed = 0
                poll_interval = 5
                status = "RUNNING"
                while elapsed < timeout:
                    await asyncio.sleep(poll_interval)
                    elapsed += poll_interval
                    scanlist = await client.get(f"{base_url}/scanlist")
                    if scanlist.status_code != 200:
                        continue
                    for row in scanlist.json():
                        if isinstance(row, list) and row[0] == scan_id:
                            status = row[5] if len(row) > 5 else "UNKNOWN"
                            break
                    if status in ("FINISHED", "ERROR-FAILED", "ABORT-REQUESTED"):
                        break
                    if elapsed % 30 == 0:
                        line = f"[SpiderFoot] Still running ({elapsed}s)..."
                        log.append(line)
                        context.report_progress(line, elapsed, timeout)

                if status != "FINISHED":
                    log.append(f"[SpiderFoot] Scan ended with status: {status}")
                    if status == "RUNNING":
                        log.append(f"[SpiderFoot] Timeout after {timeout}s — partial results may be missing")

                export = await client.get(
                    f"{base_url}/scanexportjsonmulti",
                    params={"ids": scan_id},
                )
                if export.status_code != 200:
                    log.append("[SpiderFoot] ERROR: could not export results")
                    return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}

                events: list[dict[str, Any]] = export.json()
                if not isinstance(events, list):
                    log.append("[SpiderFoot] ERROR: invalid export format")
                    return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}

                for event in events:
                    if event.get("false_positive") in ("1", 1, True):
                        continue
                    data = str(event.get("data", "")).strip()
                    event_type = str(event.get("event_type", ""))
                    module = str(event.get("module", ""))
                    if not data or not event_type:
                        continue

                    node_type = SPIDERFOOT_TYPE_MAP.get(event_type)
                    if not node_type:
                        continue

                    key = (node_type, data)
                    if key in seen:
                        continue
                    seen.add(key)

                    nodes.append({
                        "type": node_type,
                        "label": data,
                        "properties": {
                            "source": "spiderfoot",
                            "sf_event_type": event_type,
                            "sf_module": module,
                        },
                    })
                    edges.append({
                        "source": value,
                        "target": data,
                        "type": "LINKED_TO",
                    })
                    observations.append(build_observation(
                        "spiderfoot",
                        {
                            "field": event_type.lower(),
                            "value": data,
                            "module": module,
                        },
                        collection_method="PUBLIC_SEARCH",
                        confidence=0.65,
                    ))

                done_line = f"[SpiderFoot] Done — {len(nodes)} entit(y/ies) from {len(events)} events"
                log.append(done_line)
                context.report_progress(done_line, timeout, timeout)

        except httpx.ConnectError:
            log.append("[SpiderFoot] ERROR: cannot connect to SpiderFoot server.")
            log.append("  Start SpiderFoot: python3 sf.py -l 127.0.0.1:5001")
            log.append("  Or set SPIDERFOOT_URL in environment")
        except Exception as e:
            log.append(f"[SpiderFoot] ERROR: {type(e).__name__}")

        return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}
