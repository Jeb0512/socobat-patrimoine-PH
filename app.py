import streamlit as st
import pandas as pd
import os

# --- CONSTANTES DE COLONNES ---
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
    layout="wide",  # large sur desktop, mais reste utilisable sur mobile [web:19]
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
        padding: 16px !important;
        border-radius: 16px !important;
        border: 1px solid #E5E7EB !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 12px !important;
        color: #111827 !important;
    }
    .t-label {
        color: #6B7280 !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .t-val {
        color: #111827 !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        letter-spacing: -1.5px;
        line-height: 1;
    }
    .t-sub {
        color: #6366F1 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        margin-top: 6px;
    }
    h1, h2, h3, p, label {
        color: #111827 !important;
        font-weight: 600 !important;
    }
    .stButton>button {
        background-color: #6366f1 !important;
        color: white !important;
        border-radius: 999px !important;
        font-weight: 700 !important;
        border: none !important;
        width: 100%;
        height: 45px;
    }
    @media (max-width: 768px) {
        .t-val {
            font-size: 1.7rem !important;
        }
        .alan-card {
            padding: 12px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# 3. ACCÈS SÉCURISÉ
if "auth" not in st.session_state:
    st.markdown("<div style='text-align:center; padding-top:40px;'>", unsafe_allow_html=True)
    st.markdown("<h1>🏢 Socobat Asset</h1><p style='color:#6B7280;'>By Jeb 😉</p>", unsafe_allow_html=True)

    # Sur mobile, une seule colonne pleine largeur reste lisible. [web:11][web:18]
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
# __file__ peut ne pas exister en mode interactif, on sécurise. [web:7]
try:
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    CURRENT_DIR = os.getcwd()

FILES_MAPPING = {
    "ug": "4 - UG SURFACES - NOVEMBRE 2024.xlsx - SURFACES DES UG.csv",
    "batiments": "3 - BATIMENTS_SURFACES_NOVEMBRE 2024.xlsx - SURFACES BATIMENTS.csv",
    "ind": "2-EQUIPEMENTS CHAUFFAGE INDIVIDUEL_NOVEMBRE 2024.xlsx - BDD CIgaz.csv",
    "coll": "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx - COLLECTIF + TRAVAUX.csv",
    "pv": "5 - PANNEAUX SOLAIRES_NOVEMBRE 2024.xlsx - InfoPV.csv",
    "th": "5 - PANNEAUX SOLAIRES_NOVEMBRE 2024.xlsx - Thermique.csv"
}

def get_path(filename: str) -> str:
    return os.path.join(CURRENT_DIR, filename)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoyage agressif des espaces et normalisation basique."""
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()
    return df

def safe_get(row: pd.Series, key: str, default: str = '') -> str:
    """Accès sécurisé à une valeur de ligne, en renvoyant une chaîne propre."""
    if key not in row.index:
        return default or ""
    val = row[key]
    if pd.isna(val) or str(val).lower() in ['nan', 'none', '', 'nat']:
        return default or ""
    return str(val)

@st.cache_data(show_spinner="Chargement des données...")
def load_data():
    data = {}
    missing_files = []

    # 1. UG
    path_ug = get_path(FILES_MAPPING["ug"])
    if os.path.exists(path_ug):
        df = pd.read_csv(path_ug, dtype=str)
        df = clean_data(df)
        df = df.rename(columns={
            "N° UG": "N°UG",
            "N°UG ": "N°UG",
            "GROUPE (HP2)": "GROUPE HP2",
            "GROUPE HP2 ": "GROUPE HP2"
        })
        data["ug"] = df
    else:
        missing_files.append(FILES_MAPPING["ug"])

    # 2. Bâtiments
    path_bat = get_path(FILES_MAPPING["batiments"])
    if os.path.exists(path_bat):
        df = pd.read_csv(path_bat, dtype=str)
        df = clean_data(df)
        df = df.rename(columns={
            "GROUPE (HP2)": "GROUPE HP2",
            "GROUPE HP2 ": "GROUPE HP2"
        })
        data["batiments"] = df
    else:
        data["batiments"] = pd.DataFrame()
        missing_files.append(FILES_MAPPING["batiments"])

    # 3. Individuel
    path_ind = get_path(FILES_MAPPING["ind"])
    if os.path.exists(path_ind):
        # header=2 car deux lignes d'entête dans l’export ; à ajuster si ton modèle change. [web:6][web:9]
        df = pd.read_csv(path_ind, dtype=str, header=2)
        df = clean_data(df)
        df = df.rename(columns={"HP2": "GROUPE HP2", "HP2 ": "GROUPE HP2"})
        data["ind"] = df
    else:
        data["ind"] = pd.DataFrame()
        missing_files.append(FILES_MAPPING["ind"])

    # 4. Collectif
    path_coll = get_path(FILES_MAPPING["coll"])
    if os.path.exists(path_coll):
        df = pd.read_csv(path_coll, dtype=str)
        df = clean_data(df)
        df = df.rename(columns={
            "HP2": "GROUPE HP2",
            "HP2 ": "GROUPE HP2",
            "Type combustible": "Energie",
            "Type d'équipement": COL_SYSTEME_COLL
        })
        data["coll"] = df
    else:
        data["coll"] = pd.DataFrame()
        missing_files.append(FILES_MAPPING["coll"])

    # 5. PV
    path_pv =
