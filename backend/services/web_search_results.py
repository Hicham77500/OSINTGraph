"""Fetch displayable web hits (titles, URLs, snippets) via official/lightweight APIs."""
from __future__ import annotations

import logging
from urllib.parse import quote_plus, urlparse

import httpx

logger = logging.getLogger("osintgraph.web_search_results")

MAX_FINDINGS = 12


async def _brave_web_search(query: str, api_key: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            res = await client.get(
                "https://api.search.brave.com/res/v1/web/search",
                params={"q": query, "count": 10},
                headers={
                    "Accept": "application/json",
                    "X-Subscription-Token": api_key,
                },
            )
            if res.status_code != 200:
                return out
            data = res.json()
            for item in (data.get("web") or {}).get("results") or []:
                url = item.get("url") or ""
                title = item.get("title") or url
                snippet = item.get("description") or ""
                if url:
                    out.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "source_engine": "brave",
                    })
    except httpx.HTTPError as e:
        logger.debug("Brave search failed: %s", type(e).__name__)
    return out


async def _duckduckgo_instant(query: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            res = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_redirect": 1, "no_html": 1},
            )
            if res.status_code != 200:
                return out
            data = res.json()
            abstract_url = data.get("AbstractURL") or ""
            if abstract_url:
                out.append({
                    "title": data.get("Heading") or query,
                    "url": abstract_url,
                    "snippet": data.get("Abstract") or "",
                    "source_engine": "duckduckgo",
                })

            def walk(topics: list) -> None:
                for topic in topics:
                    if isinstance(topic, dict):
                        if topic.get("FirstURL"):
                            out.append({
                                "title": (topic.get("Text") or "")[:120] or topic["FirstURL"],
                                "url": topic["FirstURL"],
                                "snippet": topic.get("Text") or "",
                                "source_engine": "duckduckgo",
                            })
                        if topic.get("Topics"):
                            walk(topic["Topics"])

            walk(data.get("RelatedTopics") or [])
    except httpx.HTTPError as e:
        logger.debug("DDG instant failed: %s", type(e).__name__)
    return out


async def _wikipedia_opensearch(query: str, lang: str = "fr") -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(
                f"https://{lang}.wikipedia.org/w/api.php",
                params={
                    "action": "opensearch",
                    "search": query,
                    "limit": 5,
                    "format": "json",
                },
                headers={"User-Agent": "OSINTGraph/1.0 (public OSINT; local analyst)"},
            )
            if res.status_code != 200:
                return out
            data = res.json()
            if len(data) >= 4:
                titles, descriptions, urls = data[1], data[2], data[3]
                for title, desc, url in zip(titles, descriptions, urls):
                    out.append({
                        "title": title,
                        "url": url,
                        "snippet": desc or "",
                        "source_engine": f"wikipedia_{lang}",
                    })
    except httpx.HTTPError:
        pass
    return out


def _dedupe_findings(items: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for item in items:
        url = (item.get("url") or "").strip()
        if not url or url in seen:
            continue
        seen.add(url)
        out.append(item)
        if len(out) >= MAX_FINDINGS:
            break
    return out


async def fetch_web_findings(
    query: str,
    brave_api_key: str | None = None,
) -> list[dict[str, str]]:
    """Best-effort real hits for analyst review (not search-engine meta nodes)."""
    query = query.strip()
    if not query:
        return []

    collected: list[dict[str, str]] = []
    if brave_api_key:
        collected.extend(await _brave_web_search(query, brave_api_key))
    collected.extend(await _duckduckgo_instant(query))
    collected.extend(await _wikipedia_opensearch(query, "fr"))
    collected.extend(await _wikipedia_opensearch(query, "en"))

    return _dedupe_findings(collected)


async def fetch_site_findings(
    site: str,
    query: str,
    brave_api_key: str | None,
) -> list[dict[str, str]]:
    q = f'site:{site} {query}'
    if brave_api_key:
        return _dedupe_findings(await _brave_web_search(q, brave_api_key))
    return _dedupe_findings(await _duckduckgo_instant(q))


def findings_to_graph(
    seed: str,
    findings: list[dict[str, str]],
    platform: str,
) -> tuple[list[dict], list[dict], list[dict]]:
    from plugins.helpers import build_observation

    nodes: list[dict] = []
    edges: list[dict] = []
    observations: list[dict] = []

    for f in findings:
        url = f["url"]
        title = f.get("title") or urlparse(url).netloc
        label = title if len(title) <= 96 else title[:93] + "…"
        host = urlparse(url).netloc.lower()
        node_type = "SOCIAL_ACCOUNT" if any(
            s in host for s in ("facebook.", "instagram.", "linkedin.", "twitter.", "x.com", "tiktok.")
        ) else "URL"

        nodes.append({
            "type": node_type,
            "label": label,
            "properties": {
                "url": url,
                "snippet": (f.get("snippet") or "")[:500],
                "source_engine": f.get("source_engine", ""),
                "source": platform,
            },
        })
        edges.append({"source": seed, "target": label, "type": "LINKED_TO"})
        observations.append(build_observation(
            platform,
            {"field": "web_hit", "title": title, "url": url, "snippet": f.get("snippet", "")},
            collection_method="PUBLIC_SEARCH",
            confidence=0.55,
            status="UNVERIFIED",
            url=url,
        ))

    return nodes, edges, observations
