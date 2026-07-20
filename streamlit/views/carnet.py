"""Vue carnet — entités, notes, chronologie."""
from __future__ import annotations

import streamlit as st

from streamlit.services import backend as api

NOTEBOOK_ENTITY_TYPES: dict[str, list[str]] = {
    "personnes": ["PERSON"],
    "reseaux_sociaux": ["SOCIAL_ACCOUNT", "USERNAME"],
    "entreprises": ["ORGANIZATION"],
    "pseudonymes": ["ALIAS", "USERNAME"],
}


def _filter_entities(entities, notebook_type: str):
    allowed = NOTEBOOK_ENTITY_TYPES.get(notebook_type)
    if not allowed:
        return entities
    return [e for e in entities if e.entity_type in allowed]


def render_carnet() -> None:
    dossier_id = st.session_state.get("dossier_id")
    carnet_id = st.session_state.get("carnet_id")
    if not dossier_id or not carnet_id:
        st.session_state.page = "dossiers"
        st.rerun()
        return

    carnets = api.list_carnets(dossier_id)
    carnet = next((c for c in carnets if c.id == carnet_id), None)
    if not carnet:
        st.error("Carnet introuvable")
        return

    if st.button("← Retour au dossier"):
        st.session_state.page = "dossier"
        st.session_state.carnet_id = None
        st.rerun()

    st.title(carnet.name)
    st.caption(f"Type : {carnet.notebook_type}")

    entities = api.list_entities(dossier_id, carnet_id)
    filtered = _filter_entities(entities, carnet.notebook_type)

    if carnet.notebook_type == "notes":
        _render_notes(dossier_id, carnet_id, entities)
    elif carnet.notebook_type == "chronologie":
        _render_timeline(filtered)
    else:
        _render_entity_list(dossier_id, carnet_id, filtered)


def _render_entity_list(dossier_id: str, carnet_id: str, entities) -> None:
    with st.expander("➕ Ajouter une entité"):
        label = st.text_input("Libellé")
        etype = st.selectbox(
            "Type",
            ["PERSON", "USERNAME", "SOCIAL_ACCOUNT", "ORGANIZATION", "EMAIL", "PHONE", "DOMAIN", "IP", "ALIAS"],
        )
        if st.button("Ajouter", type="primary"):
            if label.strip():
                api.create_entity(dossier_id, {
                    "entity_type": etype,
                    "label": label.strip(),
                    "carnet_id": carnet_id,
                })
                st.rerun()

    if not entities:
        st.info("Aucune entité dans ce carnet.")
        return

    for e in entities:
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                st.markdown(f"**{e.label}** `{e.entity_type}`")
                st.caption(f"Confiance {int(e.confidence * 100)}% · {e.status}")
            with c2:
                if e.entity_type == "PERSON" and st.button("Fiche", key=f"person_{e.id}"):
                    st.session_state.page = "person"
                    st.session_state.entity_id = e.id
                    st.rerun()
            with c3:
                if st.button("🗑️", key=f"del_{e.id}"):
                    api.delete_entity(e.id)
                    st.rerun()


def _render_notes(dossier_id: str, carnet_id: str, entities) -> None:
    with st.expander("➕ Nouvelle note"):
        title = st.text_input("Titre")
        body = st.text_area("Contenu")
        if st.button("Enregistrer la note", type="primary"):
            if title.strip():
                api.create_entity(dossier_id, {
                    "entity_type": "NOTE",
                    "label": title.strip(),
                    "carnet_id": carnet_id,
                    "properties": {"body": body, "title": title.strip()},
                })
                st.rerun()

    notes = [e for e in entities if e.entity_type == "NOTE"]
    if not notes:
        st.info("Aucune note.")
        return

    for n in notes:
        props = n.properties or {}
        with st.container(border=True):
            st.markdown(f"**{props.get('title', n.label)}**")
            st.write(props.get("body", ""))
            if st.button("Supprimer", key=f"note_del_{n.id}"):
                api.delete_entity(n.id)
                st.rerun()


def _render_timeline(entities) -> None:
    entries = []
    for e in entities:
        for obs in api.get_observations(e.id):
            content = obs.get("content") or {}
            if not isinstance(content, dict):
                content = {}
            summary = content.get("value") or content.get("field") or str(content)
            entries.append({
                "date": obs.get("observed_at") or obs.get("collected_at"),
                "entity": e.label,
                "entity_id": e.id,
                "summary": summary,
                "platform": obs.get("platform", ""),
            })

    entries.sort(key=lambda x: x["date"] or "", reverse=True)
    if not entries:
        st.info("Aucun événement dans la chronologie.")
        return

    for entry in entries:
        with st.container(border=True):
            st.caption(f"{entry['date']} · {entry['platform']}")
            st.markdown(f"**{entry['entity']}** — {entry['summary']}")
