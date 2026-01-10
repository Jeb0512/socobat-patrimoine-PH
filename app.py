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

# 4. CHARGEMENT DES DONNÉES
@st.cache_data
def load_data():
    # FICHIERS : Assure-toi que les noms sur GitHub sont EXACTEMENT ceux-là
    f1, f3, f4 = "1-EQUIPEMENTS.xlsx", "3-BATIMENTS.xlsx", "4-SURFACES.xlsx"
    
    d_ug = pd.read_excel(f4, sheet_name="SURFACES DES UG", dtype={'N° UG': str, 'GROUPE (HP2)': str})
    d_bat = pd.read_excel(f3, sheet_name="SURFACES BATIMENTS", dtype={'GROUPE (HP2)': str})
    d_coll = pd.read_excel(f1, sheet_name="COLLECTIF + TRAVAUX", dtype={'HP2': str})
    
    d_ug['N° UG'] = d_ug['N° UG'].str.strip().str.zfill(6)
    d_ug['GROUPE (HP2)'] = d_ug['GROUPE (HP2)'].str.strip()
    d_bat['GROUPE (HP2)'] = d_bat['GROUPE (HP2)'].str.strip()
    d_coll['HP2'] = d_coll['HP2'].str.strip()
    return d_ug, d_bat, d_coll

try:
    df_ug, df_bat, df_coll = load_data()

    st.markdown("<h2 style='color: #1a202c;'>🏢 Asset Manager</h2>", unsafe_allow_html=True)
    
    # RECHERCHE
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        hp2_list = sorted(df_ug['GROUPE (HP2)'].dropna().unique())
        sel_hp2 = st.selectbox("Groupe HP2", hp2_list, index=None, placeholder="Choisir...")
    
    if sel_hp2:
        with c_s2:
            ug_list = sorted(df_ug[df_ug['GROUPE (HP2)'] == sel_hp2]['N° UG'].unique())
            sel_ug = st.selectbox("Numéro d'UG", ug_list, index=None, placeholder="Choisir...")

        if sel_ug:
            # EXTRACTION SÉCURISÉE
            info_ug = df_ug[(df_ug['GROUPE (HP2)'] == sel_hp2) & (df_ug['N° UG'] == sel_ug)].iloc[0]
            surf_immeuble = df_ug[df_ug['GROUPE (HP2)'] == sel_hp2]['SURFACE HABITABLE (SHA)'].sum()
            info_coll = df_coll[df_coll['HP2'] == sel_hp2]
            
            st.markdown(f"🔍 **{info_ug['NOM GROUPE']}**")

            # AFFICHAGE CARTES
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""<div class="card"><div class="card-label">🏠 Logement</div><div class="card-value">{info_ug['SURFACE HABITABLE (SHA)']} m²</div><div class="card-sub">{info_ug['Type']} • {info_ug['Etage']}</div></div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""<div class="card"><div class="card-label">🏢 Immeuble</div><div class="card-value">{int(surf_immeuble)} m²</div><div class="card-sub">{len(df_ug[df_ug['GROUPE (HP2)'] == sel_hp2])} UG au total</div></div>""", unsafe_allow_html=True)

            # CHAUFFAGE
            is_c = not info_coll.empty
            b = '<span class="badge-coll">COLLECTIF</span>' if is_c else '<span class="badge-indiv">INDIVIDUEL</span>'
            val = info_coll['Type combustible'].iloc[0] if is_c else "Individuel"
            det = info_coll['Equipement'].iloc[0] if is_c else "Équipement privé"

            st.markdown(f"""<div class="card"><div style="display:flex; justify-content:space-between;">
                <div class="card-label">🔥 Chauffage</div>{b}</div>
                <div class="card-value" style="font-size:1.3rem; margin-top:8px;">{val}</div>
                <div class="card-sub">{det}</div></div>""", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Données manquantes : {e}")