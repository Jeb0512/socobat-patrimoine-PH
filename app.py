import streamlit as st
import pandas as pd
import os

# --- CONSTANTES DE COLONNES (Pour éviter les erreurs de syntaxe) ---
COL_ANNEE_INDIV = 'Années (chaudières & chauffe-bains)\nà titre indicatif'
COL_NB_EQUIP_INDIV = "Nb d'équipements individuels gaz"
COL_TRAVAUX_INDIV = 'Travaux réalisés'
COL_TRAVAUX_COLL = 'Travaux réalisés'
COL_DATE_TRAVAUX_COLL = "Date d'achèvement travaux"
COL_SYSTEME_COLL = "Systeme_Type"

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

# 4. GESTION FICHIERS
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

FILES_MAPPING = {
    "ug": "4 - UG SURFACES - NOVEMBRE 2024.xlsx - SURFACES DES UG.csv",
    "batiments": "3 - BATIMENTS_SURFACES_NOVEMBRE 2024.xlsx - SURFACES BATIMENTS.csv",
    "ind": "2-EQUIPEMENTS CHAUFFAGE INDIVIDUEL_NOVEMBRE 2024.xlsx - BDD CIgaz.csv",
    "coll": "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx - COLLECTIF + TRAVAUX.csv",
    "pv": "5 - PANNEAUX SOLAIRES_NOVEMBRE 2024.xlsx - InfoPV.csv",
    "th": "5 - PANNEAUX SOLAIRES_NOVEMBRE 2024.xlsx - Thermique.csv"
}

def clean_columns(df):
    df.columns = df.columns.str.strip()
    return df

def get_path(filename):
    return os.path.join(CURRENT_DIR, filename)

def safe_get(row, key, default=''):
    """Récupère une valeur de manière sécurisée (gère NaN et strings vides)"""
    val = row.get(key, default)
    if pd.isna(val) or str(val).lower() in ['nan', 'none', '']:
        return default if default else ""
    return str(val)

@st.cache_data
def load_data():
    data = {}
    missing_files = []
    
    # 1. UG
    path_ug = get_path(FILES_MAPPING["ug"])
    if os.path.exists(path_ug):
        df = pd.read_csv(path_ug, dtype=str)
        df = clean_columns(df)
        df = df.rename(columns={"N° UG": "N°UG", "GROUPE (HP2)": "GROUPE HP2"})
        data["ug"] = df
    else:
        missing_files.append(FILES_MAPPING["ug"])

    # 2. Batiments
    path_bat = get_path(FILES_MAPPING["batiments"])
    if os.path.exists(path_bat):
        df = pd.read_csv(path_bat, dtype=str)
        df = clean_columns(df)
        df = df.rename(columns={"GROUPE (HP2)": "GROUPE HP2"})
        data["batiments"] = df
    
    # 3. Indiv
    path_ind = get_path(FILES_MAPPING["ind"])
    if os.path.exists(path_ind):
        df = pd.read_csv(path_ind, dtype=str, header=2)
        df = clean_columns(df)
        df = df.rename(columns={"HP2": "GROUPE HP2"})
        data["ind"] = df
    else:
        data["ind"] = pd.DataFrame()

    # 4. Collectif
    path_coll = get_path(FILES_MAPPING["coll"])
    if os.path.exists(path_coll):
        df = pd.read_csv(path_coll, dtype=str)
        df = clean_columns(df)
        df = df.rename(columns={
            "HP2": "GROUPE HP2", 
            "Type combustible": "Energie",
            "Type d'équipement": COL_SYSTEME_COLL
        })
        data["coll"] = df
    else:
        data["coll"] = pd.DataFrame()

    # 5. PV
    path_pv = get_path(FILES_MAPPING["pv"])
    if os.path.exists(path_pv):
        df = pd.read_csv(path_pv, dtype=str)
        df = clean_columns(df)
        if "Code HP2" in df.columns:
            df = df.rename(columns={"Code HP2": "GROUPE HP2"})
        data["pv"] = df
    else:
        data["pv"] = pd.DataFrame()

    # 6. Thermique
    path_th = get_path(FILES_MAPPING["th"])
    if os.path.exists(path_th):
        df = pd.read_csv(path_th, dtype=str)
        df = clean_columns(df)
        if "Code HP2" in df.columns:
            df = df.rename(columns={"Code HP2": "GROUPE HP2"})
        data["th"] = df
    else:
        data["th"] = pd.DataFrame()
        
    return data, missing_files

# --- APP ---
datasets, missing = load_data()

if "ug" not in datasets:
    st.error("❌ ERREUR : Fichier UG introuvable.")
    st.stop()

