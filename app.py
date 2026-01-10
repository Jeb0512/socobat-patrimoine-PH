import streamlit as st
import pandas as pd

# 1. CONFIGURATION
st.set_page_config(
    page_title="Socobat Asset - Jeb",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. STYLE FINTECH PREMIUM
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #F8F9FB; }
    
    /* Header */
    .header-container {
        display: flex;
        align-items: center;
        margin-bottom: 25px;
        gap: 12px;
    }
    .logo-text { font-size: 1.8rem; font-weight: 800; color: #111827; letter-spacing: -1.2px; }
    .jeb-text { color: #6B7280; font-size: 0.9rem; font-weight: 500; margin-top: -5px; }
    
    /* Widget Cards */
    .widget-card {
        background-color: white;
        padding: 24px;
        border-radius: 24px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02), 0 20px 25px -5px rgba(0,0,0,0.05);
        margin-bottom: 16px;
    }
    
    /* Typography */
    .t-label { color: #6B7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
    .t-value { color: #111827; font-size: 2rem; font-weight: 800; margin: 4px 0; letter-spacing: -1px; }
    .t-sub { color: #4F46E5; font-size: 0.85rem; font-weight: 600; }
    
    /* Badges */
    .mollie-tag {
        background-color: #111827;
        color: white;
        padding: 5px 12px;
        border-radius: 100px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .energy-tag { background-color: #DEF7EC; color: #03543F; border: 1px solid #BCF0DA; }

    /* Inputs Mobile */
    div[data-baseweb="select"] { 
        border-radius: 14px !important; 
        border: 1px solid #D1D5DB !important;
        background: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ACCÈS SÉCURISÉ
if "authorized" not in st.session_state:
    st.markdown("<div style='padding:80px 20px; text-align:center'>", unsafe_allow_html=True)
    st.markdown("<div class='logo-text'>🏢 Socobat.</div>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B7280'>Asset Management Portal</p>", unsafe_allow_html=True)
    
    with st.container():
        _, mid, _ = st.columns([1,3,1])
        with mid:
            code = st.text_input("Code confidentiel", type="password")
            if st.button("Déverrouiller l'accès", use_container_width=True):
                if code == "SOCOBAT2026":
                    st.session_state["authorized"] = True
                    st.rerun()
                else: st.error("Accès refusé")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 4. LOAD DATA
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

    # TITRE PERSONNALISÉ JEB
    st.markdown("""
        <div class="header-container">
            <span style="font-size:2.2rem;">🏢</span>
            <div>
                <div class="logo-text">A votre service</div>
                <div class="jeb-text">by Jeb 😉</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # RECHERCHE
    c1, c2 = st.columns(2)
    with c1:
        hp2_options = sorted(df_ug['GROUPE (HP2)'].dropna().unique())
        sel_hp2 = st.selectbox("Groupe HP2", hp2_options, index=None, placeholder="Rechercher...")
    
    if sel_hp2:
        with c2:
            ug_options = sorted(df_ug[df_ug['GROUPE (HP2)'] == sel_hp2]['N° UG'].unique())
            sel_ug = st.selectbox("Numéro UG", ug_options, index=None, placeholder="Saisir N° UG...")

        if sel_ug:
            u = df_ug[(df_ug['GROUPE (HP2)'] == sel_hp2) & (df_ug['N° UG'] == sel_ug)].iloc[0]
            s_i = df_ug[df_ug['GROUPE (HP2)'] == sel_hp2]['SURFACE HABITABLE (SHA)'].sum()
            c = df_coll[df_coll['HP2'] == sel_hp2]
            
            st.markdown(f"<p style='color:#6B7280; font-weight:600; margin-bottom:15px'>📍 {u['NOM GROUPE']}</p>", unsafe_allow_html=True)

            # GRILLE WIDGETS
            w1, w2 = st.columns(2)
            with w1:
                st.markdown(f"""
                <div class="widget-card">
                    <div class="t-label">Surface Logement</div>
                    <div class="t-value">{u['SURFACE HABITABLE (SHA)']} m²</div>
                    <div class="t-sub">Type {u['Type']} • {u['Etage']}</div>
                </div>
                """, unsafe_allow_html=True)
            with w2:
                st.markdown(f"""
                <div class="widget-card">
                    <div class="t-label">Surface Immeuble</div>
                    <div class="t-value">{int(s_i):,} m²</div>
                    <div class="t-sub">{len(df_ug[df_ug['GROUPE (HP2)'] == sel_hp2])} Logements gérés</div>
                </div>
                """, unsafe_allow_html=True)

            # CHAUFFAGE
            is_c = not c.empty
            tag = "Collectif" if is_c else "Individuel"
            t_cls = "energy-tag" if is_c else ""
            fuel = c['Type combustible'].iloc[0] if is_c else "Gaz / Électricité"
            eq = c['Equipement'].iloc[0] if is_c else "Équipement privé"

            st.markdown(f"""
            <div class="widget-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div class="t-label">Énergie & Chauffage</div>
                    <span class="mollie-tag {t_cls}">{tag}</span>
                </div>
                <div class="t-value" style="font-size:1.6rem;">{fuel}</div>
                <div style="color:#6B7280; font-size:0.85rem;">{eq}</div>
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.info("Sélectionnez un groupe pour activer l'Asset Manager.")
