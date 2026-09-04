"""Composants UI Streamlit partagés."""
from __future__ import annotations

import streamlit as st


def render_empty_dossier_onboarding(*, open_graph_key: str = "onboarding_graph") -> None:
    """Bandeau d'accueil pour un dossier sans entités (aligné sur React DossierPage)."""
    st.info(
        "**Bienvenue dans votre investigation** — Ce dossier est vide. "
        "Voici comment démarrer :"
    )
    st.markdown(
        """
1. **Commencez par le graphe complet** — ajoutez des entités et lancez des transforms OSINT
2. **Utilisez Notes** — capture rapide sans ouvrir le graphe
3. **Chronologie** — se remplit automatiquement quand vous collectez des observations
        """
    )
    if st.button("🔀 Ouvrir le graphe complet", key=open_graph_key, type="primary"):
        st.session_state.page = "graph"
        st.rerun()


def render_first_run_panel(*, on_seed_demo) -> None:
    """Panneau d'accueil quand aucun dossier n'existe."""
    st.markdown("### Première investigation ?")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            "**Option A — Démo guidée**  \n"
            "Charge un dossier TEST avec personnes, comptes et relations fictifs."
        )
        if st.button("📦 Charger la démo", type="primary", use_container_width=True):
            message, ok = on_seed_demo()
            if ok:
                st.success(message)
            else:
                st.warning(message)
            st.rerun()
    with col2:
        st.markdown(
            "**Option B — Dossier vierge**  \n"
            "Créez votre propre investigation via le formulaire ci-dessous."
        )
