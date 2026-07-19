from plugins.base import TransformPlugin, PluginContext
import phonenumbers
from phonenumbers import geocoder, carrier

class PhoneLookupPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        value = context.entity.label
        context.log(f"[PhoneLookup] Analysing {value}...")
        
        nodes = []
        edges = []
        log = []
        
        try:
            # Parse number (assuming it might not have a + prefix, we try to parse it, 
            # if invalid we can try appending + if it's international format)
            raw = value if value.startswith('+') else f"+{value}"
            try:
                parsed = phonenumbers.parse(raw)
            except phonenumbers.NumberParseException:
                # Fallback without plus if it was a local format, though OSINT usually requires country code
                parsed = phonenumbers.parse(value, "FR") # Defaulting to FR for local numbers as a fallback
                
            if not phonenumbers.is_valid_number(parsed):
                log.append(f"[PhoneLookup] Number {value} is not a valid phone number.")
                return {"nodes": nodes, "edges": edges, "log": log}
                
            # Extract Location (Country / Region)
            location_name = geocoder.description_for_number(parsed, "en")
            if location_name:
                nodes.append({
                    "type": "LOCATION",
                    "label": location_name,
                    "properties": {"source": "phonenumbers", "type": "Country/Region"}
                })
                edges.append({
                    "source": value,
                    "target": location_name,
                    "type": "LOCATED_AT"
                })
                log.append(f"[+] Location found: {location_name}")
                
            # Extract Carrier (Organization)
            carrier_name = carrier.name_for_number(parsed, "en")
            if carrier_name:
                nodes.append({
                    "type": "ORGANIZATION",
                    "label": carrier_name,
                    "properties": {"source": "phonenumbers", "type": "Telecom Carrier"}
                })
                edges.append({
                    "source": value,
                    "target": carrier_name,
                    "type": "USES" # The phone number uses this carrier
                })
                log.append(f"[+] Carrier found: {carrier_name}")
                
            log.append("[PhoneLookup] Done.")
            
        except Exception as e:
            log.append(f"[PhoneLookup] Error: {e}")

        return {"nodes": nodes, "edges": edges, "log": log}
