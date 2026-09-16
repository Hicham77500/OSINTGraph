"""Person/query web search — real hits on the graph, engine links in result_cards only."""
from __future__ import annotations

from plugins.base import PluginContext, TransformPlugin
from plugins.helpers import parse_person_label
from services.general_search import build_person_name_links, build_phone_public_links, build_web_browser_links
from services.web_search_results import fetch_web_findings, findings_to_graph


def _primary_query(label: str, input_type: str) -> str:
    input_type = input_type.upper()
    if input_type == "PERSON" or "," in label or (" " in label and "@" not in label):
        nom, prenom = parse_person_label(label)
        if prenom and nom:
            return f'"{prenom} {nom}"'
        return f'"{label}"'
    return label.strip()


class WebSearchAssistantsPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        label = context.entity.label.strip()
        input_type = (context.config.get("input_type") or "").upper()
        context.log("[WebSearch] Fetching public web hits…")

        digits = label.replace("+", "").replace(" ", "").replace("-", "")
        if input_type == "PHONE" or (digits.isdigit() and len(digits) >= 8):
            query = f'"{label}"'
            assistants = build_phone_public_links(label)
        elif input_type == "PERSON" or "," in label or (" " in label and "@" not in label):
            nom, prenom = parse_person_label(label)
            full = f"{prenom} {nom}".strip() if prenom else nom
            query = _primary_query(label, input_type)
            assistants = build_person_name_links(prenom, nom, full or label)
        else:
            query = label
            assistants = build_web_browser_links(label)

        brave_key = await context.api_manager.get_key_and_check_quota("brave")
        findings = await fetch_web_findings(query, brave_api_key=brave_key)
        if brave_key:
            await context.api_manager.register_usage("brave")

        nodes, edges, observations = findings_to_graph(label, findings, "web_search")

        log = [f"[WebSearch] Query: {query}"]
        for f in findings:
            log.append(f"[+] {f.get('title', f['url'])[:80]}")
        if not findings:
            log.append("[WebSearch] Aucun hit structuré — configurez BRAVE_SEARCH_API_KEY ou vérifiez manuellement.")
        log.append(f"[WebSearch] {len(findings)} résultat(s) affichable(s)")

        return {
            "nodes": nodes,
            "edges": edges,
            "observations": observations,
            "log": log,
            "result_cards": findings,
            "search_assistants": assistants,
        }
