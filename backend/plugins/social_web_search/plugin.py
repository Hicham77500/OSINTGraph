"""Social search — concrete profile/page URLs when available, not platform label nodes."""
from __future__ import annotations

from plugins.base import PluginContext, TransformPlugin
from plugins.helpers import parse_person_label
from services.general_search import build_social_platform_links
from services.web_search_results import fetch_site_findings, findings_to_graph

SITE_QUERIES = [
    ("facebook.com", "Facebook"),
    ("instagram.com", "Instagram"),
    ("linkedin.com", "LinkedIn"),
    ("x.com", "X"),
    ("tiktok.com", "TikTok"),
    ("github.com", "GitHub"),
]


class SocialWebSearchPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        label = context.entity.label.strip()
        handle = label
        person_name = None

        if "@" in label and "." in label.split("@")[-1]:
            handle = label.split("@")[0]
        elif "," in label or (label.count(" ") >= 1 and not label.startswith("@")):
            nom, prenom = parse_person_label(label)
            person_name = f"{prenom} {nom}".strip() if prenom else nom
            handle = person_name

        search_term = person_name or handle.lstrip("@")
        context.log(f"[SocialSearch] Resolving public pages for {search_term}…")

        brave_key = await context.api_manager.get_key_and_check_quota("brave")
        findings: list[dict[str, str]] = []
        for site, _name in SITE_QUERIES:
            hits = await fetch_site_findings(site, search_term, brave_key)
            findings.extend(hits[:3])

        if brave_key:
            await context.api_manager.register_usage("brave")

        # Dedupe by url
        seen: set[str] = set()
        unique: list[dict[str, str]] = []
        for f in findings:
            u = f.get("url", "")
            if u and u not in seen:
                seen.add(u)
                unique.append(f)

        nodes, edges, observations = findings_to_graph(label, unique[:12], "social_search")
        assistants = build_social_platform_links(handle.lstrip("@"), person_name)

        log = [f"[SocialSearch] {len(unique)} page(s) trouvée(s)"]
        if not unique:
            log.append("[SocialSearch] Configurez BRAVE_SEARCH_API_KEY pour des hits site:… fiables.")

        return {
            "nodes": nodes,
            "edges": edges,
            "observations": observations,
            "log": log,
            "result_cards": unique,
            "search_assistants": assistants,
        }
