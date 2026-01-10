import streamlit as st
import pandas as pd

# 1. CONFIGURATION
st.set_page_config(page_title="Socobat Asset - Jeb", layout="wide", initial_sidebar_state="collapsed")

# 2. CHARTE GRAPHIQUE "SIGNATURE" (EXTRAITE DE TON IMAGE)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    /* Fond global clair */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F8F9FB; }
    .stApp { background-color: #F8F9FB; }
    
    /* Header Branding */
    .header-box { display: flex; align-items: center; gap: 15px; margin-bottom: 25px; padding-top: 10px; }
    .logo-container { background: white; padding: 12px; border-radius: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    .title-txt { font-size: 1.8rem; font-weight: 800; color: #111827; letter-spacing: -1.2px; line-height: 1.1; }
    .sub-txt { color: #6B7280; font-size: 0.9rem; font-weight: 500; }

    /* Cards Style (Identique à ton image) */
    .st-card {
        background-color: white; padding: 25px; border-radius: 24px;
        border: 1px solid #F2F4F7; margin-bottom: 15px;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.04);
        position: relative;
    }

    /* Boîte avec Icônes */
    .card-icon { font-size: 1.5rem; margin-bottom: 10px; display: block; }
    .t-lbl { color: #6B7280; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; }
    .t-val { color: #111827; font-size: 2.2rem; font-weight: 800; letter-spacing: -1.5px; line-height: 1; }
    .t-sub { color: #3B82F6; font-size: 0.85rem; font-weight: 600; margin-top: 8px; }
    
    /* Tags arrondis */
    .tag { float: right; background-color: #111827; color: white; padding: 5px 12px; border-radius: 100px; font-size: 0.65rem; font-weight: 700; }
    .tag-gr { background-color: #D1FAE5; color: #065F46; }

    /* CORRECTION : PLUS DE NOIR DANS LES CHAMPS */
    div[data-baseweb="select"], div[data-baseweb="input"] { 
        border-radius: 16px !important; 
        border: 1px solid #D1D5DB !important; 
        background-color: white !important; 
        color: #111827 !important;
    }
    div[data-baseweb="select"] * { color: #111827 !important; background-color: white !important; }
    
    /* Bouton Connexion */
    .stButton>button {
        border-radius: 14px; background-color: #111827; color: white; font-weight: 600; padding: 10px 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ACCÈS SÉCURISÉ (PAGE CLAIRE)
if "auth" not in st.session_state:
    st.markdown("<div style='text-align:center;padding-top:80px'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:3.5rem; margin-bottom:15px;'>🏢</div>", unsafe_allow_html=True)
    st.markdown("<div class='title-txt'>Socobat Asset</div><p class='sub-txt'>By Jeb Edition 😉</p>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1,3,1])
    with mid:
        pw = st.text_input("Code secret", type="password")
        if st.button("Accéder au Dashboard", use_container_width=True):
            if pw == "SOCOBAT2026":
                st.session_state["auth"] = True
                st.rerun()
            else: st.error("Code erroné")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# 4. CHARGEMENT DATA
@st.cache_data
def load_data():
    f1, f3, f4 = "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx", "3 - BATIMENTS_SURFACES_NOVEMBRE 2024.xlsx", "4 - UG SURFACES - NOVEMBRE 2024.xlsx"
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

    # LOGO SOCOBAT & TITRE JEB
    st.markdown("""
        <div class="header-box">
            <div class="logo-container">🏢</div>
            <div>
                <div class="title-txt">A votre service</div>
                <div class="sub-txt">by Jeb 😉</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # RECHERCHE SANS FOND NOIR
    c1, c2 = st.columns(2)
    with c1:
        h_opts = sorted(du['GROUPE (HP2)'].dropna().unique())
        sel_h = st.selectbox("Code HP2", h_opts, index=None, placeholder="Chercher...")
    
    if sel_h:
        with c2:
            u_opts = sorted(du[du['GROUPE (HP2)'] == sel_h]['N° UG'].unique())
            sel_u = st.selectbox("Numéro d'UG", u_opts, index=None, placeholder="N° UG...")

        if sel_u:
            u = du[(du['GROUPE (HP2)'] == sel_h) & (du['N° UG'] == sel_u)].iloc[0]
            s_i = du[du['GROUPE (HP2)'] == sel_h]['SURFACE HABITABLE (SHA)'].sum()
            c = dc[dc['HP2'] == sel_h]
            
            st.markdown(f"<p style='color:#6B7280; font-weight:600; margin-left:5px;'>📍 {u['NOM GROUPE']}</p>", unsafe_allow_html=True)

            # GRILLE AVEC ICONES
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""
                <div class="st-card">
                    <span class="card-icon">🏠</span>
                    <div class="t-lbl">Logement Personnel</div>
                    <div class="t-val">{u['SURFACE HABITABLE (SHA)']} m²</div>
                    <div class="t-sub">Type {u['Type']} • Étage {u['Etage']}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div class="st-card">
                    <span class="card-icon">🏢</span>
                    <div class="t-lbl">Surface Immeuble</div>
                    <div class="t-value">{int(s_i):,} m²</div>
                    <div class="t-sub">{len(du[du['GROUPE (HP2)'] == sel_h])} Logements gérés</div>
                </div>
                """, unsafe_allow_html=True)

            # CHAUFFAGE AVEC TAGS MOLLIE
            is_c = not c.empty
            tag_lbl = "COLLECTIF" if is_c else "INDIVIDUEL"
            tag_style = "tag-gr" if is_c else ""
            fuel = c['Type combustible'].iloc[0] if is_c else "Gaz / Électricité"
            eq = c['Equipement'].iloc[0] if is_c else "Chaudière privée"

            st.markdown(f"""
            <div class="st-card">
                <span class="tag {tag_style}">{tag_lbl}</span>
                <span class="card-icon">⚡</span>
                <div class="t-lbl">Énergie & Chauffage</div>
                <div class="t-val" style="font-size:1.8rem;">{fuel}</div>
                <div style="color:#6B7280; font-size:0.85rem; margin-top:5px;">{eq}</div>
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.info("Utilisez les filtres pour afficher l'Asset Manager.")
