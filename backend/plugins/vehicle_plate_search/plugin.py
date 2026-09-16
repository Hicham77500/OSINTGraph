"""Vehicle plate — public web hits (mentions), not registry meta-nodes."""
from __future__ import annotations

from plugins.base import PluginContext, TransformPlugin
from services.general_search import build_vehicle_plate_links
from services.web_search_results import fetch_web_findings, findings_to_graph


class VehiclePlateSearchPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        plate = context.entity.label.strip()
        country = str(context.config.get("country") or "FR")
        context.log("[PlateSearch] Public web mentions…")

        brave_key = await context.api_manager.get_key_and_check_quota("brave")
        normalized = plate.upper().replace(" ", "-")
        findings = await fetch_web_findings(normalized, brave_api_key=brave_key)
        if brave_key:
            await context.api_manager.register_usage("brave")

        nodes, edges, observations = findings_to_graph(plate, findings, "plate_search")
        assistants = build_vehicle_plate_links(plate, country=country)

        log = [
            "[PlateSearch] Données registre = voie légale uniquement.",
            f"[PlateSearch] {len(findings)} mention(s) web publique(s)",
        ]

        return {
            "nodes": nodes,
            "edges": edges,
            "observations": observations,
            "log": log,
            "result_cards": findings,
            "search_assistants": assistants,
        }
