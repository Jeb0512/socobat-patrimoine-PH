import streamlit as st
import pandas as pd

# 1. CONFIGURATION
st.set_page_config(page_title="Socobat Business", layout="wide", initial_sidebar_state="collapsed")

# 2. STYLE REVOLUT BUSINESS (Dark/Light Contrast)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #F9FAFB; }
    
    /* Widget Card Style */
    .widget-card {
        background-color: white;
        padding: 24px;
        border-radius: 24px;
        border: 1px solid #F2F4F7;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    /* Typography & Icons */
    .icon-header { font-size: 1.5rem; margin-bottom: 10px; }
    .stat-label { color: #667085; font-size: 0.85rem; font-weight: 600; margin-bottom: 4px; }
    .stat-value { color: #101828; font-size: 1.75rem; font-weight: 700; letter-spacing: -0.02em; }
    .stat-desc { color: #0052FF; font-size: 0.85rem; font-weight: 600; margin-top: 8px; }
    
    /* Badge Status */
    .status-badge {
        background-color: #F2F4F7;
        color: #344054;
        padding: 6px 14px;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 700;
        float: right;
    }
    .badge-energy { background-color: #ECFDF3; color: #027A48; }

    /* Custom Search Input */
    div[data-baseweb="select"] { border-radius: 16px !important; border: 1px solid #D0D5DD !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. AUTHENTIFICATION REVOLUT STYLE
if "auth" not in st.session_state:
    st.markdown("<div style='padding:60px 0; text-align:center'><h2>Socobat.</h2><p style='color:#667085'>Business Asset Manager</p></div>", unsafe_allow_html=True)
    with st.container():
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            pw = st.text_input("Code de sécurité", type="password")
            if st.button("S'identifier", use_container_width=True):
                if pw == "SOCOBAT2026":
                    st.session_state["auth"] = True
                    st.rerun()
                else: st.error("Accès refusé")
    st.stop()

# 4. LOAD DATA
@st.cache_data
def load():
    f1 = "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx"
    f3 = "3 - BATIMENTS_SURFACES_NOVEMBRE 2024.xlsx"
    f4 = "4 - UG SURFACES - NOVEMBRE 2024.xlsx"
    d1 = pd.read_excel(f1, sheet_name="COLLECTIF + TRAVAUX", dtype={'HP2': str})
    d3 = pd.read_excel(f3, sheet_name="SURFACES BATIMENTS", dtype={'GROUPE (HP2)': str})
    d4 = pd.read_excel(f4, sheet_name="SURFACES DES UG", dtype={'N° UG': str, 'GROUPE (HP2)': str})
    for d in [d1, d3, d4]:
        col = 'HP2' if 'HP2' in d.columns else 'GROUPE (HP2)'
        d[col] = d[col].str.strip()
    d4['N° UG'] = d4['N° UG'].str.strip().str.zfill(6)
    return d1, d3, d4

try:
    df1, df3, df4 = load()
    
    # NAVIGATION / HEADER
    st.markdown("<h1 style='font-weight:700; color:#101828; margin-bottom:30px'>Dashboard.</h1>", unsafe_allow_html=True)

    # RECHERCHE
    row_search = st.columns([1.5, 1])
    with row_search[0]:
        list_hp2 = sorted(df4['GROUPE (HP2)'].dropna().unique())
        sel_hp2 = st.selectbox("Groupe Patrimonial (HP2)", list_hp2, index=None, placeholder="Sélectionner HP2")
    
    if sel_hp2:
        with row_search[1]:
            list_ug = sorted(df4[df4['GROUPE (HP2)'] == sel_hp2]['N° UG'].unique())
            sel_ug = st.selectbox("Unité de Gestion (UG)", list_ug, index=None, placeholder="N° UG")

        if sel_ug:
            # DATA PREP
            u = df4[(df4['GROUPE (HP2)'] == sel_hp2) & (df4['N° UG'] == sel_ug)].iloc[0]
            s_t = df4[df4['GROUPE (HP2)'] == sel_hp2]['SURFACE HABITABLE (SHA)'].sum()
            c = df1[df1['HP2'] == sel_hp2]
            
            st.markdown(f"#### 📍 {u['NOM GROUPE']}")

            # WIDGETS SECTION
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown(f"""
                <div class="widget-card">
                    <div class="icon-header">🏠</div>
                    <div class="stat-label">Surface Habitable UG</div>
                    <div class="stat-value">{u['SURFACE HABITABLE (SHA)']} m²</div>
                    <div class="stat-desc">Type {u['Type']} • Etage {u['Etage']}</div>
                </div>
                """, unsafe_allow_html=True)

            with col_b:
                st.markdown(f"""
                <div class="widget-card">
                    <div class="icon-header">🏢</div>
                    <div class="stat-label">Total Groupe HP2</div>
                    <div class="stat-value">{int(s_t):,} m²</div>
                    <div class="stat-desc">{len(df4[df4['GROUPE (HP2)'] == sel_hp2])} Logements gérés</div>
                </div>
                """, unsafe_allow_html=True)

            # ENERGY SECTION
            is_c = not c.empty
            tag_label = "COLLECTIF" if is_c else "INDIVIDUEL"
            badge_class = "badge-energy" if is_c else ""
            energy_val = c['Type combustible'].iloc[0] if is_c else "Gaz / Electrique"
            equip_val = c['Equipement'].iloc[0] if is_c else "Equipement Individuel"

            st.markdown(f"""
            <div class="widget-card">
                <div style="display:flex; justify-content:space-between; align-items:start;">
                    <div>
                        <div class="icon-header">⚡</div>
                        <div class="stat-label">Énergie & Chauffage</div>
                        <div class="stat-value">{energy_val}</div>
                    </div>
                    <span class="status-badge {badge_class}">{tag_label}</span>
                </div>
                <div class="stat-desc" style="color:#667085">{equip_val}</div>
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.info("Utilisez les filtres ci-dessus pour consulter le patrimoine.")
