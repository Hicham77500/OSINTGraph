"""
OSINTGraph — Plugin Registry (Auto-discovery)
"""
import os
import json
import logging
import importlib.util
from typing import Dict, List, Any, Optional

from plugins.base import TransformPlugin

logger = logging.getLogger("osintgraph.plugins")


class PluginRegistry:
    """Discovers, loads, and manages TransformPlugins."""
    
    _plugins: Dict[str, Dict[str, Any]] = {}
    _instances: Dict[str, TransformPlugin] = {}

    @classmethod
    def load_plugins(cls, plugins_dir: str = None):
        """Scans the plugins directory for plugin.json manifests."""
        if not plugins_dir:
            plugins_dir = os.path.dirname(os.path.abspath(__file__))
            
        cls._plugins.clear()
        cls._instances.clear()
        
        for root, dirs, files in os.walk(plugins_dir):
            if "plugin.json" in files:
                manifest_path = os.path.join(root, "plugin.json")
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
                    
                    plugin_id = manifest.get("id") or manifest.get("name", "").lower().replace(" ", "_")
                    entrypoint = manifest.get("entrypoint", "plugin.py")
                    entrypoint_path = os.path.join(root, entrypoint)
                    
                    if not os.path.exists(entrypoint_path):
                        logger.error(f"Plugin {plugin_id} entrypoint {entrypoint_path} missing.")
                        continue
                        
                    # Store manifest
                    manifest["__path"] = entrypoint_path
                    manifest["id"] = plugin_id
                    cls._plugins[plugin_id] = manifest
                    logger.info(f"Discovered plugin: {manifest.get('name')} ({plugin_id})")
                    
                except Exception as e:
                    logger.error(f"Failed to load plugin manifest at {manifest_path}: {e}")

    @classmethod
    def get_all_manifests(cls) -> List[Dict[str, Any]]:
        return list(cls._plugins.values())

    @classmethod
    def get_plugin_instance(cls, plugin_id: str) -> Optional[TransformPlugin]:
        if plugin_id in cls._instances:
            return cls._instances[plugin_id]
            
        manifest = cls._plugins.get(plugin_id)
        if not manifest:
            return None
            
        # Dynamically load the module
        module_path = manifest["__path"]
        module_name = f"osintgraph.plugins.{plugin_id}"
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the TransformPlugin subclass in the module
            plugin_class = None
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, TransformPlugin) and attr is not TransformPlugin:
                    plugin_class = attr
                    break
                    
            if not plugin_class:
                logger.error(f"No TransformPlugin subclass found in {module_path}")
                return None
                
            # Instantiate and inject manifest
            instance = plugin_class()
            instance.manifest = manifest
            cls._instances[plugin_id] = instance
            return instance
            
        except Exception as e:
            logger.error(f"Failed to load plugin module {plugin_id}: {e}")
            return None


# Initialize registry when module is imported
PluginRegistry.load_plugins()
