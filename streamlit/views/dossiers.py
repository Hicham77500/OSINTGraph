"""Vue liste des dossiers."""
from __future__ import annotations

import streamlit as st

from streamlit.services import backend as api


def render_dossiers() -> None:
    st.title("OSINTGraph")
    st.caption("Investigations OSINT — sources ouvertes et données analyste uniquement")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ Corbeille", use_container_width=True):
            st.session_state.page = "trash"
            st.rerun()

    dossiers = api.list_dossiers()

    with st.expander("➕ Nouveau dossier", expanded=False):
        name = st.text_input("Nom du dossier", key="new_dossier_name")
        desc = st.text_area("Description (optionnel)", key="new_dossier_desc")
        if st.button("Créer", type="primary"):
            if name.strip():
                api.create_dossier(name.strip(), desc.strip() or None)
                st.success(f"Dossier « {name} » créé")
                st.rerun()
            else:
                st.warning("Le nom est requis")

    if not dossiers:
        st.info("Aucun dossier. Créez votre première investigation ci-dessus.")
        return

    for d in dossiers:
        stats = d.stats or {}
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                st.subheader(d.name)
                if d.description:
                    st.write(d.description)
                st.caption(
                    f"👤 {stats.get('persons', 0)} personnes · "
                    f"🔗 {stats.get('accounts', 0)} comptes · "
                    f"↔ {stats.get('relations', 0)} relations"
                )
            with c2:
                if st.button("Ouvrir", key=f"open_{d.id}", use_container_width=True):
                    st.session_state.page = "dossier"
                    st.session_state.dossier_id = d.id
                    st.rerun()
