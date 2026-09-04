"""Navigation sidebar Streamlit."""
from __future__ import annotations

import streamlit as st


def render_sidebar_nav() -> None:
    st.subheader("Navigation")
    if st.button("📁 Mes dossiers", use_container_width=True):
        st.session_state.page = "dossiers"
        st.session_state.dossier_id = None
        st.session_state.carnet_id = None
        st.session_state.entity_id = None
        st.rerun()

    if st.button("🗑️ Corbeille", use_container_width=True):
        st.session_state.page = "trash"
        st.rerun()

    dossier_id = st.session_state.get("dossier_id")
    if dossier_id and st.session_state.page in ("dossier", "carnet", "graph", "person"):
        st.caption("Dossier ouvert")
        if st.button("📂 Hub dossier", use_container_width=True):
            st.session_state.page = "dossier"
            st.session_state.carnet_id = None
            st.session_state.entity_id = None
            st.rerun()
        if st.button("🔀 Graphe", use_container_width=True):
            st.session_state.page = "graph"
            st.rerun()

    st.divider()
    with st.expander("ℹ️ Aide rapide"):
        st.markdown(
            """
**React (complet)** : `npm run dev` → :5173  
**Streamlit (cloud)** : preview ou Streamlit Cloud  
**Démo** : bouton « Charger la démo » sur l'accueil  

Docs : [GETTING_STARTED.md](https://github.com/Hicham77500/OSINTGraph/blob/main/docs/GETTING_STARTED.md)
            """
        )
