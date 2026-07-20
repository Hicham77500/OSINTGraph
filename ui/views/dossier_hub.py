"""Hub dossier — carnets et accès graphe."""
from __future__ import annotations

import streamlit as st

from ui.services import backend as api

NOTEBOOK_LABELS = {
    "personnes": "👤 Personnes",
    "reseaux_sociaux": "📱 Réseaux sociaux",
    "entreprises": "🏢 Entreprises",
    "pseudonymes": "🎭 Pseudonymes",
    "telephones": "📞 Téléphones",
    "emails": "✉️ Emails",
    "domaines": "🌐 Domaines",
    "evenements": "📅 Événements",
    "chronologie": "⏱️ Chronologie",
    "notes": "📝 Notes",
    "custom": "📋 Carnet",
}


def render_dossier_hub() -> None:
    dossier_id = st.session_state.get("dossier_id")
    if not dossier_id:
        st.session_state.page = "dossiers"
        st.rerun()
        return

    if st.button("← Retour aux dossiers"):
        st.session_state.page = "dossiers"
        st.session_state.dossier_id = None
        st.rerun()

    dossier = api.get_dossier(dossier_id)
    carnets = api.list_carnets(dossier_id)

    st.title(dossier.name)
    if dossier.description:
        st.write(dossier.description)

    stats = dossier.stats or {}
    st.caption(
        f"👤 {stats.get('persons', 0)} · 🔗 {stats.get('accounts', 0)} · ↔ {stats.get('relations', 0)}"
    )

    col_del, col_graph = st.columns([1, 3])
    with col_del:
        if st.button("🗑️ Supprimer le dossier"):
            api.soft_delete_dossier(dossier_id)
            st.session_state.page = "dossiers"
            st.session_state.dossier_id = None
            st.rerun()
    with col_graph:
        if st.button("🔀 Ouvrir le graphe complet", type="primary", use_container_width=True):
            st.session_state.page = "graph"
            st.rerun()

    st.divider()
    st.subheader("Axes d'investigation")

    cols = st.columns(3)
    for i, c in enumerate(carnets):
        label = NOTEBOOK_LABELS.get(c.notebook_type, c.name)
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"**{label}**")
                st.caption(f"{c.entity_count} entité(s)")
                if st.button("Ouvrir", key=f"carnet_{c.id}", use_container_width=True):
                    st.session_state.page = "carnet"
                    st.session_state.carnet_id = c.id
                    st.rerun()

    with st.expander("➕ Nouveau carnet"):
        new_name = st.text_input("Nom du carnet")
        nb_type = st.selectbox("Type", list(NOTEBOOK_LABELS.keys()), index=len(NOTEBOOK_LABELS) - 1)
        if st.button("Créer le carnet"):
            if new_name.strip():
                api.create_carnet(dossier_id, new_name.strip(), nb_type)
                st.rerun()
