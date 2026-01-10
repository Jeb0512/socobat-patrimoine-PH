import streamlit as st
import pandas as pd

# 1. CONFIGURATION
st.set_page_config(
    page_title="Socobat Asset - Jeb",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. CHARTE GRAPHIQUE EXTRAITE DE L'IMAGE (CSS CUSTOM)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #F8F9FB; }
    
    /* Header Branding */
    .header-box {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 30px;
        padding-top: 10px;
    }
    .logo-socobat {
        background: white;
        padding: 10px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .title-text { font-size: 1.8rem; font-weight: 800; color: #111827; letter-spacing: -1px; }
    .subtitle-text { color: #6B7280; font-size: 0.9rem; font-weight: 500; }

    /* Cards Style (Identique à l'image) */
    .st-card {
        background-color: white;
        padding: 28px;
        border-radius: 24px;
        border: 1px solid #F2F4F7;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.04), 0 8px 10px -6px rgba(0,0,0,0.04);
        margin-bottom: 16px;
    }

    /* Typography & Tags */
    .t-label { color: #6B7280; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
    .t-value { color: #111827; font-size: 2.2rem; font-weight: 800; letter-spacing: -1.5px; }
    .t-sub { color: #3B82F6; font-size: 0.85rem; font-weight: 600; margin-top: 8px; }
    
    /* Mollie/Fintech Tags */
    .tag {
        float: right;
        background-color: #111827;
        color: white;
        padding: 4px 12px;
        border-radius: 100px;
        font-size: 0.65rem;
        font-weight: 700;
    }
    .tag-green { background-color: #D1FAE5; color: #065F46; }
    .tag-blue { background-color: #DBEAFE; color: #1E40AF; }

    /* Search Input Style */
    div[data-baseweb="select"] { 
        border-radius: 16px !important; 
        border: 1px solid #D1D5DB !important;
        background: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. AUTHENTIFICATION SÉCURISÉE
if "authorized" not in st.session_state:
    st.markdown("<div style='padding:80px 20px; text-align:center'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:3rem; margin-bottom:10px;'>🏢</div>", unsafe_allow_html=True)
    st.markdown("<div class='title-text'>Socobat Portal.</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B7280'>Sécurisé par Jeb</p>", unsafe_allow_html=True)
    
    with st.container():
        _, mid, _ = st.columns([1,3,1])
        with mid:
            code = st.text_input("Code confidentiel", type="password")
            if st.button("Déverrouiller", use_container_width=True):
                if code == "SOCOBAT2026":
                    st.session_state["authorized"] = True
                    st.rerun()
                else: st.error("Accès refusé")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 4. CHARGEMENT DES DONNÉES
@st.cache_data
def load_all_assets():
    f1 = "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx"
    f3 = "3 - BATIMENTS_SURFACES_NOVEMBRE 2024.xlsx"
    f4 = "4 - UG SURFACES - NOVEMBRE 2024.xlsx"
    d_ug = pd.read_excel(f4, sheet_name="SURFACES DES UG", dtype={'N° UG': str, 'GROUPE (HP2)': str})
    d_bat = pd.read_excel(f3, sheet_name="SURFACES BATIMENTS", dtype={'GROUPE (HP2)': str})
    d_coll = pd.read_excel(f1, sheet_name="COLLECTIF + TRAVAUX", dtype={'HP2': str})
    d_ug['N° UG'] = d_ug['N° UG'].str.strip().str.zfill(6)
    d_ug['GROUPE (HP2)'] = d_ug['GROUPE (HP2)'].str.strip()
    d_coll['HP2'] = d_coll['HP2'].str.strip()
    return d_ug, d_bat, d_coll

try:
    df_ug, df_bat, df_coll = load_all_assets()

    # HEADER CHARTE JEB
    st.markdown("""
        <div class="header-box">
            <div class="logo-socobat"><span style="font-size:1.8rem;">🏢</span></div>
            <div>
                <div class="title-text">A votre service</div>
                <div class="subtitle-text">by Jeb 😉</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # BARRE DE RECHERCHE (MOBILE READY)
    c1, c2 = st.columns(2)
    with c1:
        hp2_options = sorted(df_ug['GROUPE (HP
