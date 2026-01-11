import streamlit as st
import pandas as pd

# 1. CONFIGURATION
st.set_page_config(page_title="Socobat Asset - Jeb", layout="wide", initial_sidebar_state="collapsed")

# 2. DESIGN SIGNATURE JEB (SANS FOND NOIR)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F4F7F9 !important; }
    .stApp { background-color: #F4F7F9 !important; }
    
    .brand-box { display: flex; align-items: center; gap: 12px; margin-bottom: 25px; }
    .logo-sq { background: white; padding: 10px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #E1E8ED; font-size: 1.5rem; }
    .t-main { font-size: 1.6rem; font-weight: 800; color: #111827 !important; }

    .m-card {
        background-color: white !important; padding: 24px; border-radius: 20px;
        border: 1px solid #E1E8ED; box-shadow: 0 4px 12px rgba(0,0,0,0.03); margin-bottom: 16px;
    }
    .m-lbl { color: #697689 !important; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
    .m-val { color: #111827 !important; font-size: 2.1rem; font-weight: 800; letter-spacing: -1.2px; }

    /* FIX NOIR IPHONE */
    input, [data-baseweb="select"], [data-baseweb="base-input"] {
        background-color: white !important; color: #111827 !important; border-radius: 12px !important;
    }
    div[data-baseweb="select"] > div { background-color: white !important; color: #111827 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. LOGIN
if "auth" not in st.session_state:
    st.markdown("<div style='text-align:center;padding-top:60px'><h1>🏢 Socobat</h1><p>A votre service by Jeb 😉</p></div>", unsafe_allow_html=True)
    pw = st.text_input("Code secret", type="password")
    if st.button("Se connecter", use_container_width=True):
        if pw == "SOCOBAT2026":
            st.session_state["auth"] = True
            st.rerun()
    st.stop()

# 4. DATA LOAD
@st.cache_data
def load():
    f1, f4 = "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx", "4 - UG SURFACES - NOVEMBRE 2024.xlsx"
    du = pd.read_excel(f4, sheet_name="SURFACES DES UG", dtype={'N° UG': str, 'GROUPE (HP2)': str})
    dc = pd.read_excel(f1, sheet_name="COLLECTIF + TRAVAUX", dtype={'HP2': str})
    du['N° UG'] = du['N° UG'].str.strip().str.zfill(6)
    du['GROUPE (HP2)'] = du['GROUPE (HP2)'].str.strip()
    dc['HP2'] = dc['HP2'].str.strip()
    return du, dc

try:
    du, dc = load()
    st.markdown('<div class="brand-box"><div class="logo-sq">🏢</div><div><div class="t-main">A votre service</div><div style="color:#697689">by Jeb 😉</div></div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        sel_h = st.selectbox("Groupe HP2", sorted(du['GROUPE (HP2)'].unique()), index=None, placeholder="Chercher...")
    
    if sel_h:
        with c2:
            sel_u = st.selectbox("N° UG", sorted(du[du['GROUPE (HP2)'] == sel_h]['N° UG'].unique()), index=None)

        if sel_u:
            u_row = du[(du['GROUPE (HP2)'] == sel_h) & (du['N° UG'] == sel_u)].iloc[0]
            s_imm = du[du['GROUPE (HP2)'] == sel_h]['SURFACE HABITABLE (SHA)'].sum()
            c_row = dc[dc['HP2'] == sel_h]

            st.markdown(f"<p style='color:#697689; font-weight:600;'>📍 {u_row['NOM GROUPE']}</p>", unsafe_allow_html=True)

            w1, w2 = st.columns(2)
            with w1:
                st.markdown(f'<div class="m-card"><span style="font-size:1.5rem">🏠</span><div class="m-lbl">Logement</div><div class="m-val">{u_row["SURFACE HABITABLE (SHA)"]} m²</div><div style="color:#4F46E5; font-size:0.8rem">Type {u_row["Type"]} • {u_row["Etage"]}</div></div>', unsafe_allow_html=True)
            with w2:
                st.markdown(f'<div class="m-card"><span style="font-size:1.5rem">🏢</span><div class="m-lbl">Immeuble</div><div class="m-val">{int(s_imm):,} m²</div><div style="color:#4F46E5; font-size:0.8rem">{len(du[du["GROUPE (HP2)"] == sel_h])} Logements</div></div>', unsafe_allow_html=True)

            # Chauffage
            is_c = not c_row.empty
            tag = '<span style="float:right; background:#D1FAE5; color:#065F46; padding:4px 12px; border-radius:20px; font-size:0.6rem; font-weight:700;">COLLECTIF</span>' if is_c else ""
            fuel = c_row['Type combustible'].iloc[0] if is_c else "Gaz Individuel"
            st.markdown(f'<div class="m-card">{tag}<span style="font-size:1.5rem">⚡</span><div class="m-lbl">Chauffage</div><div class="m-val" style="font-size:1.7rem">{fuel}</div></div>', unsafe_allow_html=True)

except Exception as e:
    st.info("Sélectionnez un groupe.")
