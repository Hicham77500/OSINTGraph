"""Vue graphe — visualisation, édition, transforms, import/export."""
from __future__ import annotations

import json
import uuid

import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components

from streamlit.services import backend as api
from streamlit.services.export_utils import export_csv, export_json, export_markdown, parse_import_json

NODE_COLORS = {
    "PERSON": "#4a9eff",
    "USERNAME": "#a78bfa",
    "SOCIAL_ACCOUNT": "#34d399",
    "ORGANIZATION": "#fbbf24",
    "EMAIL": "#f87171",
    "PHONE": "#fb923c",
    "DOMAIN": "#38bdf8",
    "IP": "#94a3b8",
    "ALIAS": "#c084fc",
    "LOCATION": "#2dd4bf",
    "default": "#64748b",
}


def _workspace_id(dossier_id: str) -> str:
    dossier = api.get_dossier(dossier_id)
    return dossier.workspace_id or dossier_id


def _render_pyvis(nodes: list[dict], edges: list[dict], height: int = 500) -> None:
    net = Network(height=f"{height}px", width="100%", bgcolor="#0f1419", font_color="#e2e8f0", directed=True)
    net.set_options("""
    {
      "physics": {"enabled": true, "barnesHut": {"gravitationalConstant": -8000}},
      "interaction": {"hover": true, "navigationButtons": true}
    }
    """)
    for n in nodes:
        color = NODE_COLORS.get(n.get("type", ""), NODE_COLORS["default"])
        net.add_node(n["id"], label=n.get("label", n["id"]), title=n.get("type", ""), color=color)
    for e in edges:
        net.add_edge(e["source"], e["target"], title=e.get("type", ""), label=e.get("label") or e.get("type", ""))
    html = net.generate_html(notebook=False)
    components.html(html, height=height + 20, scrolling=True)


