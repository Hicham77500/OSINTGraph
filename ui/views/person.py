"""Vue fiche personne / entité."""
from __future__ import annotations

import json

import streamlit as st

from ui.services import backend as api


def render_person() -> None:
    dossier_id = st.session_state.get("dossier_id")
    entity_id = st.session_state.get("entity_id")
    if not entity_id:
        st.session_state.page = "dossier" if dossier_id else "dossiers"
        st.rerun()
        return

    if st.button("← Retour"):
        st.session_state.page = "dossier" if dossier_id else "dossiers"
        st.session_state.entity_id = None
        st.rerun()

    entity = api.get_entity(entity_id)
    observations = api.get_observations(entity_id)
    relations = api.get_entity_relations(entity_id)
    readiness = api.get_readiness(entity_id)

    st.title(entity.label)
    st.caption(f"{entity.entity_type} · Confiance {int(entity.confidence * 100)}% · {entity.status}")

    tabs = st.tabs(["Vue d'ensemble", "Observations", "Relations", "IA"])

    with tabs[0]:
        st.subheader("Propriétés")
        if entity.properties:
            st.json(entity.properties)
        else:
            st.caption("Aucune propriété")
        st.metric("Score de préparation IA", f"{readiness.score}/100")
        st.caption(readiness.message)
        for key, val in (readiness.factors or {}).items():
            st.caption(f"• {key}: {val}")

    with tabs[1]:
        if not observations:
            st.info("Aucune observation")
        for obs in observations:
            with st.container(border=True):
                content = obs.get("content") or {}
                st.markdown(f"**{obs.get('platform')}** — {obs.get('collection_method')}")
                st.write(content.get("value") or json.dumps(content, ensure_ascii=False))
                st.caption(f"{obs.get('status')} · collecté {obs.get('collected_at')}")

    with tabs[2]:
        if not relations:
            st.info("Aucune relation")
        for rel in relations:
            st.markdown(f"**{rel.relation_type}** → `{rel.target_entity_id}`")
            st.caption(f"Confiance {int(rel.confidence * 100)}% · {rel.status}")

    with tabs[3]:
        if readiness.sufficient:
            if st.button("Lancer l'analyse IA", type="primary"):
                with st.spinner("Analyse en cours…"):
                    result = api.run_ai_analysis(entity_id)
                st.warning("⚠️ Hypothèse IA — à confirmer par l'analyste")
                st.markdown(f"**{result.claim}**")
                st.caption(f"Confiance : {int(result.confidence * 100)}%")
                if result.evidence_ids:
                    st.write(f"Preuves : {len(result.evidence_ids)} référence(s)")
        else:
            st.info(f"Score insuffisant ({readiness.score}/{readiness.threshold}). Enrichissez la fiche avant l'analyse IA.")
