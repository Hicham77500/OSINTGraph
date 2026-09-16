"""Reddit / forum — public hit URLs when Brave available, else keyword search assistants only."""
from __future__ import annotations

from plugins.base import PluginContext, TransformPlugin
from services.general_search import build_forum_keyword_links
from services.web_search_results import fetch_site_findings, findings_to_graph

DEFAULT_SUGGESTED_KEYWORDS = [
    "reddit",
    "forum",
    "leak",
    "breach",
    "credential",
    "pirate",
]


class ForumSearchAssistantsPlugin(TransformPlugin):
    async def run(self, context: PluginContext) -> dict:
        label = context.entity.label.strip()
        raw_kw = context.config.get("keywords") or context.config.get("forum_keywords")
        if isinstance(raw_kw, str):
            keywords = [k.strip() for k in raw_kw.split(",") if k.strip()]
        elif isinstance(raw_kw, list):
            keywords = [str(k).strip() for k in raw_kw if str(k).strip()]
        else:
            keywords = DEFAULT_SUGGESTED_KEYWORDS[:6]

        context.log(f"[ForumSearch] Public index: {', '.join(keywords)}")

        brave_key = await context.api_manager.get_key_and_check_quota("brave")
        findings: list[dict[str, str]] = []
        for kw in keywords[:6]:
            q = f"{label} {kw}"
            findings.extend(await fetch_site_findings("reddit.com", q, brave_key))
        if brave_key:
            await context.api_manager.register_usage("brave")

        seen: set[str] = set()
        unique: list[dict[str, str]] = []
        for f in findings:
            u = f.get("url", "")
            if u and u not in seen:
                seen.add(u)
                unique.append(f)

        nodes, edges, observations = findings_to_graph(label, unique[:10], "forum_search")
        assistants = build_forum_keyword_links(label, keywords)

        log = [
            "[ForumSearch] Index public uniquement.",
            f"[ForumSearch] {len(unique)} fil(s) Reddit/public trouvé(s)",
        ]

        return {
            "nodes": nodes,
            "edges": edges,
            "observations": observations,
            "log": log,
            "result_cards": unique,
            "search_assistants": assistants,
        }
