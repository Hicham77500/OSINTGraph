import httpx
from plugins.base import TransformPlugin, PluginContext


class IpGeolocationPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        value = context.entity.label
        context.log(f"[IP Geo] Geolocating {value}...")
        
        nodes = []
        edges = []
        log = []

        try:
            # Simple public API usage for now (could be abstracted to GeoProvider later)
            async with httpx.AsyncClient() as client:
                response = await client.get(f"https://ipinfo.io/{value}/json", timeout=10.0)
                if response.status_code != 200:
                    log.append(f"[IP Geo] API returned status {response.status_code}")
                    return {"nodes": nodes, "edges": edges, "log": log}
                
                data = response.json()
                
                city = data.get("city")
                country = data.get("country")
                if city and country:
                    loc = f"{city}, {country}"
                    nodes.append({
                        "type": "LOCATION",
                        "label": loc,
                        "properties": {"source": "ipinfo", "coords": data.get("loc")}
                    })
                    edges.append({
                        "source": value,
                        "target": loc,
                        "type": "LOCATED_AT"
                    })
                    log.append(f"[+] Location: {loc}")
                    
                org = data.get("org")
                if org:
                    nodes.append({
                        "type": "ORGANIZATION",
                        "label": org,
                        "properties": {"source": "ipinfo", "type": "ASN/ISP"}
                    })
                    edges.append({
                        "source": value,
                        "target": org,
                        "type": "OWNS"
                    })
                    log.append(f"[+] Organization/ASN: {org}")
                    
            log.append("[IP Geo] Done.")
            
        except Exception as e:
            log.append(f"[IP Geo] Error: {e}")

        return {"nodes": nodes, "edges": edges, "log": log}
