"""Export graphe JSON / CSV / Markdown."""
from __future__ import annotations

import json
from typing import Any


def export_json(nodes: list[dict], edges: list[dict]) -> str:
    return json.dumps({"nodes": nodes, "edges": edges}, indent=2, ensure_ascii=False)


def export_csv(nodes: list[dict]) -> str:
    header = ["id", "type", "label", "properties"]
    rows = []
    for n in nodes:
        props = json.dumps(n.get("properties") or {}, ensure_ascii=False).replace('"', '""')
        label = str(n.get("label", "")).replace('"', '""')
        rows.append(f'"{n.get("id")}","{n.get("type")}","{label}","{props}"')
    return ",".join(header) + "\n" + "\n".join(rows)


def export_markdown(nodes: list[dict], edges: list[dict]) -> str:
    md = "# OSINTGraph Export\n\n## Nodes\n\n"
    if not nodes:
        md += "Aucun nœud.\n\n"
    else:
        for n in nodes:
            md += f"- **{n.get('label')}** ({n.get('type')}) `id: {n.get('id')}`\n"
            for k, v in (n.get("properties") or {}).items():
                md += f"  - {k}: {v}\n"
        md += "\n"

    md += "## Edges\n\n"
    if not edges:
        md += "Aucune arête.\n"
    else:
        node_map = {n["id"]: n.get("label", n["id"]) for n in nodes}
        for e in edges:
            src = node_map.get(e.get("source"), e.get("source"))
            tgt = node_map.get(e.get("target"), e.get("target"))
            md += f"- {src} --[{e.get('type')}]--> {tgt}\n"
    return md


def parse_import_json(raw: str) -> dict[str, Any]:
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("JSON invalide : objet attendu")
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("Format invalide : nodes et edges requis")
    return {"nodes": nodes, "edges": edges}
