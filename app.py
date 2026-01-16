import streamlit as st
import pandas as pd

# 1. CONFIG PAGE
st.set_page_config(
    page_title="Socobat Asset - Jeb",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. DESIGN SYSTEM
st.markdown("""
    <style>
    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #F9FAFB !important;
    }
    div[data-baseweb="select"], div[data-baseweb="base-input"], input {
        background-color: white !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 12px !important;
    }
    div[role="listbox"] div, span[data-baseweb="select"] {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
    }
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
    h1, h2, h3, p, label { color: #111827 !important; font-weight: 600 !important; }
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

# 4. CHARGEMENT DES DONNÉES (CSV)
@st.cache_data
def load_ug():
    df = pd.read_csv("ug_surfaces.csv", dtype=str)
    # harmonisation éventuelle
    if "N° UG" in df.columns and "N°UG" not in df.columns:
        df = df.rename(columns={"N° UG": "N°UG"})
    return df

@st.cache_data
def load_chauffage_ind():
    return pd.read_csv("chauffage_individuel.csv", dtype=str)

@st.cache_data
def load_chauffage_coll():
    return pd.read_csv("chauffage_collectif.csv", dtype=str)

@st.cache_data
def load_pv():
    return pd.read_csv("pv.csv", dtype=str)

@st.cache_data
def load_thermique():
    return pd.read_csv("thermique.csv", dtype=str)

try:
    df_ug = load_ug()
    df_ind = load_chauffage_ind()
    df_coll = load_chauffage_coll()
    df_pv = load_pv()
    df_th = load_thermique()

    st.markdown("<h2>🏢 Assistant DPE logement – Socobat Asset</h2>", unsafe_allow_html=True)

    # 5. SÉLECTION HP2 / UG
    hp2_list = sorted(df_ug['GROUPE HP2'].dropna().unique())
    col1, col2 = st.columns(2)
    with col1:
        sel_h = st.selectbox("Groupe HP2", hp2_list, index=None, placeholder="Choisir...")
    sel_u = None
    if sel_h:
        ug_list = sorted(df_ug[df_ug['GROUPE HP2'] == sel_h]['N°UG'].dropna().unique())
        with col2:
            sel_u = st.selectbox("Unité UG", ug_list, index=None, placeholder="Choisir...")

    if sel_h and sel_u:
        # Données UG
        u_row = df_ug[(df_ug['GROUPE HP2'] == sel_h) & (df_ug['N°UG'] == sel_u)]
        if u_row.empty:
            st.warning("Aucune donnée UG trouvée pour cette combinaison.")
            st.stop()
        u_data = u_row.iloc[0]

        # SHA numérique + totaux par HP2 et par adresse
        df_ug['SHA_NUM'] = pd.to_numeric(df_ug.get('SURFACE HABITABLE (SHA)', pd.Series([None]*len(df_ug))), errors='coerce')
        total_immeuble = df_ug[df_ug['GROUPE HP2'] == sel_h]['SHA_NUM'].sum()

        adresse_col = 'Adresse' if 'Adresse' in df_ug.columns else None
        if adresse_col:
            adresse_ug = u_data[adresse_col]
            mask_same_addr = (df_ug['GROUPE HP2'] == sel_h) & (df_ug[adresse_col] == adresse_ug)
            total_addr = df_ug[mask_same_addr]['SHA_NUM'].sum()
            nb_ug_addr = mask_same_addr.sum()
        else:
            adresse_ug = "Adresse non disponible"
            total_addr = None
            nb_ug_addr = None

        st.markdown(f"<p style='color:#6366F1; font-weight:700; margin-left:5px;'>📍 {sel_h} – UG {sel_u}</p>", unsafe_allow_html=True)

        # 6. CARTES SURFACES
        c_a, c_b = st.columns(2)
        with c_a:
            st.markdown(f"""
            <div class="alan-card">
                <div class="t-label">🏠 LOGEMENT (UG)</div>
                <div class="t-val">{u_data.get('SURFACE HABITABLE (SHA)', 'NC')} m²</div>
                <div class="t-sub">Type {u_data.get('Type', 'NC')} • Etage {u_data.get('Etage', 'NC')}</div>
            </div>
            """, unsafe_allow_html=True)
        with c_b:
            st.markdown(f"""
            <div class="alan-card">
                <div class="t-label">🏢 IMMEUBLE (HP2)</div>
                <div class="t-val">{int(total_immeuble) if pd.notna(total_immeuble) else 'NC'} m²</div>
                <div class="t-sub">{len(df_ug[df_ug['GROUPE HP2'] == sel_h])} logements</div>
            </div>
            """, unsafe_allow_html=True)

        if adresse_col:
            st.markdown(f"""
            <div class="alan-card">
                <div class="t-label">📏 SOMME DES SURFACES PAR ADRESSE</div>
                <div class="t-val">{int(total_addr) if pd.notna(total_addr) else 'NC'} m²</div>
                <div class="t-sub">{nb_ug_addr} UG • {adresse_ug}</div>
            </div>
            """, unsafe_allow_html=True)

        # 7. CHAUFFAGE INDIVIDUEL
        st.markdown("### 🔥 Chauffage individuel")
        ind_rows = df_ind[df_ind['GROUPE HP2'] == sel_h]
        if not ind_rows.empty:
            # si tu as une colonne N°UG dans cette base, filtre aussi dessus
            if 'N°UG' in ind_rows.columns:
                ind_rows = ind_rows[ind_rows['N°UG'] == sel_u]
            if not ind_rows.empty:
                for _, r in ind_rows.iterrows():
                    st.markdown(f"""
                    <div class="alan-card">
                        <div class="t-label">Chaudière individuelle</div>
                        <div class="t-sub">{r.get('Modèle', r.get('Modèles des chaudières', 'Modèle NC'))}</div>
                        <p>Type : {r.get('Type', 'NC')}<br>
                        Année : {r.get('Années (chaudières & chauffe-bains)', 'NC')}<br>
                        Nb équipements : {r.get('Nb d\'équipements individuels gaz', 'NC')}<br>
                        Travaux : {r.get('Travaux réalisés', 'NC')} – {r.get('Date d\'achèvement travaux', 'NC')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Pas de chauffage individuel spécifique à cette UG.")
        else:
            st.info("Pas de données de chauffage individuel pour ce HP2.")

        # 8. CHAUFFAGE COLLECTIF
        st.markdown("### 🏢 Chauffage collectif")
        coll_rows = df_coll[df_coll['GROUPE HP2'] == sel_h] if 'GROUPE HP2' in df_coll.columns else df_coll[df_coll['Code HP2'] == sel_h]
        if not coll_rows.empty:
            for _, r in coll_rows.iterrows():
                st.markdown(f"""
                <div class="alan-card">
                    <div class="t-label">Chauffage collectif</div>
                    <p>Type chaudière : {r.get('Type de chaudière', 'NC')}<br>
                    Énergie : {r.get('Type d\'énergie', 'NC')}<br>
                    Nb équipements : {r.get('Nb d\'équipements collectifs', 'NC')}<br>
                    Travaux : {r.get('Travaux réalisés', 'NC')} – {r.get('Date d\'achèvement travaux', 'NC')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Pas de données de chauffage collectif pour ce HP2.")

        # 9. PANNEAUX SOLAIRES PV
        st.markdown("### ☀️ Panneaux solaires photovoltaïques")
        pv_rows = df_pv[df_pv['Code HP2'] == sel_h] if 'Code HP2' in df_pv.columns else df_pv[df_pv['GROUPE HP2'] == sel_h]
        if not pv_rows.empty:
            for _, r in pv_rows.iterrows():
                st.markdown(f"""
                <div class="alan-card">
                    <div class="t-label">PV – {r.get('Nom du groupe', r.get('Nom', ''))}</div>
                    <p>Surface : {r.get('Surface totale de capteurs', 'NC')} m²<br>
                    Nb capteurs : {r.get('Nb de capteurs', 'NC')}<br>
                    Type : {r.get('Type de capteurs', 'NC')}<br>
                    Inclinaison : {r.get('Inclinaison [°/hor]', 'NC')}<br>
                    Orientation : {r.get('Orientation [°/Sud]', r.get('Orientation', 'NC'))}<br>
                    État : {r.get('Etat de l\'installation', r.get('Etat des lieux', 'NC'))}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Pas de PV recensés pour ce HP2.")

        # 10. PANNEAUX SOLAIRES THERMIQUES
        st.markdown("### ♨️ Panneaux solaires thermiques")
        th_rows = df_th[df_th['Code HP2'] == sel_h] if 'Code HP2' in df_th.columns else df_th[df_th['GROUPE HP2'] == sel_h]
        if not th_rows.empty:
            for _, r in th_rows.iterrows():
                st.markdown(f"""
                <div class="alan-card">
                    <div class="t-label">Thermique – {r.get('Nom', r.get('Nom du groupe', ''))}</div>
                    <p>Surface : {r.get('Surface totale des capteurs (m2)', 'NC')} m²<br>
                    Nb capteurs : {r.get('Nb de capteurs', 'NC')}<br>
                    Type : {r.get('Type de capteurs', 'NC')}<br>
                    Inclinaison : {r.get('Inclinaison [°/hor]', 'NC')}<br>
                    Orientation : {r.get('Orientation', 'NC')}<br>
                    État : {r.get('Etat des lieux', r.get('Etat de l\'installation', 'NC'))}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Pas de solaire thermique recensé pour ce HP2.")

        # 11. RÉSUMÉ DES TRAVAUX
        st.markdown("### 🛠️ Résumé des travaux")
        resume = []

        # Chauffage indiv
        if not ind_rows.empty:
            for _, r in ind_rows.iterrows():
                resume.append(f"Chauffage individuel : {r.get('Travaux réalisés', 'NC')} ({r.get('Date d\'achèvement travaux', 'NC')})")

        # Chauffage coll
        if not coll_rows.empty:
            for _, r in coll_rows.iterrows():
                resume.append(f"Chauffage collectif : {r.get('Travaux réalisés', 'NC')} ({r.get('Date d\'achèvement travaux', 'NC')})")

        # PV
        if not pv_rows.empty:
            for _, r in pv_rows.iterrows():
                resume.append(f"PV : {r.get('Etat de l\'installation', 'NC')} – {r.get('Adresse', r.get('Adresse', ''))}")

        # Thermique
        if not th_rows.empty:
            for _, r in th_rows.iterrows():
                resume.append(f"Thermique : {r.get('Etat des lieux', 'NC')} – {r.get('Adresse', r.get('Adresse', ''))}")

        if resume:
            st.markdown("<div class='alan-card'>", unsafe_allow_html=True)
            for line in resume:
                st.markdown(f"- {line}")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Aucun travail recensé dans les bases pour ce HP2 / cette UG.")

except Exception as e:
    st.error(f"Erreur lors du chargement ou de l'affichage des données : {e}")
