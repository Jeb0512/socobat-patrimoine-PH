import streamlit as st
import pandas as pd

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="Socobat Asset Manager",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🏢"
)

# 2. DESIGN FINTECH (Style Revolut / Qonto)
st.markdown("""
    <style>
    /* Fond global */
    .main { background-color: #f4f7f9; }
    
    /* Style des Cartes */
    .card {
        background-color: white;
        padding: 24px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03);
        margin-bottom: 16px;
        border: 1px solid #eef2f6;
    }
    
    /* Typography */
    .card-label { 
        color: #8a94a6; 
        font-size: 0.7rem; 
        font-weight: 700; 
        text-transform: uppercase; 
        letter-spacing: 1px;
        margin-bottom: 8px;
    }
    .card-value { 
        color: #1a202c; 
        font-size: 1.8rem; 
        font-weight: 800; 
        letter-spacing: -0.5px;
    }
    .card-sub { 
        color: #5a67d8; 
        font-size: 0.85rem; 
        font-weight: 600;
        margin-top: 4px;
    }
    
    /* Badges Style Revolut */
    .badge-coll { 
        background-color: #e6fffa; 
        color: #319795; 
        padding: 6px 14px; 
        border-radius: 12px; 
        font-size: 0.7rem; 
        font-weight: 800; 
    }
    .badge-indiv { 
        background-color: #fff5f5; 
        color: #e53e3e; 
        padding: 6px 14px; 
        border-radius: 12px; 
        font-size: 0.7rem; 
        font-weight: 800; 
    }
    
    /* Inputs */
    div[data-baseweb="select"] {
        border-radius: 15px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. MOT DE PASSE SÉCURISÉ
if "authenticated" not in st.session_state:
    st.markdown("<div style='text-align:center; padding:100px 20px;'>", unsafe_allow_html=True)
    st.image("https://img.icons8.com/fluency/96/shield-lock.png")
    st.title("Socobat Private Access")
    pwd = st.text_input("Enter Access Code", type="password")
    if st.button("Unlock Dashboard", use_container_width=True):
        if pwd == "SOCOBAT2026":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid Code")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 4. CHARGEMENT DES DONNÉES
@st.cache_data
def load_data():
    f1 = "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx"
    f3 = "3 - BATIMENTS_SURFACES_NOVEMBRE 2024.xlsx"
    f4 = "4 - UG SURFACES - NOVEMBRE 2024.xlsx"
    
    # Lecture
    d_ug = pd.read_excel(f4, sheet_name="SURFACES DES UG", dtype={'N° UG': str, 'GROUPE (HP2)': str})
    d_bat = pd.read_excel(f3, sheet_name="SURFACES BATIMENTS", dtype={'GROUPE (HP2)': str})
    d_coll = pd.read_excel(f1, sheet_name="COLLECTIF + TRAVAUX", dtype={'HP2': str})
    
    # Nettoyage
    d_ug['N° UG'] = d_ug['N° UG'].str.strip().str.zfill(6)
    d_ug['GROUPE (HP2)'] = d_ug['GROUPE (HP2)'].str.strip()
    d_coll['HP2'] = d_coll['HP2'].str.strip()
    return d_ug, d_bat, d_coll

try:
    df_ug, df_bat, df_coll = load_data()

    # HEADER
    st.markdown("<h2 style='color: #1a202c; font-weight:800;'>Socobat Asset</h2>", unsafe_allow_html=True)
    
    # RECHERCHE ULTRA-FLUIDE
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        hp2_list = sorted(df_ug['GROUPE (HP2)'].dropna().unique())
        sel_hp2 = st.selectbox("Code Groupe", hp2_list, index=None, placeholder="Search HP2...")
    
    if sel_hp2:
        with c_s2:
            ug_list = sorted(df_ug[df_ug['GROUPE (HP2)'] == sel_hp2]['N° UG'].unique())
            sel_ug = st.selectbox("Unité UG", ug_list, index=None, placeholder="Search UG...")

        if sel_ug:
            # DATA EXTRACTION
            info_ug = df_ug[(df_ug['GROUPE (HP2)'] == sel_hp2) & (df_ug['N° UG'] == sel_ug)].iloc[0]
            surf_tot = df_ug[df_ug['GROUPE (HP2)'] == sel_hp2]['SURFACE HABITABLE (SHA)'].sum()
            info_coll = df_coll[df_coll['HP2'] == sel_hp2]
            
            st.markdown(f"### {info_ug['NOM GROUPE']}")

            # CARTES STYLE FINTECH
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="card">
                    <div class="card-label">Surface Logement</div>
                    <div class="card-value">{info_ug['SURFACE HABITABLE (SHA)']} m²</div>
                    <div class="card-sub">Type {info_ug['Type']} • {info_ug['Etage']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="card">
                    <div class="card-label">Total Immeuble</div>
                    <div class="card-value">{int(surf_tot):,} m²</div>
                    <div class="card-sub">{len(df_ug[df_ug['GROUPE (HP2)'] == sel_hp2])} Unités Habitables</div>
                </div>
                """, unsafe_allow_html=True)

            # CHAUFFAGE SECTION
            is_c = not info_coll.empty
            badge = '<span class="badge-coll">COLLECTIF</span>' if is_c else '<span class="badge-indiv">INDIVIDUEL</span>'
            type_ch = info_coll['Type combustible'].iloc[0] if is
