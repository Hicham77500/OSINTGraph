"""Shared helpers for OSINTGraph transform plugins."""
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
