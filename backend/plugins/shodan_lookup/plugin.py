import asyncio
import shodan
from plugins.base import TransformPlugin, PluginContext


class ShodanLookupPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        value = context.entity.label
        context.log(f"[Shodan] Lookup for {value}...")
        
        api_key = await context.api_manager.get_key_and_check_quota("shodan")
        if not api_key:
            context.log("[Shodan] ERROR: Missing or disabled API key.")
            return {"nodes": [], "edges": [], "log": ["[Shodan] ERROR: Missing or disabled API key."]}

        nodes = []
        edges = []
        log = []

        try:
            api = shodan.Shodan(api_key)
            # Run blocking call in thread
            result = await asyncio.to_thread(api.host, value)

            # Extract Organization
            org = result.get("org")
            if org:
                nodes.append({
                    "type": "ORGANIZATION",
                    "label": org,
                    "properties": {"source": "shodan"},
                })
                edges.append({
                    "source": value,
                    "target": org,
                    "type": "OWNS",
                })
                log.append(f"[+] Organization: {org}")

            # Extract OS
            os_name = result.get("os")
            if os_name:
                log.append(f"[+] OS: {os_name}")

            # Extract Ports
            ports = result.get("ports", [])
            for p in ports:
                # Add a CUSTOM node for the port for now, or just log
                log.append(f"[+] Open port: {p}")

            await context.api_manager.register_usage("shodan")
            log.append(f"[Shodan] Done — {len(ports)} ports found, org: {org}")

        except shodan.APIError as e:
            log.append(f"[Shodan] API Error: {e}")
        except Exception as e:
            log.append(f"[Shodan] Unexpected Error: {e}")

        return {"nodes": nodes, "edges": edges, "log": log}