try:
    df_ug = datasets["ug"]
    df_bat = datasets.get("batiments", pd.DataFrame())
    df_ind = datasets["ind"]
    df_coll = datasets["coll"]
    df_pv = datasets["pv"]
    df_th = datasets["th"]

    st.markdown("<h2>🏢 Assistant DPE logement – Socobat Asset</h2>", unsafe_allow_html=True)

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
        u_row = df_ug[(df_ug['GROUPE HP2'] == sel_h) & (df_ug['N°UG'] == sel_u)]
        if u_row.empty:
            st.warning("UG introuvable.")
            st.stop()
        
        u_data = u_row.iloc[0]

        # CALCULS
        df_ug['SHA_NUM'] = pd.to_numeric(df_ug.get('SURFACE HABITABLE (SHA)', pd.Series([0]*len(df_ug))), errors='coerce').fillna(0)
        total_immeuble = df_ug[df_ug['GROUPE HP2'] == sel_h]['SHA_NUM'].sum()

        adresse_ug = "Adresse non disponible"
        if 'Adresse' in u_data and pd.notna(u_data['Adresse']):
            adresse_ug = u_data['Adresse']
        elif not df_bat.empty:
            bat_info = df_bat[df_bat['GROUPE HP2'] == sel_h]
            if not bat_info.empty:
                adresse_ug = bat_info.iloc[0].get('Adresse', 'Adresse NC')
        
        nb_ug_addr = len(df_ug[df_ug['GROUPE HP2'] == sel_h])
        
        st.markdown(f"<p style='color:#6366F1; font-weight:700; margin-left:5px;'>📍 {sel_h} – UG {sel_u}</p>", unsafe_allow_html=True)

        # 1. Surfaces
        val_sha = safe_get(u_data, 'SURFACE HABITABLE (SHA)', 'NC')
        val_type = safe_get(u_data, 'Type', 'NC')
        val_etage = safe_get(u_data, 'Etage', 'NC')
        
        c_a, c_b = st.columns(2)
        with c_a:
            st.markdown(f"""
            <div class="alan-card">
                <div class="t-label">🏠 LOGEMENT (UG)</div>
                <div class="t-val">{val_sha} m²</div>
                <div class="t-sub">Type {val_type} • Etage {val_etage}</div>
            </div>
            """, unsafe_allow_html=True)
        with c_b:
            st.markdown(f"""
            <div class="alan-card">
                <div class="t-label">🏢 GROUPE (HP2)</div>
                <div class="t-val">{int(total_immeuble)} m²</div>
                <div class="t-sub">{nb_ug_addr} logements • {adresse_ug}</div>
            </div>
            """, unsafe_allow_html=True)

        # 2. Indiv
        st.markdown("### 🔥 Chauffage individuel")
        ind_rows = pd.DataFrame()
        if not df_ind.empty and 'GROUPE HP2' in df_ind.columns:
            ind_rows = df_ind[df_ind['GROUPE HP2'] == sel_h]
            
        if not ind_rows.empty:
            for _, r in ind_rows.iterrows():
                modele = safe_get(r, 'Modèle', '') or safe_get(r, 'Modèles des chaudières', 'Modèle non détecté')
                annee = safe_get(r, COL_ANNEE_INDIV, 'NC')
                nb_eq = safe_get(r, COL_NB_EQUIP_INDIV, 'NC')
                trav = safe_get(r, COL_TRAVAUX_INDIV, 'NC')

                st.markdown(f"""
                <div class="alan-card">
                    <div class="t-label">Chaudière Individuelle</div>
                    <div class="t-sub">{modele}</div>
                    <p>Année : {annee}<br>Nb équipements : {nb_eq}<br>Travaux : {trav}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Pas de chauffage individuel gaz recensé pour ce groupe.")

        # 3. Collectif (LE CORRECTIF PRINCIPAL EST ICI)
        st.markdown("### 🏢 Chauffage collectif")
        coll_rows = pd.DataFrame()
        if not df_coll.empty and 'GROUPE HP2' in df_coll.columns:
            coll_rows = df_coll[df_coll['GROUPE HP2'] == sel_h]

        if not coll_rows.empty:
            for _, r in coll_rows.iterrows():
                sys_t = safe_get(r, COL_SYSTEME_COLL, 'NC')
                marque = safe_get(r, 'Marque')
                mod = safe_get(r, 'Modèle')
                energie = safe_get(r, 'Energie', 'NC')
                trav = safe_get(r, COL_TRAVAUX_COLL, 'Aucun travaux récents')
                date_trav = safe_get(r, COL_DATE_TRAVAUX_COLL, '-')
                
                # Construction propre de la description
                desc_sys = sys_t
                if marque:
                    desc_sys += f" - {marque}"
                if mod:
                    desc_sys += f" ({mod})"

                st.markdown(f"""
                <div class="alan-card">
                    <div class="t-label">Chaufferie Collective</div>
                    <div class="t-sub">Système : {desc_sys}</div>
                    <div class="t-val" style="font-size: 1.5rem !important;">Énergie : {energie}</div>
                    <p style="margin-top:10px;">Travaux : {trav}<br>Date : {date_trav}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Pas de chauffage collectif recensé pour ce HP2.")

        # 4. PV
        st.markdown("### ☀️ Panneaux solaires PV")
        pv_rows = pd.DataFrame()
        if not df_pv.empty and 'GROUPE HP2' in df_pv.columns:
            pv_rows = df_pv[df_pv['GROUPE HP2'] == sel_h]

        if not pv_rows.empty:
            for _, r in pv_rows.iterrows():
                surf = safe_get(r, 'Surface totale de capteurs', 'NC')
                ori = safe_get(r, 'Orientation [°/Sud]', 'NC')
                etat = safe_get(r, "Etat de l'installation", 'NC')

                st.markdown(f"""
                <div class="alan-card">
                    <div class="t-label">Photovoltaïque</div>
                    <p>Surface : {surf} m²<br>Orientation : {ori}<br>État : {etat}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Pas de PV.")

        # 5. Thermique
        st.markdown("### ♨️ Solaire Thermique")
        th_rows = pd.DataFrame()
        if not df_th.empty and 'GROUPE HP2' in df_th.columns:
            th_rows = df_th[df_th['GROUPE HP2'] == sel_h]

        if not th_rows.empty:
            for _, r in th_rows.iterrows():
                surf = safe_get(r, 'Surface totale des capteurs (m2)', 'NC')
                etat = safe_get(r, 'Etat des lieux', 'NC')

                st.markdown(f"""
                <div class="alan-card">
                    <div class="t-label">Solaire Thermique</div>
                    <p>Surface : {surf} m²<br>État : {etat}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Pas de solaire thermique.")

except Exception as e:
    st.error(f"Une erreur inattendue est survenue : {e}")
