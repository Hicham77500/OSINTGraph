"""
OSINTGraph — TransformPlugin Base Architecture
"""
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import logging

from models.domain import EntityOut

@dataclass
class PluginContext:
    """Context passed to each plugin during execution."""
    entity: EntityOut
    api_manager: Any
    logger: logging.Logger
    cache: Any = None
    config: Dict[str, Any] = field(default_factory=dict)
    cancellation_token: Any = None
    progress_callback: Optional[Callable[[int, int, str], None]] = None

    def log(self, msg: str, level: int = logging.INFO):
        self.logger.log(level, msg)

    def report_progress(self, message: str, current: int = 0, total: int = 0) -> None:
        """Stream a progress/log line to the transform WebSocket channel."""
        if self.progress_callback:
            self.progress_callback(current, total, message)


class TransformPlugin:
    """
    Base class for all OSINTGraph plugins.
    In the new architecture, most metadata is loaded from manifest.yaml.
    This class just provides the interface and helper methods.
    """
    
    # These will be populated by the registry based on manifest.yaml
    manifest: Dict[str, Any] = {}
    
    def __init__(self):
        self.name = self.manifest.get("name", "Unknown Plugin")
        
    async def run(self, context: PluginContext) -> Dict[str, Any]:
        """
        Execute the plugin.
        Returns a dictionary containing the subgraph to merge:
        {
            "nodes": [ { "type": "...", "label": "...", "properties": {}, "confidence": 1.0, "source": "..." } ],
            "edges": [ { "source": "node_label", "target": "node_label", "type": "..." } ],
            "observations": [...],
            "log": ["sanitized steps"]
        }
        """
        raise NotImplementedError("Plugins must implement the run() method.")
