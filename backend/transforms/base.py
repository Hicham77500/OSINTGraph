"""
OSINTGraph — Transform Base Class & Registry
"""
import importlib
import logging
import pkgutil
from typing import Any

logger = logging.getLogger("osintgraph.transforms")


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


class Transform:
    """Base class for all OSINTGraph OSINT transforms."""
    name: str = "base"
    display_name: str = "Base Transform"
    input_type: str = "*"
    output_type: str = "unknown"
    description: str = ""
    platform: str = "transform"

    async def run(self, value: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Execute the transform.
        Returns:
          {
            "nodes": [...],
            "edges": [],
            "observations": [...],
            "log": ["sanitized steps"]
          }
        """
        raise NotImplementedError


_registry: dict[str, type[Transform]] = {}


def register(cls: type[Transform]) -> type[Transform]:
    _registry[cls.name] = cls
    return cls


def get_transform(name: str) -> Transform | None:
    cls = _registry.get(name)
    return cls() if cls else None


def list_transforms() -> list[dict]:
    return [
        {
            "name": cls.name,
            "display_name": cls.display_name,
            "input_type": cls.input_type,
            "output_type": cls.output_type,
            "description": cls.description,
        }
        for cls in _registry.values()
    ]


def autodiscover():
    """Auto-import all transform modules in this package."""
    import transforms as pkg
    for _, module_name, _ in pkgutil.iter_modules(pkg.__path__):
        if module_name not in ("base", "registry"):
            importlib.import_module(f"transforms.{module_name}")
