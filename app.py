import streamlit as st
import pandas as pd

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="Socobat Asset Manager",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🏢"
)

# 2. DESIGN CSS (STYLE REVOLUT / PRO DASHBOARD)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    
    /* Style des Cartes */
    .card {
        background-color: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 16px;
        border: 1px solid #edf2f7;
    }
    .card-label { color: #718096; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
    .card-value { color: #1a202c; font-size: 1.8rem; font-weight: 800; }
    .card-sub { color: #a0aec0; font-size: 0.85rem; margin-top: 4px; }
    
    /* Badges Chauffage */
    .badge-coll { background-color: #c6f6d5; color: #22543d; padding: 4px 12px; border-radius: 99px; font-size: 0.75rem; font-weight: 700; }
    .badge-indiv { background-color: #fed7d7; color: #822727; padding: 4px 12px; border-radius: 99px; font-size: 0.75rem; font-weight: 700; }
    
    /* Inputs */
    .stSelectbox div[data-baseweb="select"] { border-radius: 12px; border: 1px solid #e2e8f0; }
    </style>
    """, unsafe_allow_html=True)

# 3. PROTECTION PAR MOT DE PASSE
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<div style='text-align:center; padding:50px;'>", unsafe_allow_html=True)
        st.title("🔒 Accès Privé Socobat")
        pwd = st.text_input("Veuillez entrer le code d'accès", type="password")
        if st.button("Se connecter"):
            if pwd == "SOCOBAT2026":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Code incorrect")
        st.markdown("</div>", unsafe_allow_html=True)
        return False
    return True

if not check_password():
    st.stop()

# 4. CHARGEMENT DES DONNÉES (AVEC NOMS SIMPLIFIÉS)
@st.cache_data
def load_data():
    # MODIFIE CES NOMS SI TU NE VEUX PAS RENOMMER TES FICHIERS SUR GITHUB
    file_ug = "4-SURFACES.xlsx"
    file_bat = "3-BATIMENTS.xlsx"
    file_coll = "1-EQUIPEMENTS.xlsx"
    
    df_ug = pd.read_excel(file_ug, sheet_name="SURFACES DES UG", dtype={'N° UG': str, 'GROUPE (HP2)': str})
    df_bat = pd.read_excel(file_bat, sheet_name="SURFACES BATIMENTS", dtype={'GROUPE (HP2)': str})
    df_coll = pd.read_excel(file_coll, sheet_name="COLLECTIF + TRAVAUX", dtype={'HP2': str})
    
    # Nettoyage des données
    df_ug['N° UG'] = df_ug['N° UG'].str.strip().str.zfill(6)
    df_ug['GROUPE (HP2)'] = df_ug['GROUPE (HP2)'].str.strip()
    df_bat['GROUPE (HP2)'] = df_bat['GROUPE (HP2)'].str.strip()
    df_coll['HP2'] = df_coll['HP2'].str.strip()
    
    return df_ug, df_bat, df_coll

try:
    df_ug, df_bat, df_coll = load_data()

    # --- EN-TÊTE ---
    st.markdown("<h1 style='color: #1a202c; font-size: 1.5rem; margin-bottom: 1rem;'>🏢 Socobat Asset Manager</h1>", unsafe_allow_html=True)
    
    # --- BARRE DE RECHERCHE ---
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        hp2_list = sorted(df_ug['GROUPE (HP2)'].dropna().unique())
        selected_hp2 = st.selectbox("Code HP2 (Groupe)", hp2_list, index=None, placeholder="Saisir HP2...")
    
    if selected_hp2:
        with col_s2:
            ug_list = sorted(df_ug[df_ug['GROUPE (HP2)'] == selected_hp2]['N° UG'].unique())
            selected_ug = st.selectbox("Numéro d'UG", ug_list, index=None, placeholder="Saisir UG...")

        if selected_ug:
            # Extraction des données
            info_ug =