import streamlit as st
import pandas as pd

# 1. CONFIGURATION
st.set_page_config(
    page_title="Socobat Asset Manager",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. DESIGN SYSTEM (Inspiré de Make.com)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global Reset */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F4F7F9 !important; color: #1A1C21; }
    .stApp { background-color: #F4F7F9 !important; }
    
    /* Header Branding */
    .brand-box { display: flex; align-items: center; gap: 12px; margin-bottom: 30px; }
    .logo-square { background: white; padding: 10px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #E1E8ED; }
    .title-main { font-size: 1.6rem; font-weight: 800; color: #1A1C21; letter-spacing: -0.5px; }
    .title-sub { color: #697689; font-size: 0.85rem; font-weight: 500; }

    /* Widgets / Cards (Style Make.com) */
    .m-card {
        background-color: white !important;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #E1E8ED;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02), 0 4px 6px rgba(0,0,0,0.02);
        margin-bottom: 16px;
    }
    .m-icon { font-size: 1.4rem; margin-bottom: 12px; display: block; }
    .m-label { color: #697689; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; }
    .m-value { color: #1A1C21; font-size: 2rem; font-weight: 800; line-height: 1; letter-spacing: -0.8px; }
    .m-footer { color: #4F46E5; font-size: 0.8rem; font-weight: 600; margin-top: 10px; }
    
    /* Status Tags */
    .m-tag { float: right; padding: 4px 12px; border-radius: 20px; font-size: 0.65rem; font-weight: 700; }
    .tag-active { background-color: #ECFDF5; color: #065F46; border: 1px solid #D1FAE5; }
    .tag-standard { background-color: #F3F4F6; color: #374151; border: 1px solid #E5E7EB; }

    /* FIX INPUTS : PLUS DE NOIR DANS LES CHAMPS */
    input[type="text"], input[type="password"], div[data-baseweb="select"], div[data-baseweb="base-input"] {
        background-color: white !important;
        color: #1A1C21 !important;
        border-radius: 10px !important;
        border: 1px solid #D1D5DB !important;
    }
    div[data-baseweb="select"] > div { background-color: white !important; color: #1A1C21 !important; }
    label, p, span { color: #1A1C21 !important; }

    /* Bouton Pro */
    .stButton>button {
        background-color: #111827; color: white; border-radius: 10px;
        padding: 12px 24px; font-weight: 600; width: 100%; border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. PAGE DE CONNEXION (Style Make)
if "authenticated" not in st.session_state:
    st.markdown("<div style='max-width:450px; margin: 0 auto; padding-top:100px; text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:3rem; margin-bottom:20px;'>🏢</div>", unsafe_allow_html=True)
    st.markdown("<h1 class='title-main'>Accès réservé</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#697689; margin-bottom:30px;'>Outil Asset Manager Socobat.<br><i>Veuillez vous identifier pour continuer.</i></p>", unsafe_allow_html=True)
    
    pw = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if pw == "SOCOBAT2026":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect")
    
    st.markdown("<p style='color:#A0AEC0; font-size:0.8rem; margin-top:40px;'>by Jeb 😉</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 4. CHARGEMENT DES DONNÉES
@st.cache_data
def load_data():
    f1 = "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx"
    f3 = "3 - BATIMENTS_SURFACES_NOVEMBRE 2024.xlsx"
    f4 = "4 - UG SURFACES - NOVEMBRE 2024.xlsx"
    
    d_ug = pd.read_excel(f4, sheet_name="SURFACES DES UG", dtype={'N° UG': str, 'GROUPE (HP2)': str})
    d_bt = pd.read_excel(f3, sheet_name="SURFACES BATIMENTS", dtype={'GROUPE (HP2)': str})
    d_cl = pd.read_excel(f1, sheet_name="COLLECTIF + TRAVAUX", dtype={'HP2': str})
    
    d_ug['N° UG'] = d_ug['N° UG'].str.strip().str.zfill(6)
    for d in [d_ug, d_bt, d_cl]:
        c = 'GROUPE (HP2)' if 'GROUPE (HP2)' in d.columns else 'HP2'
        d[c] = d[c].str.strip()
    return d_ug, d_bt, d_cl

try:
    du, db, dc = load_data()

    # HEADER DASHBOARD
    st.markdown("""
        <div class="brand-box">
            <div class="logo-square">🏢</div>
            <div>
                <div class="title-main">A votre service</div>
                <div class="title-sub">Asset Manager Socobat by Jeb 😉</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # RECHERCHE (BLANC FORCÉ)
    c1, c2 = st.columns(2)
    with c1:
        hp2_opts = sorted(du['GROUPE (HP2)'].dropna().unique())
        sel_h = st.selectbox("Groupe HP2", hp2_opts, index=None, placeholder="Filtrer par HP2...")
    
    if sel_h:
        with c2:
            ug_opts = sorted(du[du['GROUPE (HP2)'] == sel_h]['N° UG'].unique())
            sel_u = st.selectbox("Numéro UG", ug_opts, index=None, placeholder="Filtrer par UG...")

        if sel_u:
            # EXTRACTION INFOS
            u_data = du[(du['GROUPE (HP2)'] == sel_h) & (du['N° UG'] == sel_u)].iloc[0]
            
            # FIX SURFACE IMMEUBLE (Total du HP2)
            surf_immeuble = du[du['GROUPE (HP2)'] == sel_h]['SURFACE HABITABLE (SHA)'].sum()
            nb_logs = len(du[du['GROUPE (HP2)'] == sel_h])
            
            c_data = dc[dc['HP2'] == sel_h]
            
            st.markdown(f"<p style='color:#697689; font-weight:600; margin-bottom:20px; border-left: 3px solid #111827; padding-left:12px;'>📍 {u_data['NOM GROUPE']}</p>", unsafe_allow_html=True)

            # GRILLE WIDGETS
            w1, w2 = st.columns(2)
            
            with w1:
                st.markdown(f"""
                <div class="m-card">
                    <span class="m-icon">🏠</span>
                    <div class="m-label">Surface Logement</div>
                    <div class="m-value">{u_data['SURFACE HABITABLE (SHA)']} m²</div>
                    <div class="m-footer">Type {u_data['Type']} • Étage {u_data['Etage']}</div>
                </div>
                """, unsafe_allow_html=True)

            with w2:
                st.markdown(f"""
                <div class="m-card">
                    <span class="m-icon">🏢</span>
                    <div class="m-label">Surface Immeuble</div>
                    <div class="m-value">{int(surf_immeuble):,} m²</div>
                    <div class="m-footer">{nb_logs} Logements gérés</div>
                </div>
                """, unsafe_allow_html=True)

            # CHAUFFAGE (WIDGET LARGE)
            is_c = not c_data.empty
            lbl = "COLLECTIF" if is_c else "INDIVIDUEL"
            sty = "tag-active" if is_c else "tag-standard"
            fuel = c_data['Type combustible'].iloc[0] if is_c else "Gaz / Électricité"
            equip = c_data['Equipement'].iloc[0] if is_c else "Chaudière individuelle"

            st.markdown(f"""
            <div class="m-card">
                <span class="m-tag {sty}">{lbl}</span>
                <span class="m-icon">⚡</span>
                <div class="m-label">Énergie & Chauffage</div>
                <div class="m-value" style="font-size:1.6rem;">{fuel}</div>
                <div style="color:#697689; font-size:0.85rem; margin-top:8px;">{equip}</div>
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.info("Veuillez sélectionner un groupe pour charger l'Asset Manager.")
