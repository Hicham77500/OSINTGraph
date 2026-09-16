"""Public search-engine and platform URL assistants — links only, no scraping."""
from __future__ import annotations

from urllib.parse import quote_plus


def _q(value: str) -> str:
    return quote_plus(value.strip())


def build_web_browser_links(query: str) -> list[dict[str, str]]:
    q = _q(query)
    return [
        {"id": "google", "name": "Google", "url": f"https://www.google.com/search?q={q}", "category": "web"},
        {"id": "bing", "name": "Bing", "url": f"https://www.bing.com/search?q={q}", "category": "web"},
        {"id": "duckduckgo", "name": "DuckDuckGo", "url": f"https://duckduckgo.com/?q={q}", "category": "web"},
        {"id": "qwant", "name": "Qwant", "url": f"https://www.qwant.com/?q={q}", "category": "web"},
        {"id": "yandex", "name": "Yandex", "url": f"https://yandex.com/search/?text={q}", "category": "web"},
        {"id": "brave", "name": "Brave Search", "url": f"https://search.brave.com/search?q={q}", "category": "web"},
        {"id": "ecosia", "name": "Ecosia", "url": f"https://www.ecosia.org/search?q={q}", "category": "web"},
        {"id": "startpage", "name": "Startpage", "url": f"https://www.startpage.com/sp/search?q={q}", "category": "web"},
    ]


def build_person_name_links(first_name: str | None, last_name: str | None, full_label: str) -> list[dict[str, str]]:
    parts = [p for p in (first_name, last_name) if p and p.strip()]
    if not parts:
        parts = full_label.split()
    if len(parts) >= 2:
        queries = [
            f'"{parts[0]}" "{parts[-1]}"',
            f"{parts[0]} {parts[-1]}",
            f'"{full_label}"',
        ]
    else:
        queries = [f'"{full_label}"', full_label]
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for query in queries:
        if query in seen:
            continue
        seen.add(query)
        for link in build_web_browser_links(query):
            item = {**link, "id": f"person_{link['id']}_{len(seen)}", "query": query}
            out.append(item)
    return out[:24]


def build_social_platform_links(handle: str, person_name: str | None = None) -> list[dict[str, str]]:
    """Public profile discovery via official search pages or site:-scoped web queries."""
    h = handle.strip().lstrip("@")
    name_q = _q(person_name) if person_name else _q(h)
    user_q = _q(h)
    platforms = [
        ("facebook", "Facebook", f"https://www.google.com/search?q=site:facebook.com+{user_q}"),
        ("instagram", "Instagram", f"https://www.google.com/search?q=site:instagram.com+{user_q}"),
        ("x", "X (Twitter)", f"https://x.com/search?q={user_q}&f=user"),
        ("linkedin", "LinkedIn", f"https://www.google.com/search?q=site:linkedin.com/in+{user_q}"),
        ("tiktok", "TikTok", f"https://www.google.com/search?q=site:tiktok.com+{user_q}"),
        ("youtube", "YouTube", f"https://www.youtube.com/results?search_query={user_q}"),
        ("github", "GitHub", f"https://github.com/search?q={user_q}&type=users"),
        ("reddit_user", "Reddit (user)", f"https://www.reddit.com/search/?q={user_q}"),
        ("pinterest", "Pinterest", f"https://www.pinterest.com/search/pins/?q={user_q}"),
        ("snapchat", "Snapchat (web index)", f"https://www.google.com/search?q=site:snapchat.com+{user_q}"),
        ("telegram", "Telegram (web index)", f"https://www.google.com/search?q=site:t.me+{user_q}"),
        ("discord", "Discord (public index)", f"https://www.google.com/search?q=discord+{user_q}"),
    ]
    if person_name and person_name.strip() != h:
        platforms.append(
            ("facebook_name", "Facebook (name)", f"https://www.google.com/search?q=site:facebook.com+{name_q}"),
        )
    return [
        {
            "id": pid,
            "name": label,
            "url": url,
            "category": "social",
            "handle": h,
        }
        for pid, label, url in platforms
    ]


