"""
OSINTGraph — Dynamic Entity Type Registry
"""
from typing import Dict, List, Any


class EntityTypeRegistry:
    """Registry to hold dynamically loaded Entity Types for the platform."""
    _types: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, type_name: str, config: Dict[str, Any] = None):
        """Register a new entity type."""
        if config is None:
            config = {}
        cls._types[type_name.upper()] = config

    @classmethod
    def is_valid(cls, type_name: str) -> bool:
        """Check if an entity type is registered."""
        return type_name.upper() in cls._types

    @classmethod
    def get_all(cls) -> List[str]:
        """Return all registered entity types."""
        return list(cls._types.keys())

    @classmethod
    def get_config(cls, type_name: str) -> Dict[str, Any]:
        return cls._types.get(type_name.upper(), {})


# Pre-populate with standard OSINTGraph types
def _populate_defaults():
    defaults = [
        # Personnes
        "PERSON", "ALIAS", "USERNAME", "EMAIL", "PHONE", "FACE", "VOICE",
        # Réseau
        "IP", "IPV6", "DOMAIN", "SUBDOMAIN", "URL", "WEBSITE", "ASN", "DNS_RECORD", "SSL_CERTIFICATE",
        # Localisation
        "COUNTRY", "REGION", "CITY", "ADDRESS", "GPS_COORDINATES", "PLACE",
        # Entreprises
        "COMPANY", "ORGANIZATION", "GOVERNMENT", "ASSOCIATION",
        # Sociaux
        "SOCIAL_ACCOUNT", "SOCIAL_POST", "COMMENT", "HASHTAG", "MENTION", "GROUP", "CHANNEL",
        # Documents
        "IMAGE", "VIDEO", "AUDIO", "PDF", "ARCHIVE", "SCREENSHOT",
        # Crypto
        "WALLET", "TRANSACTION", "BLOCKCHAIN", "TOKEN",
        # Infra
        "HOST", "SERVER", "SERVICE", "REPOSITORY", "DOCKER_IMAGE", "API_ENDPOINT",
        # Legacy / Divers
        "EVENT", "MEDIA", "CUSTOM"
    ]
    for dt in defaults:
        EntityTypeRegistry.register(dt)

_populate_defaults()
