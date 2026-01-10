import streamlit as st
import pandas as pd

# Configuration Mode Sombre & Mobile
st.set_page_config(page_title="Socobat Asset", layout="wide", initial_sidebar_state="collapsed")

# Design Style Revolut (CSS Custom)
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #000000; color: #ffffff; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .stSelectbox div[data-baseweb="select"] { background-color: #1c1c1e; border-radius: 12px; border: none; color: white; }
    .metric-card { background-color: #1c1c1e; padding: 20px; border-radius: 16px; border: 1px solid #2c2c2e; margin-bottom: 10px; }
    .label { color: #8e8e93; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; }
    .value { color: #ffffff; font-size: 1.5rem; font-weight: 600; }
    .status-badge { background-color: #32d74b; color: black; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.7rem; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    df_ug = pd.read_excel("4 - UG SURFACES - NOVEMBRE 2024.xlsx", sheet_name="SURFACES DES UG", dtype={'N° UG': str, 'GROUPE (HP2)': str})
    df_bat = pd.read_excel("3 - BATIMENTS_SURFACES_NOVEMBRE 2024.xlsx", sheet_name="SURFACES BATIMENTS", dtype={'GROUPE (HP2)': str})
    df_coll = pd.read_excel("1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx", sheet_name="COLLECTIF + TRAVAUX", dtype={'HP2': str})
    df_ug['N° UG'] = df_ug['N° UG'].str.strip().str.zfill(6)
    return df_ug, df_bat, df_coll

try:
    df_ug, df_bat, df_coll = load_data()

    st.title("Asset Manager")
    
    # Zone de saisie ultra-compacte
    c_search1, c_search2 = st.columns(2)
    with c_search1:
        hp2_list = sorted(df_ug['GROUPE (HP2)'].dropna().unique())
        selected_hp2 = st.selectbox("Groupe", hp2_list, index=None, placeholder="Rechercher HP2...")
    
    if selected_hp2:
        with c_search2:
            ug_list = sorted(df_ug[df_ug['GROUPE (HP2)'] == selected_hp2]['N° UG'].unique())
            selected_ug = st.selectbox("Unité (UG)", ug_list, index=None, placeholder="Rechercher UG...")

        if selected_ug:
            # Extraction
            info_ug = df_ug[(df_ug['GROUPE (HP2)'] == selected_hp2) & (df_ug['N° UG'] == selected_ug)].iloc[0]
            surface_totale = df_ug[df_ug['GROUPE (HP2)'] == selected_hp2]['SURFACE HABITABLE (SHA)'].sum()
            info_coll = df_coll[df_coll['HP2'] == selected_hp2]

            # Affichage style Cartes Revolut
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Ligne 1 : Les surfaces
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""<div class="metric-card"><div class="label">Surface Logement</div><div class="value">{info_ug['SURFACE HABITABLE (SHA)']} m²</div></div>""", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""<div class="metric-card"><div class="label">Surface Immeuble</div><div class="value">{int(surface_totale)} m²</div></div>""", unsafe_allow_html=True)

            # Ligne 2 : Chauffage
            is_coll = not info_coll.empty
            badge = '<span class="status-badge">COLLECTIF</span>' if is_coll else '<span class="status-badge" style="background:#ff453a">INDIVIDUEL</span>'
            
            st.markdown(f"""
                <div class="metric-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div class="label">Système de chauffage</div>
                        {badge}
                    </div>
                    <div class="value" style="margin-top:10px;">{info_coll['Type combustible'].iloc[0] if is_coll else "Équipement individuel"}</div>
                    <div style="color:#8e8e93; font-size:0.9rem;">{info_coll['Equipement'].iloc[0] if is_coll else "Gestion par le locataire"}</div>
                </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Erreur : {e}")