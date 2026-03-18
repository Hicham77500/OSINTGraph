"""
OsintGraph — Transform Base Class & Registry
"""
import importlib
import pkgutil
from typing import Any


class Transform:
    """Base class for all OsintGraph OSINT transforms."""
    name: str = "base"
    display_name: str = "Base Transform"
    input_type: str = "*"
    output_type: str = "unknown"
    description: str = ""

    async def run(self, value: str, options: dict[str, Any] = {}) -> dict[str, Any]:
        """
        Execute the transform.
        Returns:
          {
            "nodes": [{"type": str, "label": str, "properties": {...}}],
            "edges": [],
            "log": ["step 1", "step 2", ...]
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
