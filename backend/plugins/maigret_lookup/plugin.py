"""Maigret Lookup — Username → social profiles (inspired by knwldgbox)."""
import asyncio
import json
import os
import re
import shutil
import tempfile

from plugins.base import PluginContext, TransformPlugin
from plugins.helpers import build_observation, sanitize_username

ANSI_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


class MaigretLookupPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        raw = context.entity.label.strip()
        username = sanitize_username(raw)
        if not username:
            return {"nodes": [], "edges": [], "observations": [], "log": ["[Maigret] Invalid username"]}

        context.log(f"[Maigret] Building dossier for username...")
        timeout = int(context.config.get("timeout", 10))
        all_sites = bool(context.config.get("all_sites", False))

        nodes: list[dict] = []
        edges: list[dict] = []
        observations: list[dict] = []
        log: list[str] = [f"[Maigret] Scanning (timeout={timeout}s)..."]

        reports_dir = tempfile.mkdtemp(prefix="osintgraph_maigret_")
        process = None

        try:
            cmd = [
                "maigret", username,
                "--json", "ndjson",
                "--no-progressbar",
                "--folder", reports_dir,
                "--timeout", str(timeout),
            ]
            if all_sites:
                cmd.append("--all-sites")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            found_sites: dict[str, str] = {}

            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                text = ANSI_RE.sub("", line.decode("utf-8", errors="ignore").strip())
                if not text or "[+]" not in text:
                    continue
                text = text[text.find("[+]") :]
                parts = text[4:].split(": http", 1)
                if len(parts) == 2:
                    site = parts[0].strip()
                    url = "http" + parts[1].strip()
                    found_sites[site] = url
                    context.report_progress(f"[+] {site}: {url}", len(found_sites), 0)

            await process.wait()

            report_path = os.path.join(reports_dir, f"report_{username}_ndjson.json")
            if os.path.exists(report_path):
                with open(report_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        status = entry.get("status") or {}
                        if status.get("status") != "Claimed":
                            continue
                        site_name = entry.get("siteName") or entry.get("site", "unknown")
                        url = status.get("url") or found_sites.get(site_name, "")
                        ids = status.get("ids") or {}
                        props: dict = {
                            "platform": site_name,
                            "source": "maigret",
                            "username": username,
                        }
                        if url:
                            props["url"] = url
                        for k, v in ids.items():
                            if not str(k).startswith("_"):
                                props[f"id_{k}"] = str(v)
                        label = f"{username}@{site_name}"
                        nodes.append({
                            "type": "SOCIAL_ACCOUNT",
                            "label": label,
                            "properties": props,
                        })
                        edges.append({
                            "source": username,
                            "target": label,
                            "type": "OWNS",
                        })
                        observations.append(build_observation(
                            "maigret",
                            {"field": "profile", "platform": site_name, "username": username},
                            collection_method="PUBLIC_SEARCH",
                            url=url or None,
                            confidence=0.7,
                        ))
            else:
                for site, url in found_sites.items():
                    label = f"{username}@{site}"
                    nodes.append({
                        "type": "SOCIAL_ACCOUNT",
                        "label": label,
                        "properties": {
                            "platform": site,
                            "url": url,
                            "source": "maigret",
                            "username": username,
                        },
                    })
                    edges.append({"source": username, "target": label, "type": "OWNS"})

            log.append(f"[Maigret] Done — {len(nodes)} profile(s) found")

        except FileNotFoundError:
            log.append("[Maigret] ERROR: maigret CLI not installed. Run: pip install maigret")
        except Exception as e:
            log.append(f"[Maigret] ERROR: {type(e).__name__}")
        finally:
            if process and process.returncode is None:
                process.terminate()
                await process.wait()
            shutil.rmtree(reports_dir, ignore_errors=True)

        return {"nodes": nodes, "edges": edges, "observations": observations, "log": log}