def build_forum_keyword_links(
    seed: str,
    keywords: list[str] | None = None,
) -> list[dict[str, str]]:
    """
    Public forum/Reddit search URLs. Keywords are analyst-supplied (threat-intel context).
    Does not access private communities or bypass moderation.
    """
    seed = seed.strip()
    kw_list = [k.strip() for k in (keywords or []) if k and k.strip()]
    if not kw_list:
        kw_list = ["reddit"]

    out: list[dict[str, str]] = []
    for kw in kw_list:
        combined = f"{seed} {kw}".strip()
        cq = _q(combined)
        sq = _q(seed)
        kq = _q(kw)
        out.extend([
            {
                "id": f"reddit_{kq}",
                "name": f"Reddit — {kw}",
                "url": f"https://www.reddit.com/search/?q={cq}",
                "category": "forum",
                "keyword": kw,
            },
            {
                "id": f"google_reddit_{kq}",
                "name": f"Google site:reddit.com — {kw}",
                "url": f"https://www.google.com/search?q=site:reddit.com+{cq}",
                "category": "forum",
                "keyword": kw,
            },
            {
                "id": f"google_forum_{kq}",
                "name": f"Google forums — {kw}",
                "url": f"https://www.google.com/search?q={sq}+intext:{kq}+(forum OR board OR community)",
                "category": "forum",
                "keyword": kw,
            },
        ])
    return out


def build_phone_public_links(phone: str) -> list[dict[str, str]]:
    pq = _q(phone)
    quoted = _q(f'"{phone}"')
    return [
        *[{**l, "category": "phone"} for l in build_web_browser_links(f'"{phone}"')],
        {
            "id": "google_phone_reddit",
            "name": "Google site:reddit.com (phone)",
            "url": f"https://www.google.com/search?q=site:reddit.com+{quoted}",
            "category": "phone",
        },
        {
            "id": "google_phone_forums",
            "name": "Google forums (phone)",
            "url": f"https://www.google.com/search?q={pq}+forum",
            "category": "phone",
        },
    ]


def build_vehicle_plate_links(plate: str, country: str = "FR") -> list[dict[str, str]]:
    """
    Public web mentions only — no unauthorized registry API.
    French plates: analyst must use lawful official channels for authoritative data.
    """
    normalized = plate.strip().upper().replace(" ", "-")
    pq = _q(normalized)
    return [
        {
            "id": "plate_web",
            "name": "Google (public mentions)",
            "url": f"https://www.google.com/search?q={pq}",
            "category": "vehicle_plate",
        },
        {
            "id": "plate_forums",
            "name": "Google forums / Reddit",
            "url": f"https://www.google.com/search?q={pq}+(site:reddit.com OR forum)",
            "category": "vehicle_plate",
        },
        {
            "id": "plate_bing",
            "name": "Bing",
            "url": f"https://www.bing.com/search?q={pq}",
            "category": "vehicle_plate",
        },
        {
            "id": "plate_disclaimer",
            "name": "Official registry (manual)",
            "url": "https://www.service-public.fr/" if country.upper() == "FR" else "https://www.google.com/search?q=vehicle+registration+official+portal",
            "category": "vehicle_plate",
            "hint": "Authoritative plate data requires lawful authority — OSINTGraph links public search only.",
        },
    ]


def assistants_to_graph(seed: str, assistants: list[dict[str, str]], platform: str) -> tuple[list, list, list]:
    """Convert assistant links to plugin graph payload with observations."""
    from plugins.helpers import build_observation

    nodes: list[dict] = []
    edges: list[dict] = []
    observations: list[dict] = []
    for item in assistants:
        label = item["name"]
        url = item["url"]
        nodes.append({
            "type": "URL",
            "label": label,
            "properties": {
                "url": url,
                "source": platform,
                "category": item.get("category", ""),
            },
        })
        edges.append({"source": seed, "target": label, "type": "LINKED_TO"})
        observations.append(build_observation(
            platform,
            {
                "field": "search_assistant",
                "name": label,
                "url": url,
                "category": item.get("category"),
                "keyword": item.get("keyword"),
            },
            collection_method="PUBLIC_SEARCH",
            confidence=0.4,
            status="UNVERIFIED",
            url=url,
        ))
    return nodes, edges, observations
