"""OSINTGraph — point d'entrée Streamlit."""
from __future__ import annotations

import sys
from pathlib import Path

# Racine du dépôt dans le path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from ui.services.backend import ensure_backend, global_search
from ui.views.carnet import render_carnet
from ui.views.dossier_hub import render_dossier_hub
from ui.views.dossiers import render_dossiers
from ui.views.graph import render_graph
from ui.views.person import render_person
from ui.views.trash import render_trash

st.set_page_config(
    page_title="OSINTGraph",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS minimal — thème sombre
st.markdown("""
<style>
    .stApp { background-color: #0f1419; }
    [data-testid="stSidebar"] { background-color: #1a1f2e; }
</style>
""", unsafe_allow_html=True)

# Session state defaults
for key, default in [
    ("page", "dossiers"),
    ("dossier_id", None),
    ("carnet_id", None),
    ("entity_id", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

ensure_backend()

# Recherche globale (sidebar)
with st.sidebar:
    st.header("🔍 Recherche")
    query = st.text_input("Rechercher", placeholder="Nom, pseudo, email…")
    if query and len(query) >= 2:
        results = global_search(query)
        if results:
            for r in results[:10]:
                label = r.get("label", "")
                rtype = r.get("entity_type", "")
                match = r.get("match_type", "")
                if st.button(f"{label} ({rtype})", key=f"srch_{r['id']}"):
                    st.session_state.page = "person"
                    st.session_state.entity_id = r["id"]
                    st.session_state.dossier_id = r.get("dossier_id")
                    st.rerun()
                st.caption(f"{match} · {r.get('dossier_name', '')}")
        else:
            st.caption("Aucun résultat")

    st.divider()
    st.caption("OSINTGraph v0.2 — sources ouvertes uniquement")

# Routage
page = st.session_state.page
if page == "dossiers":
    render_dossiers()
elif page == "trash":
    render_trash()
elif page == "dossier":
    render_dossier_hub()
elif page == "carnet":
    render_carnet()
elif page == "graph":
    render_graph()
elif page == "person":
    render_person()
else:
    st.session_state.page = "dossiers"
    st.rerun()
