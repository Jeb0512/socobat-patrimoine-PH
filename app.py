import streamlit as st
import pandas as pd

# 1. CONFIGURATION
st.set_page_config(page_title="Socobat Asset", layout="wide", initial_sidebar_state="collapsed")

# 2. DESIGN MOLLIE (Clean & Minimalist)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #FFFFFF; }
    
    /* Cartes style Mollie */
    .card {
        background-color: #F9FAFB;
        padding: 32px;
        border-radius: 12px;
        border: 1px solid #E5E7EB;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .card:hover { border-color: #374151; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
    
    /* Typography */
    .lbl { color: #6B7280; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; }
    .val { color: #111827; font-size: 2rem; font-weight: 800; line-height: 1; }
    .sub { color: #374151; font-size: 0.9rem; margin-top: 8px; font-weight: 500; }
    
    /* Badge */
    .tag { background-color: #111827; color: white; padding: 6px 16px; border-radius: 100px; font-size: 0.7rem; font-weight: 700; }
    
    /* Bouton Mollie */
    .stButton>button {
        background-color: #111827; color: white; border-radius: 100px; 
        padding: 12px 24px; font-weight: 600; border: none; width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. AUTHENTIFICATION
if "auth" not in st.session_state:
    st.markdown("<div style='padding:80px 0; text-align:center'><h1>Socobat.</h1><p>Dashboard Accès Privé</p></div>", unsafe_allow_html=True)
    p = st.text_input("Code confidentiel", type="password")
    if st.button("Accéder au Dashboard"):
        if p == "SOCOBAT2026":
            st.session_state["auth"] = True
            st.rerun()
        else: st.error("Code erroné")
    st.stop()

# 4. DATA LOAD
@st.cache_data
def load_data():
    f1 = "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx"
    f3 = "3 - BATIMENTS_SURFACES_NOVEMBRE 2024.xlsx"
    f4 = "4 - UG SURFACES - NOVEMBRE 2024.xlsx"
    d1 = pd.read_excel(f1, sheet_name="COLLECTIF + TRAVAUX", dtype={'HP2': str})
    d3 = pd.read_excel(f3, sheet_name="SURFACES BATIMENTS", dtype={'GROUPE (HP2)': str})
    d4 = pd.read_excel(f4, sheet_name="SURFACES DES UG", dtype={'N° UG': str, 'GROUPE (HP2)': str})
    for d in [d1, d3, d4]:
        c = 'HP2' if 'HP2' in d.columns else 'GROUPE (HP2)'
        d[c] = d[c].str.strip()
    d4['N° UG'] = d4['N° UG'].str.strip().str.zfill(6)
    return d1, d3, d4

try:
    df1, df3, df4 = load_data()
    st.markdown("<h1 style='font-weight:800; letter-spacing:-1px'>Asset Manager.</h1>", unsafe_allow_html=True)

    # RECHERCHE
    c1, c2 = st.columns(2)
    with c1:
        hp2s = sorted(df4['GROUPE (HP2)'].dropna().unique())
        sel_h = st.selectbox("Groupe HP2", hp2s, index=None)
    
    if sel_h:
        with c2:
            ugs = sorted(df4[df4['GROUPE (HP2)'] == sel_h]['N° UG'].unique())
            sel_u = st.selectbox("Unité UG", ugs, index=None)

        if sel_u:
            # DATA
            u_row = df4[(df4['GROUPE (HP2)'] == sel_h) & (df4['N° UG'] == sel_u)].iloc[0]
            s_tot = df4[df4['GROUPE (HP2)'] == sel_h]['SURFACE HABITABLE (SHA)'].sum()
            c_row = df1[df1['HP2'] == sel_h]
            
            st.markdown(f"### {u_row['NOM GROUPE']}")

            # GRID MOLLIE
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"""<div class="card"><div class="lbl">Surface Logement</div><div class="val">{u_row['SURFACE HABITABLE (SHA)']} m²</div><div class="sub">Type {u_row['Type']} • Étage {u_row['Etage']}</div></div>""", unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""<div class="card"><div class="lbl">Total Immeuble</div><div class="val">{int(s_tot):,} m²</div><div class="sub">{len(df4[df4['GROUPE (HP2)'] == sel_h])} Unités</div></div>""", unsafe_allow_html=True)

            # CHAUFFAGE
            is_c = not c_row.empty
            tag = "COLLECTIF" if is_c else "INDIVIDUEL"
            t_ch = c_row['Type combustible'].iloc[0] if is_c else "Gaz Individuel"
            eq = c_row['Equipement'].iloc[0] if is_c else "Équipement privé"

            st.markdown(f"""<div class="card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:15px">
                    <div class="lbl" style="margin:0">Énergie & Chauffage</div><span class="tag">{tag}</span>
                </div>
                <div class="val" style="font-size:1.6rem">{t_ch}</div>
                <div class="sub">{eq}</div>
            </div>""", unsafe_allow_html=True)

except Exception as e:
    st.info("Sélectionnez un groupe pour commencer.")
