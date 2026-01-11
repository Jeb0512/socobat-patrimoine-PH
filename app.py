import streamlit as st
import pandas as pd

# CONFIGURATION AVEC ICONE
st.set_page_config(page_title="Socobat Asset", layout="wide", page_icon="🏢")

# DESIGN SYSTEM "MAKE" (SANS AUCUN FOND NOIR)
st.markdown("""
    <style>
    /* Force le blanc sur iPhone */
    .stApp, html, body, [data-testid="stAppViewContainer"] {
        background-color: #F4F7F9 !important;
        color: #1A1C21 !important;
    }
    /* Style des cartes */
    .m-card {
        background: white !important;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #E1E8ED;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        margin-bottom: 15px;
    }
    /* Champs de saisie BLANCS */
    input, [data-baseweb="select"] {
        background-color: white !important;
        color: black !important;
        -webkit-text-fill-color: black !important;
    }
    .stButton>button {
        background-color: #111827 !important;
        color: white !important;
        border-radius: 10px;
        width: 100%;
        height: 50px;
    }
    </style>
""", unsafe_allow_html=True)

# LOGIN
if "auth" not in st.session_state:
    st.markdown("<div style='text-align:center; padding-top:50px;'><h1>🏢 Socobat</h1><p>Accès réservé</p></div>", unsafe_allow_html=True)
    pw = st.text_input("Code secret", type="password")
    if st.button("Se connecter"):
        if pw == "SOCOBAT2026":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# DATA & AFFICHAGE
@st.cache_data
def load():
    du = pd.read_excel("4 - UG SURFACES - NOVEMBRE 2024.xlsx", sheet_name="SURFACES DES UG", dtype={'N° UG': str, 'GROUPE (HP2)': str})
    dc = pd.read_excel("1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx", sheet_name="COLLECTIF + TRAVAUX", dtype={'HP2': str})
    return du, dc

try:
    du, dc = load()
    st.title("A votre service 😉")
    
    sel_h = st.selectbox("Groupe HP2", sorted(du['GROUPE (HP2)'].unique()), index=None)
    if sel_h:
        sel_u = st.selectbox("Unité UG", sorted(du[du['GROUPE (HP2)'] == sel_h]['N° UG'].unique()), index=None)
        
        if sel_u:
            u = du[(du['GROUPE (HP2)'] == sel_h) & (du['N° UG'] == sel_u)].iloc[0]
            s_imm = du[du['GROUPE (HP2)'] == sel_h]['SURFACE HABITABLE (SHA)'].sum()
            
            st.info(f"📍 {u['NOM GROUPE']}")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f'<div class="m-card"><b>Logement</b><br><h2>{u["SURFACE HABITABLE (SHA)"]} m²</h2></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="m-card"><b>Immeuble</b><br><h2>{int(s_imm)} m²</h2></div>', unsafe_allow_html=True)
except Exception as e:
    st.write("En attente de sélection...")
