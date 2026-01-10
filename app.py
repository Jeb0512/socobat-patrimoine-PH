import streamlit as st
import pandas as pd

# 1. CONFIGURATION
st.set_page_config(page_title="Socobat Asset", layout="wide", initial_sidebar_state="collapsed")

# 2. DESIGN CSS
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .card {
        background-color: white; padding: 20px; border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 16px; border: 1px solid #edf2f7;
    }
    .card-label { color: #718096; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
    .card-value { color: #1a202c; font-size: 1.5rem; font-weight: 800; margin: 10px 0; }
    .badge { background-color: #c6f6d5; color: #22543d; padding: 4px 12px; border-radius: 99px; font-size: 0.75rem; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# 3. MOT DE PASSE
if "auth" not in st.session_state:
    st.title("🔒 Accès Socobat")
    pwd = st.text_input("Code d'accès", type="password")
    if st.button("Connexion"):
        if pwd == "SOCOBAT2026":
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Code incorrect")
    st.stop()

# 4. CHARGEMENT DES DONNÉES
@st.cache_data
def load_data():
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
    df_ug, df_bat, df_coll = load_data()
    st.markdown("### 🏢 Asset Manager")

    # RECHERCHE
    c1, c2 = st.columns(2)
    with c1:
        list_hp2 = sorted(df_ug['GROUPE (HP2)'].dropna().unique())
        sel_hp2 = st.selectbox("Groupe HP2", list_hp2, index=None)
    
    if sel_hp2:
        with c2:
            list_ug = sorted(df_ug[df_ug['GROUPE (HP2)'] == sel_hp2]['N° UG'].unique())
            sel_ug = st.selectbox("Numéro UG", list_ug, index=None)

        if sel_ug:
            row_ug = df_ug[(df_ug['GROUPE (HP2)'] == sel_hp2) & (df_ug['N° UG'] == sel_ug)].iloc[0]
            surf_tot = df_ug[df_ug['GROUPE (HP2)'] == sel_hp2]['SURFACE HABITABLE (SHA)'].sum()
            row_coll = df_coll[df_coll['HP2'] == sel_hp2]

            st.info(f"📍 {row_ug['NOM GROUPE']}")

            # CARTES
            col_a, col_b = st.columns(2)
            with col_a:
                html_ug = f"""<div class="card"><div class="card-label">Logement</div><div class="card-value">{row_ug['SURFACE HABITABLE (SHA)']} m²</div><div style="color:gray">{row_ug['Type']}</div></div>"""
                st.markdown(html_ug, unsafe_allow_html=True)
            with col_b:
                html_bat = f"""<div class="card"><div class="card-label">Immeuble Total</div><div class="card-value">{int(surf_tot)} m²</div><div style="color:gray">{len(df_ug[df_ug['GROUPE (HP2)'] == sel_hp2])} Logements</div></div>"""
                st.markdown(html_bat, unsafe_allow_html=True)

            # CHAUFFAGE
            is_c = not row_coll.empty
            badge = "COLLECTIF" if is_c else "INDIVIDUEL"
            type_ch = row_coll['Type combustible'].iloc[0] if is_c else "Individuel / Gaz"
            
            html_ch = f"""<div class="card"><div style="display:flex;justify-content:space-between"><div class="card-label">Chauffage</div><span class="badge">{badge}</span></div><div class="card-value">{type_ch}</div></div>"""
            st.markdown(html_ch, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Erreur : {e}")
