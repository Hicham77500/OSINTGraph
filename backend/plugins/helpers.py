"""Shared helpers for OSINTGraph transform plugins."""
from __future__ import annotations

import unicodedata
from typing import Any


def build_observation(
    platform: str,
    content: dict[str, Any],
    collection_method: str = "TRANSFORM",
    confidence: float = 0.7,
    status: str = "UNVERIFIED",
    url: str | None = None,
) -> dict[str, Any]:
    return {
        "source": {
            "platform": platform,
            "collection_method": collection_method,
            "url": url,
        },
        "content": content,
        "confidence": confidence,
        "status": status,
    }


def sanitize_username(value: str) -> str:
    """Strip unsafe characters from usernames before subprocess calls."""
    return "".join(c for c in value if c.isalnum() or c in "_-.")


def normalize_person_name(name: str) -> str:
    """Uppercase and strip accents for INSEE-style name matching."""
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_name = "".join(c for c in nfkd if not unicodedata.combining(c))
    return ascii_name.upper().strip()


def parse_person_label(label: str) -> tuple[str, str | None]:
    """Extract family name and optional first name from a person label."""
    label = label.strip()
    if not label:
        return "", None

    if "," in label:
        parts = [p.strip() for p in label.split(",", 1)]
        nom = normalize_person_name(parts[0])
        prenom = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
        return nom, prenom

    tokens = label.split()
    if len(tokens) == 1:
        return normalize_person_name(tokens[0]), None

    # French style: last token is often the family name in uppercase.
    if tokens[-1].isupper() or tokens[-1].upper() == tokens[-1]:
        return normalize_person_name(tokens[-1]), " ".join(tokens[:-1])

    return normalize_person_name(tokens[0]), " ".join(tokens[1:])


def format_date_yyyymmdd(raw: str | None) -> str | None:
    """Format INSEE AAAAMMJJ dates as JJ/MM/AAAA."""
    if not raw or len(str(raw)) != 8 or not str(raw).isdigit():
        return str(raw) if raw else None
    s = str(raw)
    return f"{s[6:8]}/{s[4:6]}/{s[0:4]}"


# SpiderFoot event types → OSINTGraph node types
SPIDERFOOT_TYPE_MAP: dict[str, str] = {
    "IP_ADDRESS": "IP",
    "IPV6_ADDRESS": "IP",
    "INTERNET_NAME": "DOMAIN",
    "DOMAIN_NAME": "DOMAIN",
    "AFFILIATE_INTERNET_NAME": "DOMAIN",
    "AFFILIATE_DOMAIN_NAME": "DOMAIN",
    "EMAILADDR": "EMAIL",
    "EMAILADDR_COMPROMISED": "EMAIL",
    "AFFILIATE_EMAILADDR": "EMAIL",
    "USERNAME": "USERNAME",
    "PHONE_NUMBER": "PHONE",
    "HUMAN_NAME": "PERSON",
    "COMPANY_NAME": "ORGANIZATION",
    "SOCIAL_MEDIA": "SOCIAL_ACCOUNT",
    "AFFILIATE_IPADDR": "IP",
    "GEOINFO": "LOCATION",
    "PHYSICAL_ADDRESS": "LOCATION",
    "PROVIDER_HOSTING": "ORGANIZATION",
    "PROVIDER_TELCO": "ORGANIZATION",
}


def infer_spiderfoot_target_type(value: str) -> str:
    """Guess SpiderFoot target type from the seed value."""
    value = value.strip()
    if "@" in value and "." in value.split("@", 1)[-1]:
        return "EMAILADDR"
    if value.replace(".", "").replace(":", "").isdigit() or (
        ":" in value and all(p.isdigit() or p in "abcdefABCDEF:" for p in value)
    ):
        return "IP_ADDRESS"
    if value.replace("+", "").replace("-", "").replace(" ", "").isdigit():
        return "PHONE_NUMBER"
    if "." in value and " " not in value:
        return "INTERNET_NAME"
    if " " in value:
        return "HUMAN_NAME"
    return "USERNAME"
