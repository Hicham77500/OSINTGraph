"""Platform connector base — extensible multi-platform OSINT."""
from abc import ABC, abstractmethod
from typing import Any


class PlatformConnector(ABC):
    platform: str = "unknown"
    capabilities: list[str] = ["MANUAL"]

    @abstractmethod
    async def normalize(self, raw: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    async def search(self, query: str) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def parse(self, url: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def build_observations(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        ...


class ManualConnector(PlatformConnector):
    platform = "manual"
    capabilities = ["MANUAL"]

    async def normalize(self, raw: dict[str, Any]) -> dict[str, Any]:
        return raw

    async def search(self, query: str) -> list[dict[str, Any]]:
        return []

    async def parse(self, url: str) -> dict[str, Any]:
        return {"url": url, "platform": self.platform}

    async def build_observations(self, parsed: dict[str, Any]) -> list[dict[str, Any]]:
        return [
            {
                "source": {
                    "platform": self.platform,
                    "collection_method": "MANUAL",
                    "url": parsed.get("url"),
                },
                "content": parsed,
                "confidence": 0.95,
                "status": "CONFIRMED",
            }
        ]


CONNECTOR_REGISTRY: dict[str, PlatformConnector] = {
    "manual": ManualConnector(),
    "instagram": ManualConnector(),
    "tiktok": ManualConnector(),
    "linkedin": ManualConnector(),
    "github": ManualConnector(),
    "x": ManualConnector(),
    "facebook": ManualConnector(),
}
