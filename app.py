import streamlit as st
import pandas as pd
from pathlib import Path
import traceback

st.set_page_config(page_title="Socobat Asset", page_icon="🏢", layout="wide")

# --- Utiliser le répertoire du script pour éviter les problèmes de working dir ---
DATA_DIR = Path(__file__).parent

# Mappage logiques -> mots-clés attendus dans le nom de fichier (insensible à la casse)
SEARCH_KEYWORDS = {
    "ug": ["ug", "surface"],            # ex: "4 - SURFACES UG - NOVEMBRE 2024.csv"
    "ind": ["individuel", "ind"],       # ex: "2-EQUIPEMENTS CHAUFFAGE INDIVIDUEL_NOVEMBRE 2024.csv"
    "coll": ["collectif", "collectif"], # ex: "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.csv"
    "pv": ["pv"],                       # ex: "5 - INFO PV.csv"
    "th": ["thermique", "th"],          # ex: "6 - INFO THERMIQUE.csv"
}

def find_file_for(key):
    """Recherche un fichier .csv dans DATA_DIR contenant tous les mots-clés du mapping."""
    keywords = SEARCH_KEYWORDS.get(key, [])
    candidates = list(DATA_DIR.glob("*.csv")) + list(DATA_DIR.glob("*.CSV"))
    for p in candidates:
        name = p.name.lower()
        if all(k.lower() in name for k in keywords):
            return p
    # fallback: try to match any keyword presence
    for p in candidates:
        name = p.name.lower()
        if any(k.lower() in name for k in keywords):
            return p
    return None

# --- Résolution automatique des fichiers ---
FILES = {k: find_file_for(k) for k in SEARCH_KEYWORDS.keys()}

st.markdown("<h2>🏢 Assistant DPE logement – Socobat Asset</h2>", unsafe_allow_html=True)
st.markdown("### 🔎 Diagnostic fichiers CSV (recherche automatique)")

st.write("DATA_DIR utilisé :", str(DATA_DIR.resolve()))
for k, p in FILES.items():
    st.write(f"- {k} -> {p.name if p else 'Non trouvé'} ({p if p else ''})")

# afficher un échantillon du dossier pour debugging
try:
    st.write("Contenu du dossier (quelques entrées):")
    for i, p in enumerate(sorted(DATA_DIR.iterdir())):
        st.write(f"{i+1}. {p.name}")
        if i >= 50:
            break
except Exception as e:
    st.write("Impossible de lister DATA_DIR:", e)
    st.write(traceback.format_exc())

