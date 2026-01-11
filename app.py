import streamlit as st
import pandas as pd

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="Socobat Asset - Jeb",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. DESIGN SYSTEM "ALAN STYLE" (Fix complet fond blanc et texte noir)
st.markdown("""
    <style>
    /* Force le fond blanc sur toute l'application */
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #F9FAFB !important;
    }

    /* FIX CHAMPS BLANCS / TEXTE NOIR */
    div[data-baseweb="select"], div[data-baseweb="base-input"], input {
        background-color: white !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 12px !important;
    }
    
    /* Force la visibilité du texte dans les listes Safari/iPhone */
    div[role="listbox"] div, span[data-baseweb="select"] {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
    }

    /* STYLE DES CARTES ALAN */
    .alan-card {
        background-color: white !important;
        padding: 24px !important;
        border-radius: 20px !important;
        border: 1px solid #E5E7EB !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 16px !important;
        color: #111827 !important;
    }

    .t-label { color: #6B7280 !important; font-size: 0.75rem !important; font-weight: 700 !important; text-transform: uppercase; margin-bottom: 8px; }
    .t-val { color: #111827 !important; font-size: 2.2rem !important; font-weight: 800 !important; letter-spacing: -1.5px; line-height: 1; }
    .t-sub { color: #6366F1 !important; font-size: 0.85rem !important; font-weight: 600 !important; margin-top: 8px; }

    /* TITRES ET LABELS */
    h1, h2, h3, p, label { color: #111827 !important; font-weight: 600 !important; }

    /* BOUTON */
    .stButton>button {
        background-color: #6366f1 !important;
        color: white !important;
        border-radius: 100px !important;
        font-weight: 700 !important;
        border: none !important;
        width: 100%;
        height: 45px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ACCÈS SÉCURISÉ
if "auth" not in st.session_state:
    st.markdown("<div style='text-align:center; padding-top:80px;'>", unsafe_allow_html=True)
    st.markdown("<h1>🏢 Socobat Asset</h1><p style='color:#6B7280;'>By Jeb 😉</p>", unsafe_allow_html=True)
    
    _, mid, _ = st.columns([1,2,1])
    with mid:
        code = st.text_input("Code secret", type="password")
        if st.button("Se connecter"):
            if code == "SOCOBAT2026":
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Code incorrect")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 4. CHARGEMENT DES DONNÉES
@st.cache_data
def load_data():
    f_surfaces = "4 - UG SURFACES - NOVEMBRE 2024.xlsx"
    du = pd.read_excel(f_surfaces, sheet_name="SURFACES DES UG", dtype=str)
    return du

try:
    df = load_data()
    st.markdown("<h2>🏢 A votre service by Jeb 😉</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        hp2_list = sorted(df['GROUPE (HP2)'].dropna().unique())
        sel_h = st.selectbox("Groupe HP2", hp2_list, index=None, placeholder="Choisir...")
    
    if sel_h:
        with col2:
            ug_list = sorted(df[df['GROUPE (HP2)'] == sel_h]['N° UG'].unique())
            sel_u = st.selectbox("Unité UG", ug_list, index=None, placeholder="Choisir...")

        if sel_u:
            u_data = df[(df['GROUPE (HP2)'] == sel_h) & (df['N° UG'] == sel_u)].iloc[0]
            df['SHA_NUM'] = pd.to_numeric(df['SURFACE HABITABLE (SHA)'], errors='coerce')
            total_immeuble = df[df['GROUPE (HP2)'] == sel_h]['SHA_NUM'].sum()
            
            st.markdown(f"<p style='color:#6366F1; font-weight:700; margin-left:5px;'>📍 {u_data['NOM GROUPE']}</p>", unsafe_allow_html=True)

            c_a, c_b = st.columns(2)
            with c_a:
                st.markdown(f"""
                <div class="alan-card">
                    <div class="t-label">🏠 LOGEMENT PERSONNEL</div>
                    <div class="t-val">{u_data['SURFACE HABITABLE (SHA)']} m²</div>
                    <div class="t-sub">Type {u_data['Type']} • Etage {u_data['Etage']}</div>
                </div>
                """, unsafe_allow_html=True)
            with c_b:
                st.markdown(f"""
                <div class="alan-card">
                    <div class="t-label">🏢 SURFACE IMMEUBLE</div>
                    <div class="t-val">{int(total_immeuble):,} m²</div>
                    <div class="t-sub">{len(df[df['GROUPE (HP2)'] == sel_h])} Logements</div>
                </div>
                """, unsafe_allow_html=True)

except Exception as e:
    st.info("Utilisez les menus pour afficher les données.")
