import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Socobat Asset", page_icon="🏢", layout="wide")

# --- Config des fichiers (modifier si besoin) ---
# Utiliser le répertoire du fichier source pour éviter les problèmes de working dir
DATA_DIR = Path(__file__).parent
FILES = {
    "ug": DATA_DIR / "4 - UG SURFACES - NOVEMBRE 2024.csv",
    "ind": DATA_DIR / "2-EQUIPEMENTS CHAUFFAGE INDIVIDUEL_NOVEMBRE 2024.csv",
    "coll": DATA_DIR / "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.csv",
    "pv": DATA_DIR / "5 - INFO PV.csv",
    "th": DATA_DIR / "6 - INFO THERMIQUE.csv",
}

# --- Utilitaires ---
def try_read_csv(path):
    """Tente différentes encodings et renvoie DataFrame ou None."""
    encodings = ["utf-8", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            return pd.read_csv(path, dtype=str, encoding=enc)
        except Exception:
            continue
    return None

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie et normalise les noms de colonnes pour éviter les KeyError."""
    df = df.copy()
    # strip, remplacer espaces insécables, remplacer � par °
    cleaned = (
        df.columns
        .astype(str)
        .str.strip()
        .str.replace("\xa0", " ", regex=False)
        .str.replace("�", "°", regex=False)
    )
    # enlever espaces doubles
    cleaned = cleaned.str.replace(r"\s+", " ", regex=True)
    df.columns = cleaned
    return df

@st.cache_data
def load_csv(path):
    if not Path(path).exists():
        return None
    df = try_read_csv(path)
    if df is None:
        return None
    return normalize_columns(df)

# --- Chargement des données ---
df_ug = load_csv(FILES["ug"])
df_ind = load_csv(FILES["ind"])
df_coll = load_csv(FILES["coll"])
df_pv = load_csv(FILES["pv"])
df_th = load_csv(FILES["th"])

# Vérification basique
missing = [name for name,df in (("UG",df_ug),("IND",df_ind),("COLL",df_coll),("PV",df_pv),("TH",df_th)) if df is None]
if missing:
    st.error(f"Fichiers manquants ou illisibles : {', '.join(missing)}. Vérifie les chemins et l'encodage.")
    st.stop()

# CSS basique pour les cartes
st.markdown(
    """
    <style>
    .alan-card{
      border:1px solid #e6e6e6;
      padding:12px;
      border-radius:8px;
      margin-bottom:10px;
      background:#fafafa;
    }
    .t-label{ font-weight:600; margin-bottom:6px; }
    .t-val{ font-size:1.1rem; margin-bottom:4px; }
    .t-sub{ color:#666; font-size:0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h2>🏢 Assistant DPE logement – Socobat Asset</h2>", unsafe_allow_html=True)

# --- Harmonisation N°UG ---
if "N° UG" in df_ug.columns and "N°UG" not in df_ug.columns:
    df_ug = df_ug.rename(columns={"N° UG": "N°UG"})

# Si d'autres colonnes doivent être standardisées, on peut ajouter ici
# Par exemple, s'assurer que les colonnes HP2 existent sous une forme commune
for df in (df_ind, df_coll):
    if "HP2" not in df.columns and "Code HP2" in df.columns:
        df.rename(columns={"Code HP2": "HP2"}, inplace=True)

# --- Sélection Groupe HP2 / UG ---
hp2_vals = sorted(df_ug["GROUPE HP2"].dropna().unique())
hp2_options = ["Choisir..."] + list(hp2_vals)
col1, col2 = st.columns(2)
with col1:
    sel_h = st.selectbox("Groupe HP2", hp2_options, index=0)
if sel_h == "Choisir...":
    sel_h = None

sel_u = None
if sel_h:
    ug_vals = sorted(df_ug[df_ug["GROUPE HP2"] == sel_h]["N°UG"].dropna().unique())
    ug_options = ["Choisir..."] + list(ug_vals)
    with col2:
        sel_u = st.selectbox("Unité UG", ug_options, index=0)
    if sel_u == "Choisir...":
        sel_u = None

# --- Affichage des données ---
if sel_h and sel_u:
    u_row = df_ug[(df_ug["GROUPE HP2"] == sel_h) & (df_ug["N°UG"] == sel_u)]
    if u_row.empty:
        st.warning("Aucune donnée UG trouvée.")
        st.stop()
    u_data = u_row.iloc[0]

    # Surfaces
    sh = u_data.get("SURFACE HABITABLE (SHA)", "NC")
    typ = u_data.get("Type", "NC")
    etage = u_data.get("Etage", "NC")
    st.markdown(f"""
    <div class="alan-card">
        <div class="t-label">🏠 LOGEMENT (UG)</div>
        <div class="t-val">{sh} m²</div>
        <div class="t-sub">Type {typ} • Étage {etage}</div>
    </div>
    """, unsafe_allow_html=True)

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
            st.markdown(f"""
            <div class="alan-card">
                <div class="t-label">Chaudière individuelle</div>
                <p>Modèle : {r.get("Modèles des chaudières", "NC")}<br>
                Type : {r.get("Type", "NC")}<br>
                Année : {r.get("Années (chaudières & chauffe-bains)", "NC")}<br>
                Nb équipements : {r.get("Nb d'équipements individuels gaz", "NC")}<br>
                Travaux : {travaux} – {date}</p>
            </div>
            """, unsafe_allow_html=True)

    # Chauffage collectif
    st.markdown("### 🏢 Chauffage collectif")
    coll_rows = df_coll[df_coll["HP2"] == sel_h] if "HP2" in df_coll.columns else df_coll.iloc[0:0]
    if coll_rows.empty:
        st.info("Pas de chauffage collectif.")
    else:
        for _, r in coll_rows.iterrows():
            travaux = r.get("Travaux réalisés", "NC")
            date = r.get("Date d'achèvement travaux", "NC")
            system = r.get("Système collectif", r.get("Type de système", "NC"))
            st.markdown(f"""
            <div class="alan-card">
                <div class="t-label">Chauffage collectif</div>
                <p>
                🏭 Système : {system}<br>
                🔥 Type chaudière : {r.get("Type de chaudière", "NC")}<br>
                ⚡ Énergie : {r.get("Type d'énergie", "NC")}<br>
                Nb équipements : {r.get("Nb d'équipements collectifs", "NC")}<br>
                Travaux : {travaux} – {date}
                </p>
            </div>
            """, unsafe_allow_html=True)

    # PV
    st.markdown("### ☀️ Panneaux solaires photovoltaïques")
    # Les fichiers PV/TH peuvent utiliser "Code HP2" au lieu de "HP2"
    pv_key = "Code HP2" if "Code HP2" in df_pv.columns and "HP2" not in df_pv.columns else "HP2"
    pv_rows = df_pv[df_pv[pv_key] == sel_h] if pv_key in df_pv.columns else df_pv.iloc[0:0]
    if pv_rows.empty:
        st.info("Pas de PV.")
    else:
        for _, r in pv_rows.iterrows():
            surface = r.get("Surface totale de capteurs", "NC")
            nb = r.get("Nb de capteurs", "NC")
            type_cap = r.get("Type de capteurs", "NC")
            incl = r.get("Inclinaison [°/hor]", r.get("Inclinaison [�/hor]", "NC"))
            orient = r.get("Orientation [°/Sud]", r.get("Orientation", "NC"))
            etat_pv = r.get("Etat de l'installation", "NC")
            st.markdown(f"""
            <div class="alan-card">
                <div class="t-label">PV – {r.get("Nom du groupe", "NC")}</div>
                <p>Surface : {surface} m²<br>
                Nb capteurs : {nb}<br>
                Type : {type_cap}<br>
                Inclinaison : {incl}<br>
                Orientation : {orient}<br>
                État : {etat_pv}</p>
            </div>
            """, unsafe_allow_html=True)

    # Thermique
    st.markdown("### ♨️ Panneaux solaires thermiques")
    th_key = "Code HP2" if "Code HP2" in df_th.columns and "HP2" not in df_th.columns else "HP2"
    th_rows = df_th[df_th[th_key] == sel_h] if th_key in df_th.columns else df_th.iloc[0:0]
    if th_rows.empty:
        st.info("Pas de solaire thermique.")
    else:
        for _, r in th_rows.iterrows():
            surface = r.get("Surface totale des capteurs (m2)", r.get("Surface totale des capteurs", "NC"))
            nb = r.get("Nb de capteurs", "NC")
            type_cap = r.get("Type de capteurs", "NC")
            incl = r.get("Inclinaison  [°/hor]", r.get("Inclinaison  [�/hor]", "NC"))
            orient = r.get("Orientation", "NC")
            etat_th = r.get("Etat des lieux", r.get("Etat", "NC"))
            st.markdown(f"""
            <div class="alan-card">
                <div class="t-label">Thermique – {r.get("Nom", "NC")}</div>
                <p>Surface : {surface} m²<br>
                Nb capteurs : {nb}<br>
                Type : {type_cap}<br>
                Inclinaison : {incl}<br>
                Orientation : {orient}<br>
                État : {etat_th}</p>
            </div>
            """, unsafe_allow_html=True)

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