# --- Utilitaires de lecture ---
def try_read_csv(path_or_buffer):
    """Tente différentes encodings et renvoie DataFrame ou None."""
    encodings = ["utf-8", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            return pd.read_csv(path_or_buffer, dtype=str, encoding=enc)
        except Exception:
            continue
    return None

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie et normalise les noms de colonnes pour éviter les KeyError."""
    df = df.copy()
    cleaned = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace("\xa0", " ", regex=False)
        .str.replace("�", "°", regex=False)
    )
    cleaned = cleaned.str.replace(r"\s+", " ", regex=True)
    df.columns = cleaned
    return df

@st.cache_data
def load_csv(path_or_buffer):
    if path_or_buffer is None:
        return None
    try:
        df = try_read_csv(path_or_buffer)
        if df is None:
            return None
        return normalize_columns(df)
    except Exception:
        return None

# --- Chargement des données (si utilisateur veut override via upload) ---
uploaded = {}
for k in SEARCH_KEYWORDS.keys():
    if FILES.get(k) is None:
        up = st.file_uploader(f"Uploader le fichier pour {k} (optionnel)", type=["csv"], key=f"up_{k}")
        if up is not None:
            uploaded[k] = up

def source_for(k):
    return uploaded.get(k, FILES.get(k))

df_ug = load_csv(source_for("ug"))
df_ind = load_csv(source_for("ind"))
df_coll = load_csv(source_for("coll"))
df_pv = load_csv(source_for("pv"))
df_th = load_csv(source_for("th"))

# Fix syntax: build sequence of tuples for comprehension
missing = [name for name, df in ("UG", df_ug), ("IND", df_ind), ("COLL", df_coll), ("PV", df_pv), ("TH", df_th) if df is None]
if missing:
    st.error(f"Fichiers manquants ou illisibles : {', '.join(missing)}. Vérifie les noms ou upload via l'UI ci‑dessus.")
    st.info("Conseils rapides :\n- Vérifie que les CSV sont bien au même emplacement que app.py.\n- Vérifie la casse et les espaces spéciaux dans les noms de fichiers.\n- Si les fichiers existent mais ne sont pas détectés, renomme-les pour inclure des mots-clés comme 'UG', 'SURFACE', 'INDIVIDUEL', 'COLLECTIF', 'PV', 'THERMIQUE'.")
    st.stop()

# --- Harmonisation N°UG et colonnes HP2 ---
if "N° UG" in df_ug.columns and "N°UG" not in df_ug.columns:
    df_ug = df_ug.rename(columns={"N° UG": "N°UG"})
for df in (df_ind, df_coll):
    if "HP2" not in df.columns and "Code HP2" in df.columns:
        df.rename(columns={"Code HP2": "HP2"}, inplace=True)

# --- Sélection Groupe HP2 / UG ---
hp2_vals = sorted(df_ug["GROUPE HP2"].dropna().unique()) if "GROUPE HP2" in df_ug.columns else []
hp2_options = ["Choisir..."] + list(hp2_vals)
col1, col2 = st.columns(2)
with col1:
    sel_h = st.selectbox("Groupe HP2", hp2_options, index=0)
if sel_h == "Choisir...":
    sel_h = None

sel_u = None
if sel_h:
    if "N°UG" in df_ug.columns:
        ug_vals = sorted(df_ug[df_ug["GROUPE HP2"] == sel_h]["N°UG"].dropna().unique())
    else:
        ug_vals = sorted(df_ug[df_ug["GROUPE HP2"] == sel_h]["N° UG"].dropna().unique()) if "N° UG" in df_ug.columns else []
    ug_options = ["Choisir..."] + list(ug_vals)
    with col2:
        sel_u = st.selectbox("Unité UG", ug_options, index=0)
    if sel_u == "Choisir...":
        sel_u = None

# --- Affichage (inchangé, mais avec checks supplémentaires) ---
if sel_h and sel_u:
    u_row = df_ug[(df_ug["GROUPE HP2"] == sel_h) & ((df_ug.get("N°UG") == sel_u) | (df_ug.get("N° UG") == sel_u))]
    if u_row.empty:
        st.warning("Aucune donnée UG trouvée.")
        st.stop()
    u_data = u_row.iloc[0]

    sh = u_data.get("SURFACE HABITABLE (SHA)", "NC")
    typ = u_data.get("Type", "NC")
    etage = u_data.get("Etage", "NC")
st.markdown(f"\n    <div class=\"alan-card\">\n        <div class=\"t-label\">🏠 LOGEMENT (UG)</div>\n        <div class=\"t-val\">{sh} m²</div>\n        <div class=\"t-sub\">Type {typ} • Étage {etage}</div>\n    </div>\n    ", unsafe_allow_html=True)

    # Chauffage individuel
    st.markdown("### 🔥 Chauffage individuel")
    ind_rows = df_ind[df_ind["HP2"] == sel_h] if "HP2" in df_ind.columns else df_ind.iloc[0:0]
    if "N°UG" in ind_rows.columns:
        ind_rows = ind_rows[ind_rows["N°UG"] == sel_u]
    if ind_rows.empty:
        st.info("Pas de chauffage individuel.")
    else:
        for _, r in ind_rows.iterrows():
            travaux = r.get("Travaux réalisés", "NC")
            date = r.get("Date d'achèvement travaux", "NC")
            st.markdown(f"\n            <div class=\"alan-card\">\n                <div class=\"t-label\">Chaudière individuelle</div>\n                <p>Modèle : {r.get("Modèles des chaudières", "NC")}<br>\n                Type : {r.get("Type", "NC")}<br>\n                Année : {r.get("Années (chaudières & chauffe-bains)", "NC")}<br>\n                Nb équipements : {r.get("Nb d'équipements individuels gaz", "NC")}<br>\n                Travaux : {travaux} – {date}</p>\n            </div>\n            ", unsafe_allow_html=True)

    # Chauffage collectif
    st.markdown("### 🏢 Chauffage collectif")
    coll_rows = df_coll[df_coll["HP2"] == sel_h] if "HP2" in df_coll.columns else df_coll.iloc[0:0]
    if coll_rows.empty:
        st.info("Pas de chauffage collectif.")
    else:
        for _, r in coll_rows.iterrows():
            travaux = r.get("Travaux réalisés", "NC")
            date = r.get("Date d'achèvement travaux", "NC")
            system = r.get("Système collectif", r.get("Type de système", "NC")
            st.markdown(f"\n            <div class=\"alan-card\">\n                <div class=\"t-label\">Chauffage collectif</div>\n                <p>\n                🏭 Système : {system}<br>\n                🔥 Type chaudière : {r.get("Type de chaudière", "NC")}<br>\n                ⚡ Énergie : {r.get("Type d'énergie", "NC")}<br>\n                Nb équipements : {r.get("Nb d'équipements collectifs", "NC")}<br>\n                Travaux : {travaux} – {date}\n                </p>\n            </div>\n            ", unsafe_allow_html=True)

    # PV
    st.markdown("### ☀️ Panneaux solaires photovoltaïques")
    pv_key = "Code HP2" if "Code HP2" in df_pv.columns and "HP2" not in df_pv.columns else "HP2"
    pv_rows = df_pv[df_pv[pv_key] == sel_h] if pv_key in df_pv.columns else df_pv.iloc[0:0]
    if pv_rows.empty:
        st.info("Pas de PV.")
    else:
        for _, r in pv_rows.iterrows():
            surface = r.get("Surface totale de capteurs", "NC")
            nb = r.get("Nb de capteurs", "NC")
            type_cap = r.get("Type de capteurs", "NC")
            incl = r.get("Inclinaison [°/hor]", r.get("Inclinaison [°/hor]", r.get("Inclinaison [�/hor]", "NC")))
            orient = r.get("Orientation [°/Sud]", r.get("Orientation", "NC")")
            etat_pv = r.get("Etat de l'installation", "NC")
            st.markdown(f"\n            <div class=\"alan-card\">\n                <div class=\"t-label\">PV – {r.get("Nom du groupe", "NC")}</div>\n                <p>Surface : {surface} m²<br>\n                Nb capteurs : {nb}<br>\n                Type : {type_cap}<br>\n                Inclinaison : {incl}<br>\n                Orientation : {orient}<br>\n                État : {etat_pv}</p>\n            </div>\n            ", unsafe_allow_html=True)

    # Thermique
    st.markdown("### ♨️ Panneaux solaires thermiques")
    th_key = "Code HP2" if "Code HP2" in df_th.columns and "HP2" not in df_th.columns else "HP2"
    th_rows = df_th[df_th[th_key] == sel_h] if th_key in df_th.columns else df_th.iloc[0:0]
    if th_rows.empty:
        st.info("Pas de solaire thermique.")
    else:
        for _, r in th_rows.iterrows():
            surface = r.get("Surface totale des capteurs (m2)", r.get("Surface totale des capteurs", "NC")
            nb = r.get("Nb de capteurs", "NC")
            type_cap = r.get("Type de capteurs", "NC")
            incl = r.get("Inclinaison  [°/hor]", r.get("Inclinaison  [�/hor]", "NC")
            orient = r.get("Orientation", "NC")
            etat_th = r.get("Etat des lieux", r.get("Etat", "NC")
            st.markdown(f"\n            <div class=\"alan-card\">\n                <div class=\"t-label\">Thermique – {r.get("Nom", "NC")}</div>\n                <p>Surface : {surface} m²<br>\n                Nb capteurs : {nb}<br>\n                Type : {type_cap}<br>\n                Inclinaison : {incl}<br>\n                Orientation : {orient}<br>\n                État : {etat_th}</p>\n            </div>\n            ", unsafe_allow_html=True)

    # Résumé des travaux
    st.markdown("### 🛠️ Résumé des travaux")
    resume = []
    for _, r in ind_rows.iterrows():
        travaux = r.get("Travaux réalisés", "NC")
        date = r.get("Date d'achèvement travaux", "NC")
        resume.append(f"Individuel : {travaux} ({date})")
    for _, r in coll_rows.iterrows():
        travaux = r.get("Travaux réalisés", "NC")
        date = r.get("Date d'achèvement travaux", "NC")
        resume.append(f"Collectif : {travaux} ({date})")
    for _, r in pv_rows.iterrows():
        etat_pv = r.get("Etat de l'installation", "NC")
        resume.append(f"PV : {etat_pv}")
    for _, r in th_rows.iterrows():
        etat_th = r.get("Etat des lieux", "NC")
        resume.append(f"Thermique : {etat_th}")

    if resume:
        st.markdown("<div class='alan-card'><div class='t-label'>Résumé des travaux</div>", unsafe_allow_html=True)
        for line in resume:
            st.markdown(f"- {line}")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Aucun travail recensé")