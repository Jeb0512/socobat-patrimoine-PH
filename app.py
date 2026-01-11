import streamlit as st
import pandas as pd
import os

# CONFIGURATION SANS FAILLE
st.set_page_config(page_title="Socobat Asset", layout="wide")

# CSS "TOTAL WHITE" (Force le blanc sur iPhone)
st.markdown("""
    <style>
    html, body, .stApp { background-color: white !important; color: black !important; }
    input, [data-baseweb="select"] { 
        background-color: #F0F2F6 !important; 
        color: black !important; 
        -webkit-text-fill-color: black !important;
    }
    .m-card {
        background: white; padding: 20px; border-radius: 15px;
        border: 1px solid #E1E8ED; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# LOGIN
if "auth" not in st.session_state:
    st.markdown("<h2 style='text-align:center;'>🏢 Socobat Asset</h2>", unsafe_allow_html=True)
    pw = st.text_input("Code secret", type="password")
    if st.button("Se connecter", use_container_width=True):
        if pw == "SOCOBAT2026":
            st.session_state["auth"] = True
            st.rerun()
        else: st.error("Code incorrect")
    st.stop()

# VÉRIFICATION DES FICHIERS
f1 = "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx"
f4 = "4 - UG SURFACES - NOVEMBRE 2024.xlsx"

if not os.path.exists(f1) or not os.path.exists(f4):
    st.error("⚠️ Fichiers Excel manquants sur GitHub !")
    st.write("Vérifiez que les fichiers sont bien nommés exactement comme dans le code.")
    st.stop()

# CHARGEMENT ET AFFICHAGE
@st.cache_data
def load():
    du = pd.read_excel(f4, sheet_name="SURFACES DES UG", dtype=str)
    dc = pd.read_excel(f1, sheet_name="COLLECTIF + TRAVAUX", dtype=str)
    return du, dc

try:
    du, dc = load()
    st.markdown("### A votre service by Jeb 😉")
    
    # CHAMPS DE SÉLECTION (FORCÉS)
    hp2_list = sorted(du['GROUPE (HP2)'].dropna().unique())
    sel_h = st.selectbox("1. Choisir le Groupe HP2", hp2_list, index=None)
    
    if sel_h:
        ug_list = sorted(du[du['GROUPE (HP2)'] == sel_h]['N° UG'].unique())
        sel_u = st.selectbox("2. Choisir l'Unité UG", ug_list, index=None)
        
        if sel_u:
            u = du[(du['GROUPE (HP2)'] == sel_h) & (du['N° UG'] == sel_u)].iloc[0]
            
            # Calcul surface immeuble
            du['SURFACE HABITABLE (SHA)'] = pd.to_numeric(du['SURFACE HABITABLE (SHA)'], errors='coerce')
            s_imm = du[du['GROUPE (HP2)'] == sel_h]['SURFACE HABITABLE (SHA)'].sum()
            
            st.divider()
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f'<div class="m-card"><b>Logement</b><br><h2>{u["SURFACE HABITABLE (SHA)"]} m²</h2><p>Type {u["Type"]}</p></div>', unsafe_allow_html=True)
            with col2 if 'col2' in locals() else c2: # Securité colonnes
                st.markdown(f'<div class="m-card"><b>Immeuble</b><br><h2>{int(s_imm)} m²</h2><p>{len(du[du["GROUPE (HP2)"]==sel_h])} logements</p></div>', unsafe_allow_html=True)

except Exception as e:
    st.warning("Sélectionnez un groupe pour afficher les données.")
