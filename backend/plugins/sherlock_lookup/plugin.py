import asyncio
import os
from plugins.base import TransformPlugin, PluginContext


class SherlockLookupPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        value = context.entity.label
        context.log(f"[Sherlock] Searching username '{value}' across 378+ sites...")
        
        nodes = []
        edges = []
        log = []

        try:
            from sherlock_project.sherlock import sherlock, SitesInformation, QueryStatus
            from sherlock_project.notify import QueryNotify

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

            data_path = os.path.join(
                os.path.dirname(__import__("sherlock_project").__file__),
                "resources", "data.json"
            )
            site_data = {
                site.name: dict(site.information)
                for site in SitesInformation(data_path)
            }

            notifier = _SilentNotify()
            timeout = context.config.get("timeout", 20)

            results = await asyncio.to_thread(
                sherlock, value, site_data, notifier, timeout=timeout
            )

            for site_name, result in results.items():
                if result["status"].status == QueryStatus.CLAIMED:
                    url = result["status"].site_url_user
                    nodes.append({
                        "type": "SOCIAL_ACCOUNT",
                        "label": f"{value}@{site_name}",
                        "properties": {
                            "platform": site_name,
                            "url":      url,
                            "source":   "sherlock",
                            "username": value,
                        },
                    })
                    edges.append({
                        "source": value,
                        "target": f"{value}@{site_name}",
                        "type": "OWNS",
                    })
                    log.append(f"[+] {site_name}: {url}")

            log.append(f"[Sherlock] Done — {len(nodes)} profile(s) found")

        except ImportError:
            log.append("[Sherlock] ERROR: sherlock-project not installed. Run: pip install sherlock-project")
        except Exception as e:
            log.append(f"[Sherlock] ERROR: {e}")

        return {"nodes": nodes, "edges": edges, "log": log}
