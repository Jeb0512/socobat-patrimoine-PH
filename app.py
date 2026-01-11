import streamlit as st
import pandas as pd
import base64
from PIL import Image

# 1. CONFIGURATION INITIALE
st.set_page_config(page_title="Socobat Asset", layout="wide", initial_sidebar_state="collapsed")

# FONCTION POUR LE LOGO
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# 2. DESIGN SYSTEM ALAN (FORCE LE BLANC ET LES CONTRASTES)
# On injecte le CSS directement pour bloquer le mode sombre
st.markdown("""
    <style>
    /* Force le fond de l'application en blanc cassé style Alan */
    .stApp { background-color: #F9FAFB !important; }
    
    /* STYLE DES CARTES (Inspiré de ta capture Alan) */
    .alan-card {
        background-color: white !important;
        padding: 30px !important;
        border-radius: 20px !important;
        border: 1px solid #E5E7EB !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        margin-bottom: 20px !important;
    }

    /* FORCE LE TEXTE EN NOIR DANS LES CHAMPS (Fix fond noir) */
    div[data-baseweb="select"], div[data-baseweb="base-input"], input {
        background-color: white !important;
        color: #1F2937 !important;
        border-radius: 12px !important;
    }
    
    /* Fix pour le texte invisible dans les listes déroulantes */
    div[role="listbox"] div { color: #1F2937 !important; }
    label p { color: #4B5563 !important; font-weight: 600 !important; }

    /* TYPOGRAPHIE */
    .main-title { color: #111827 !important; font-weight: 800 !important; font-size: 2.2rem !important; }
    .card-label { color: #6B7280 !important; font-size: 0.85rem !important; font-weight: 700 !important; text-transform: uppercase; margin-bottom: 10px; }
    .card-value { color: #111827 !important; font-size: 2.5rem !important; font-weight: 800 !important; letter-spacing: -1px; }
    .card-sub { color: #6366F1 !important; font-weight: 600 !important; font-size: 0.95rem !important; }
    
    /* BOUTON ALAN */
    .stButton>button {
        background-color: #6366f1 !important;
        color: white !important;
        border-radius: 100px !important;
        padding: 10px 30px !important;
        border: none !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. AUTHENTIFICATION SÉCURISÉE
if "auth" not in st.session_state:
    st.markdown("<div style='text-align:center; padding-top:100px;'>", unsafe_allow_html=True)
    try:
        # Remplace par le nom exact de ton fichier logo dans GitHub
        logo_base64 = get_base64("logosocobat.jpg")
        st.markdown(f'<img src="data:image/jpeg;base64,{logo_base64}" width="200">', unsafe_allow_html=True)
    except:
        st.markdown("<h1 class='main-title'>SOCOBAT</h1>", unsafe_allow_html=True)
    
    st.markdown("<p style='color:#6B7280; margin-bottom:30px;'>Asset Management Portal • Jeb Edition</p>", unsafe_allow_html=True)
    
    _, mid, _ = st.columns([1,2,1])
    with mid:
        code = st.text_input("Code confidentiel", type="password")
        if st.button("Se connecter", use_container_width=True):
            if code == "SOCOBAT2026":
                st.session_state["auth"] = True
                st.rerun()
            else: st.error("Accès refusé")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 4. CHARGEMENT DES DONNÉES
@st.cache_data
def load_data():
    f1 = "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx"
    f4 = "4 - UG SURFACES - NOVEMBRE 2024.xlsx"
    du = pd.read_excel(f4, sheet_name="SURFACES DES UG", dtype=str)
    dc = pd.read_excel(f1, sheet_name="COLLECTIF + TRAVAUX", dtype=str)
    return du, dc

try:
    df_ug, df_coll = load_data()

    # HEADER AVEC LOGO
    col_h1, col_h2 = st.columns([1, 5])
    with col_h1:
        try:
            st.image("logosocobat.jpg", width=80)
        except:
            st.markdown("🏢")
    with col_h2:
        st.markdown("<h1 class='main-title'>A votre service by Jeb 😉</h1>", unsafe_allow_html=True)

    # RECHERCHE (FOND BLANC FORCÉ)
    c1, c2 = st.columns(2)
    with c1:
        hp2_list = sorted(df_ug['GROUPE (HP2)'].dropna().unique())
        sel_hp2 = st.selectbox("Choisir le Groupe HP2", hp2_list, index=None)
    
    if sel_hp2:
        with c2:
            ug_list = sorted(df_ug[df_ug['GROUPE (HP2)'] == sel_hp2]['N° UG'].unique())
            sel_ug = st.selectbox("Choisir l'Unité UG", ug_list, index=None)

        if sel_ug:
            u = df_ug[(df_ug['GROUPE (HP2)'] == sel_hp2) & (df_ug['N° UG'] == sel_ug)].iloc[0]
            
            # Calcul surface immeuble
            df_ug['SHA_NUM'] = pd.to_numeric(df_ug['SURFACE HABITABLE (SHA)'], errors='coerce')
            surf_total = df_ug[df_ug['GROUPE (HP2)'] == sel_hp2]['SHA_NUM'].sum()
            
            st.markdown(f"<p style='color:#4F46E5; font-weight:700; font-size:1.1rem; margin-bottom:20px;'>📍 {u['NOM GROUPE']}</p>", unsafe_allow_html=True)

            # AFFICHAGE STYLE ALAN
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                <div class="alan-card">
                    <div class="card-label">🏠 LOGEMENT PERSONNEL</div>
                    <div class="card-value">{u['SURFACE HABITABLE (SHA)']} m²</div>
                    <div class="card-sub">Type {u['Type']} • Étage {u['Etage']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div class="alan-card">
                    <div class="card-label">🏢 SURFACE IMMEUBLE</div>
                    <div class="card-value">{int(surf_total):,} m²</div>
                    <div class="card-sub">{len(df_ug[df_ug['GROUPE (HP2)'] == sel_hp2])} Logements gérés</div>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.info("Sélectionnez un groupe pour afficher les données.")