def render_graph() -> None:
    dossier_id = st.session_state.get("dossier_id")
    if not dossier_id:
        st.session_state.page = "dossiers"
        st.rerun()
        return

    if st.button("← Retour au dossier"):
        st.session_state.page = "dossier"
        st.rerun()

    dossier = api.get_dossier(dossier_id)
    workspace = _workspace_id(dossier_id)
    st.title(f"Graphe — {dossier.name}")

    if "graph_data" not in st.session_state or st.session_state.get("graph_workspace") != workspace:
        st.session_state.graph_data = api.load_graph(workspace)
        st.session_state.graph_workspace = workspace

    graph = st.session_state.graph_data
    nodes: list[dict] = graph.get("nodes", [])
    edges: list[dict] = graph.get("edges", [])

    sidebar = st.sidebar
    sidebar.header("Graphe")

    # Ajout nœud
    with sidebar.expander("➕ Nœud"):
        n_label = sidebar.text_input("Libellé", key="g_node_label")
        n_type = sidebar.selectbox(
            "Type",
            ["PERSON", "USERNAME", "SOCIAL_ACCOUNT", "ORGANIZATION", "EMAIL", "PHONE", "DOMAIN", "IP", "ALIAS"],
            key="g_node_type",
        )
        if sidebar.button("Ajouter nœud"):
            if n_label.strip():
                node = {"id": str(uuid.uuid4()), "type": n_type, "label": n_label.strip(), "properties": {}}
                nodes.append(node)
                graph["nodes"] = nodes
                st.session_state.graph_data = graph
                st.rerun()

    # Ajout arête
    with sidebar.expander("🔗 Relation"):
        if len(nodes) >= 2:
            labels = {n["id"]: n.get("label", n["id"]) for n in nodes}
            src = sidebar.selectbox("Source", list(labels.keys()), format_func=lambda x: labels[x], key="g_src")
            tgt = sidebar.selectbox("Cible", list(labels.keys()), format_func=lambda x: labels[x], key="g_tgt")
            rel_type = sidebar.text_input("Type de relation", value="LINKED_TO", key="g_rel")
            if sidebar.button("Ajouter relation"):
                if src != tgt:
                    edge = {"id": str(uuid.uuid4()), "source": src, "target": tgt, "type": rel_type}
                    edges.append(edge)
                    graph["edges"] = edges
                    st.session_state.graph_data = graph
                    st.rerun()
        else:
            sidebar.caption("Ajoutez au moins 2 nœuds")

    # Transforms
    with sidebar.expander("⚡ Transforms"):
        transforms = api.list_transforms()
        if transforms:
            t_names = {t["id"]: t["name"] for t in transforms}
            t_id = sidebar.selectbox("Transform", list(t_names.keys()), format_func=lambda x: t_names[x])
            t_value = sidebar.text_input("Valeur d'entrée")
            if sidebar.button("Exécuter"):
                if t_value.strip():
                    with st.spinner("Transform en cours…"):
                        result = api.run_transform(t_id, t_value.strip())
                    if result.get("ok"):
                        new_nodes = result.get("nodes", [])
                        new_edges = result.get("edges", [])
                        existing_ids = {n["id"] for n in nodes}
                        for n in new_nodes:
                            if n["id"] not in existing_ids:
                                nodes.append(n)
                        existing_eids = {e["id"] for e in edges}
                        for e in new_edges:
                            if e["id"] not in existing_eids:
                                edges.append(e)
                        graph["nodes"] = nodes
                        graph["edges"] = edges
                        st.session_state.graph_data = graph
                        for line in result.get("log", []):
                            st.caption(line)
                        st.success(f"{len(new_nodes)} nœud(s), {len(new_edges)} arête(s) ajouté(s)")
                        st.rerun()
                    else:
                        st.error(result.get("error", "Erreur transform"))
        else:
            sidebar.caption("Aucun plugin disponible")

    # Import / Export
    with sidebar.expander("💾 Import / Export"):
        fmt = sidebar.selectbox("Format export", ["JSON", "CSV", "Markdown"])
        if sidebar.button("Exporter"):
            if fmt == "JSON":
                content = export_json(nodes, edges)
                mime = "application/json"
                ext = "json"
            elif fmt == "CSV":
                content = export_csv(nodes)
                mime = "text/csv"
                ext = "csv"
            else:
                content = export_markdown(nodes, edges)
                mime = "text/markdown"
                ext = "md"
            sidebar.download_button("Télécharger", content, f"osintgraph.{ext}", mime)

        uploaded = sidebar.file_uploader("Importer JSON", type=["json"])
        if uploaded and sidebar.button("Appliquer l'import"):
            try:
                data = parse_import_json(uploaded.read().decode("utf-8"))
                graph["nodes"] = data["nodes"]
                graph["edges"] = data["edges"]
                st.session_state.graph_data = graph
                st.success("Import appliqué")
                st.rerun()
            except (json.JSONDecodeError, ValueError) as exc:
                st.error(str(exc))

    if sidebar.button("💾 Sauvegarder", type="primary"):
        api.save_graph(workspace, graph)
        st.sidebar.success("Graphe sauvegardé")

    # Stats
    c1, c2, c3 = st.columns(3)
    c1.metric("Nœuds", len(nodes))
    c2.metric("Arêtes", len(edges))
    c3.metric("Workspace", workspace[:8] + "…")

    if nodes:
        _render_pyvis(nodes, edges)
    else:
        st.info("Graphe vide — ajoutez des nœuds via la barre latérale ou exécutez un transform.")

    # Liste nœuds pour navigation
    if nodes:
        with st.expander("Nœuds du graphe"):
            for n in nodes:
                c1, c2, c3 = st.columns([3, 1, 1])
                with c1:
                    st.text(f"{n.get('label')} ({n.get('type')})")
                with c2:
                    if n.get("type") == "PERSON":
                        if st.button("Fiche", key=f"gp_{n['id']}"):
                            st.session_state.page = "person"
                            st.session_state.entity_id = n["id"]
                            st.rerun()
                with c3:
                    if st.button("✕", key=f"gn_{n['id']}"):
                        nodes = [x for x in nodes if x["id"] != n["id"]]
                        edges = [e for e in edges if e["source"] != n["id"] and e["target"] != n["id"]]
                        graph["nodes"] = nodes
                        graph["edges"] = edges
                        st.session_state.graph_data = graph
                        st.rerun()
