import streamlit as st
import pandas as pd

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="Socobat Asset Manager",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🏢"
)

# 2. DESIGN CSS (STYLE PRO / MOBILE)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 16px;
        border: 1px solid #edf2f7;
    }
    .card-label { color: #718096; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; margin-bottom: 8px; }
    .card-value { color: #1a202c; font-size: 1.6rem; font-weight: 800; }
    .card-sub { color: #a0aec0; font-size: 0.85rem; margin-top: 4px; }
    .badge-coll { background-color: #c6f6d5; color: #22543d; padding: 4px 12px; border-radius: 99px; font-size: 0.75rem; font-weight: 700; }
    .badge-indiv { background-color: #fed7d7; color: #822727; padding: 4px 12px; border-radius: 99px; font-size: 0.75rem; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# 3. PROTECTION PAR MOT DE PASSE
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔒 Accès Socobat")
        pwd = st.text_input("Code d'accès", type="password")
        if st.button("Connexion"):
            if pwd == "SOCOBAT2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Code incorrect")
        return False
    return True

if not check_password():
    st.stop()

# 4. CHARGEMENT DES DONNÉES AVEC TES NOMS DE FICHIERS
@st.cache_data
def load_data():
    # Noms exacts de tes fichiers sur GitHub
    file_collectif = "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx"
    file_batiments = "3 - BATIMENTS_SURFACES_NOVEMBRE 2024.xlsx"
    file_ug = "4 - UG SURFACES - NOVEMBRE 2024.xlsx"
    
    try:
        # Lecture des fichiers Excel
        d_ug = pd.read_excel(file_ug, sheet_name="SURFACES DES UG", dtype={'N° UG': str, 'GROUPE (HP2)': str})
        d_bat = pd.read_excel(file_batiments, sheet_name="SURFACES BATIMENTS", dtype={'GROUPE (HP2)': str})
        d_coll = pd.read_excel(file_collectif, sheet_name="COLLECTIF + TRAVAUX", dtype={'HP2': str})
        
        # Nettoyage des données
        d_ug['N° UG'] = d_ug['N° UG'].str.strip().str.zfill(6)
        d_ug['GROUPE (HP2)'] = d_ug['GROUPE (HP2)'].str.strip()
        d_bat['GROUPE (HP2)'] = d_bat['GROUPE (HP2)'].str.strip()
        d_coll['HP2'] = d_coll['HP2'].str.strip()
        
        return d_ug, d_bat, d_coll
    except Exception as e:
        st.error(f"Erreur lors de la lecture des fichiers : {e}")
        st.stop()

try:
    df_ug, df_bat, df_coll = load_data()

    st.markdown("<h2 style='color: #1a202c;'>🏢 Asset Manager</h2>", unsafe_allow_html=True)
    
    # RECHERCHE
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        hp2_list = sorted(df_ug['GROUPE (HP2)'].dropna().unique())
        sel_hp2 = st.selectbox("Groupe HP2", hp2_list, index=None, placeholder="Saisir HP2...")
    
    if sel_hp2:
        with c_s2:
            ug_list = sorted(df_ug[df_ug['GROUPE (HP2)'] == sel_hp2]['N° UG'].unique())
            sel_ug = st.selectbox("Numéro d'UG", ug_list, index=None, placeholder="Saisir UG...")

        if sel_ug:
            # EXTRACTION
            info_ug = df_ug[(df_ug['GROUPE (HP2)'] == sel_hp2) & (df_ug['N° UG'] == sel_ug)].iloc[0]
            surf_immeuble = df_ug[df_ug['GROUPE (HP2)'] == sel_hp2]['SURFACE HABITABLE (SHA)'].sum()
            info_coll = df_coll[df_coll['HP2'] == sel_hp2]
            
            st.markdown(f"🔍 **{info_ug['NOM GROUPE']}**")

            # AFFICHAGE CARTES
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                    <div class="card">
                        <div class="card-label">🏠 Logement</div>
                        <div class="card-value">{info_ug['SURFACE HABITABLE (SHA)']} m²</div>