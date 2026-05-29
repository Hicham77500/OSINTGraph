"""Sherlock Lookup Transform — Username → Social Media Profiles (378+ sites)"""
import asyncio
import os
from transforms.base import Transform, register


@register
class SherlockLookup(Transform):
    name = "sherlock_lookup"
    display_name = "Sherlock — Social Profiles"
    input_type = "username"
    output_type = "username"
    description = "Search username across 378+ social networks (sherlock-project)"

    async def run(self, value: str, options: dict = {}) -> dict:
        log = [f"[Sherlock] Searching username '{value}' across 378+ sites..."]
        nodes = []
        edges = []

        try:
            from sherlock_project.sherlock import sherlock, SitesInformation, QueryStatus
            from sherlock_project.notify import QueryNotify

            # Silent notifier — collects results without printing
            class _SilentNotify(QueryNotify):
                def __init__(self):
                    super().__init__()
                    self.found: list[dict] = []

                def update(self, result):
                    self.result = result
                    if result.status == QueryStatus.CLAIMED:
                        self.found.append({
                            "site":    result.site_name,
                            "url":     result.site_url_user,
                        })

            # Load sites database bundled with sherlock-project
            data_path = os.path.join(
                os.path.dirname(__import__("sherlock_project").__file__),
                "resources", "data.json"
            )
            site_data = {
                site.name: dict(site.information)
                for site in SitesInformation(data_path)
            }

            notifier = _SilentNotify()
            timeout = options.get("timeout", 20)

            # sherlock() is synchronous (uses concurrent.futures internally)
            results = await asyncio.to_thread(
                sherlock, value, site_data, notifier, timeout=timeout
            )

            # Build nodes from claimed profiles
            for site_name, result in results.items():
                if result["status"].status == QueryStatus.CLAIMED:
                    url = result["status"].site_url_user
                    nodes.append({
                        "type": "username",
                        "label": f"{value}@{site_name}",
                        "properties": {
                            "platform": site_name,
                            "url":      url,
                            "source":   "sherlock",
                            "username": value,
                        },
                    })
                    log.append(f"[+] {site_name}: {url}")

            log.append(f"[Sherlock] Done — {len(nodes)} profile(s) found")

        except ImportError:
            log.append("[Sherlock] ERROR: sherlock-project not installed. Run: pip install sherlock-project")
        except Exception as e:
            log.append(f"[Sherlock] ERROR: {e}")

        return {"nodes": nodes, "edges": edges, "log": log}
