import streamlit as st
import pandas as pd
import base64

# 1. CONFIGURATION
st.set_page_config(page_title="Socobat Asset", layout="wide", initial_sidebar_state="collapsed")

# 2. DESIGN SYSTEM ALAN (FORCE LE BLANC ABSOLU)
st.markdown("""
    <style>
    /* FORCE LE BLANC MÊME EN MODE SOMBRE IPHONE */
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        background-color: #F9FAFB !important;
        color: #111827 !important;
    }

    /* CHAMPS DE SAISIE : BLANC ET TEXTE NOIR */
    div[data-baseweb="select"], div[data-baseweb="base-input"], input {
        background-color: white !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 12px !important;
    }
    
    /* FORCE LE TEXTE DES OPTIONS EN NOIR */
    div[role="listbox"] div, div[data-baseweb="select"] span {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
    }

    /* STYLE ALAN CARDS */
    .alan-card {
        background-color: white !important;
        padding: 24px !important;
        border-radius: 20px !important;
        border: 1px solid #E5E7EB !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 16px !important;
    }

    .t-label { color: #6B7280 !important; font-size: 0.75rem !important; font-weight: 700 !important; text-transform: uppercase; margin-bottom: 8px; }
    .t-value { color: #111827 !important; font-size: 2.2rem !important; font-weight: 800 !important; letter-spacing: -1.5px; line-height: 1; }
    .t-sub { color: #6366F1 !important; font-size: 0.85rem !important; font-weight: 600 !important; margin-top: 8px; }

    /* BOUTON LOGIN STYLE ALAN */
    .stButton>button {
        background-color: #6366f1 !important;
        color: white !important;
        border-radius: 100px !important;
        font-weight: 700 !important;
        width: 100%;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ACCÈS SÉCURISÉ (PAGE BLANCHE)
if "auth" not in st.session_state:
    st.markdown("<div style='text-align:center; padding-top:80px;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='color:#111827;'>🏢 Socobat Asset</h1><p style='color:#6B7280;'>By Jeb 😉</p>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1,2,1])
    with mid:
        code = st.text_input("Tapez le code secret", type="password")
        if st.button("Se connecter"):
            if code == "SOCOBAT2026":
                st.session_state["auth"] = True
                st.rerun()
            else: st.error("Code erroné")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 4. DATA
@st.cache_data
def load():
    f1 = "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx"
    f4 = "4 - UG SURFACES - NOVEMBRE 2024.xlsx"
    du = pd.read_excel(f4, sheet_name="SURFACES DES UG", dtype=str)
    dc = pd.read_excel(f1, sheet_name="COLLECTIF + TRAVAUX", dtype=str)
    return du, dc

try:
    du, dc = load()
    
    # HEADER LOGO + TITRE
    st.markdown("<h1 style='color:#111827; margin-bottom:20px;'>A votre service by Jeb 😉</h1>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        sel_h = st.selectbox("Choisir le Groupe HP2", sorted(du['GROUPE (HP2)'].dropna().unique()), index=None)
    
    if sel_h:
        with c2:
            sel_u = st.selectbox("Choisir l'Unité UG", sorted(du[du['GROUPE (HP2)'] == sel_h]['N° UG'].unique()), index=None)

        if sel_u:
            u = du[(du['GROUPE (HP2)'] == sel_h) & (du['N° UG'] == sel_u)].iloc[0]
            du['SHA_N'] = pd.to_numeric(du['SURFACE HABITABLE (SHA)'], errors='coerce')
            s_imm = du[du['GROUPE (HP2)'] == sel_h]['SHA_N'].sum()
            
            st.markdown(f"<p style='color:#6366F1; font-weight:700; margin-left:5px;'>📍 {u['NOM GROUPE']}</p>", unsafe_allow_html=True)

            cola, colb = st.columns(2)
            with cola:
                st.markdown(f"""
                <div class="alan-card">
                    <div class="t-label">🏠 LOGEMENT PERSONNEL</div>
                    <div class="t-value">{u['SURFACE HABITABLE (SHA)']} m²</div>
                    <div class="t-sub">Type {u['Type']} • Etage {u['Etage']}</div>
                </div>
                """, unsafe_allow_html=True)
            with colb:
                st.markdown(f"""
                <div class="alan-card">
                    <div class="t-label">🏢 SURFACE IMMEUBLE</div>
                    <div class="t-value">{int(s_imm):,} m²</div>
                    <div class="t-sub">{len(du[du['GROUPE (HP2)'] == sel_h])} Logements</div>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.info("Sélectionnez un groupe pour afficher les données.")
