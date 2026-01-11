import streamlit as st
import pandas as pd

# 1. CONFIGURATION
st.set_page_config(page_title="Socobat Asset - Jeb", layout="wide")

# 2. CSS ULTRA-PRIORITAIRE (FORCE LE BLANC & NOIR)
st.markdown("""
    <style>
    /* 1. FORCE LE FOND DE L'APP */
    .stApp, [data-testid="stAppViewContainer"], .main {
        background-color: white !important;
    }

    /* 2. FORCE LE TEXTE NOIR PARTOUT */
    h1, h2, h3, p, span, label, div {
        color: black !important;
    }

    /* 3. FORCE LES CHAMPS DE SAISIE EN BLANC (ANTI-FOND NOIR) */
    div[data-baseweb="select"], div[data-baseweb="base-input"], input {
        background-color: white !important;
        border: 1px solid #ccc !important;
    }
    
    /* 4. FORCE LE TEXTE DANS LES CHAMPS EN NOIR */
    input, div[data-baseweb="select"] * {
        color: black !important;
        -webkit-text-fill-color: black !important;
    }

    /* 5. STYLE DES CARTES (DESIGN MAKE) */
    .jeb-card {
        background-color: white !important;
        border: 1px solid #eee !important;
        border-radius: 15px !important;
        padding: 20px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
        margin-bottom: 20px !important;
    }
    
    /* 6. STYLE DES TITRES DANS LES CARTES */
    .card-label { font-size: 0.8rem; font-weight: 700; color: #666 !important; text-transform: uppercase; }
    .card-value { font-size: 2rem; font-weight: 800; color: black !important; margin: 10px 0; }
    .card-icon { font-size: 1.5rem; margin-right: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 3. AUTHENTIFICATION
if "auth" not in st.session_state:
    st.markdown("<h1 style='text-align:center;'>🏢 Socobat</h1>", unsafe_allow_html=True)
    pw = st.text_input("Code secret", type="password")
    if st.button("Se connecter"):
        if pw == "SOCOBAT2026":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# 4. CHARGEMENT DATA
@st.cache_data
def load():
    f1 = "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx"
    f4 = "4 - UG SURFACES - NOVEMBRE 2024.xlsx"
    du = pd.read_excel(f4, sheet_name="SURFACES DES UG", dtype=str)
    dc = pd.read_excel(f1, sheet_name="COLLECTIF + TRAVAUX", dtype=str)
    return du, dc

try:
    du, dc = load()
    
    st.markdown("<h1>🏢 A votre service by Jeb 😉</h1>", unsafe_allow_html=True)

    # RECHERCHE
    c1, c2 = st.columns(2)
    with c1:
        hp2_list = sorted(du['GROUPE (HP2)'].dropna().unique())
        sel_h = st.selectbox("Choisir le Groupe HP2", hp2_list, index=None)
    
    if sel_h:
        with c2:
            ug_list = sorted(du[du['GROUPE (HP2)'] == sel_h]['N° UG'].unique())
            sel_u = st.selectbox("Choisir l'Unité UG", ug_list, index=None)

        if sel_u:
            u_row = du[(du['GROUPE (HP2)'] == sel_h) & (du['N° UG'] == sel_u)].iloc[0]
            
            # Calcul surface immeuble
            du['SHA_NUM'] = pd.to_numeric(du['SURFACE HABITABLE (SHA)'], errors='coerce')
            s_imm = du[du['GROUPE (HP2)'] == sel_h]['SHA_NUM'].sum()
            
            st.markdown(f"<h3>📍 {u_row['NOM GROUPE']}</h3>", unsafe_allow_html=True)

            # AFFICHAGE CARTES (ICONÉES RÉINTÉGRÉES DANS LE HTML)
            cola, colb = st.columns(2)
            with cola:
                st.markdown(f"""
                <div class="jeb-card">
                    <div class="card-label"><span class="card-icon">🏠</span>LOGEMENT</div>
                    <div class="card-value">{u_row['SURFACE HABITABLE (SHA)']} m²</div>
                    <div style="color:blue !important; font-weight:bold;">Type {u_row['Type']} • Etage {u_row['Etage']}</div>
                </div>
                """, unsafe_allow_html=True)
            with colb:
                st.markdown(f"""
                <div class="jeb-card">
                    <div class="card-label"><span class="card-icon">🏢</span>IMMEUBLE</div>
                    <div class="card-value">{int(s_imm):,} m²</div>
                    <div style="color:blue !important; font-weight:bold;">{len(du[du['GROUPE (HP2)'] == sel_h])} Logements</div>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.info("En attente de sélection...")
