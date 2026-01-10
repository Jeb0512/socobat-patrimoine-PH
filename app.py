import streamlit as st
import pandas as pd

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="Socobat Asset",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. DESIGN FINTECH PREMIUM (CSS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #FFFFFF; }
    
    /* Cartes Widget */
    .widget {
        background-color: #F9FAFB;
        padding: 24px;
        border-radius: 24px;
        border: 1px solid #F2F4F7;
        margin-bottom: 16px;
    }
    
    /* Typographie */
    .icon { font-size: 1.5rem; margin-bottom: 12px; }
    .label { color: #667085; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; }
    .value { color: #101828; font-size: 1.75rem; font-weight: 800; margin: 4px 0; }
    .subtext { color: #0052FF; font-size: 0.85rem; font-weight: 600; }
    
    /* Badges */
    .status-tag {
        float: right;
        background-color: #101828;
        color: white;
        padding: 6px 14px;
        border-radius: 100px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    .badge-green { background-color: #ECFDF3; color: #027A48; border: 1px solid #ABEFC6; }

    /* Inputs Mobile-ready */
    div[data-baseweb="select"] { 
        border-radius: 16px !important; 
        border: 1px solid #D0D5DD !important;
        background: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. AUTHENTIFICATION (SOCOBAT2026)
if "authenticated" not in st.session_state:
    st.markdown("<div style='padding:60px 0; text-align:center'><h1>Socobat.</h1><p>Asset Management Portal</p></div>", unsafe_allow_html=True)
    with st.container():
        _, col_mid, _ = st.columns([1,4,1])
        with col_mid:
            pwd = st.text_input("Code d'accès", type="password")
            if st.button("Se connecter", use_container_width=True):
                if pwd == "SOCOBAT2026":
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("Code incorrect")
    st.stop()

# 4. CHARGEMENT DES DONNÉES (Noms longs originaux)
@st.cache_data
def load_all_data():
    f_coll = "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx"
    f_bat = "3 - BATIMENTS_SURFACES_NOVEMBRE 2024.xlsx"
    f_ug = "4 - UG SURFACES - NOVEMBRE 2024.xlsx"
    
    # Lecture Excel
    d_ug = pd.read_excel(f_ug, sheet_name="SURFACES DES UG", dtype={'N° UG': str, 'GROUPE (HP2)': str})
    d_bat = pd.read_excel(f_bat, sheet_name="SURFACES BATIMENTS", dtype={'GROUPE (HP2)': str})
    d_coll = pd.read_excel(f_coll, sheet_name="COLLECTIF + TRAVAUX", dtype={'HP2': str})
    
    # Nettoyage
    d_ug['N° UG'] = d_ug['N° UG'].str.strip().str.zfill(6)
    d_ug['GROUPE (HP2)'] = d_ug['GROUPE (HP2)'].str.strip()
    d_coll['HP2'] = d_coll['HP2'].str.strip()
    
    return d_ug, d_bat, d_coll

try:
    df_ug, df_bat, df_coll = load_all_data()

    # TITRE PRINCIPAL
    st.markdown("<h1 style='font-weight:800; letter-spacing:-1px; color:#101828;'>Dashboard.</h1>", unsafe_allow_html=True)

    # ZONE DE RECHERCHE (Appelle le clavier sur iPhone)
    col_search1, col_search2 = st.columns(2)
    with col_search1:
        hp2_list = sorted(df_ug['GROUPE (HP2)'].dropna().unique())
        selected_hp2 = st.selectbox("Groupe (HP2)", hp2_list, index=None, placeholder="Rechercher HP2...")
    
    if selected_hp2:
        with col_search2:
            ug_list = sorted(df_ug[df_ug['GROUPE (HP2)'] == selected_hp2]['N° UG'].unique())
            selected_ug = st.selectbox("Unité (UG)", ug_list, index=None, placeholder="N° UG...")

        if selected_ug:
            # Extraction des infos
            u_info = df_ug[(df_ug['GROUPE (HP2)'] == selected_hp2) & (df_ug['N° UG'] == selected_ug)].iloc[0]
            s_immeuble = df_ug[df_ug['GROUPE (HP2)'] == selected_hp2]['SURFACE HABITABLE (SHA)'].sum()
            c_info = df_coll[df_coll['HP2'] == selected_hp2]

            st.markdown(f"#### 📍 {u_info['NOM GROUPE']}")

            # AFFICHAGE EN GRILLE MOBILE
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown(f"""
                <div class="widget">
                    <div class="icon">🏠</div>
                    <div class="label">Surface Logement</div>
                    <div class="value">{u_info['SURFACE HABITABLE (SHA)']} m²</div>
                    <div class="subtext">{u_info['Type']} • Etage {u_info['Etage']}</div>
                </div>
                """, unsafe_allow_html=True)

            with c2:
                st.markdown(f"""
                <div class="widget">
                    <div class="icon">🏢</div>
                    <div class="label">Surface Immeuble</div>
                    <div class="value">{int(s_immeuble):,} m²</div>
                    <div class="subtext">{len(df_ug[df_ug['GROUPE (HP2)'] == selected_hp2])} Logements</div>
                </div>
                """, unsafe_allow_html=True)

            # SECTION ÉNERGIE
            is_collectif = not c_info.empty
            status_text = "COLLECTIF" if is_collectif else "INDIVIDUEL"
            badge_style = "badge-green" if is_collectif else ""
            energy_type = c_info['Type combustible'].iloc[0] if is_collectif else "Gaz Individuel"
            details = c_info['Equipement'].iloc[0] if is_collectif else "Chaudière privée"

            st.markdown(f"""
            <div class="widget">
                <span class="status-tag {badge_style}">{status_text}</span>
                <div class="icon">⚡</div>
                <div class="label">Énergie & Chauffage</div>
                <div class="value" style="font-size:1.5rem;">{energy_type}</div>
                <div class="subtext" style="color:#667085">{details}</div>
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.info("Veuillez sélectionner un code HP2 pour afficher les données.")
