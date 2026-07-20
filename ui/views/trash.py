"""Vue corbeille."""
from __future__ import annotations

import streamlit as st

from ui.services import backend as api


def render_trash() -> None:
    if st.button("← Retour aux dossiers"):
        st.session_state.page = "dossiers"
        st.rerun()

    st.title("Corbeille")
    st.caption("Dossiers supprimés — restauration ou suppression définitive")

    trash = api.list_trash_dossiers()
    if not trash:
        st.info("La corbeille est vide.")
        return

    for d in trash:
        with st.container(border=True):
            st.subheader(d.name)
            if d.deleted_at:
                st.caption(f"Supprimé le {d.deleted_at}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("♻️ Restaurer", key=f"restore_{d.id}", use_container_width=True):
                    api.restore_dossier(d.id)
                    st.success("Dossier restauré")
                    st.rerun()
            with c2:
                if st.button("🗑️ Supprimer définitivement", key=f"perm_{d.id}", use_container_width=True):
                    api.permanent_delete_dossier(d.id)
                    st.success("Dossier supprimé définitivement")
                    st.rerun()
