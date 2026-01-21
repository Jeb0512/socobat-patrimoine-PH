import streamlit as st
import pandas as pd

st.set_page_config(page_title="Socobat Asset", page_icon="🏢", layout="wide")

# Chargement des CSV
@st.cache_data
def load_csv(path):
    return pd.read_csv(path, dtype=str)

df_ug = load_csv("4 - UG SURFACES - NOVEMBRE 2024.csv")
df_ind = load_csv("2-EQUIPEMENTS CHAUFFAGE INDIVIDUEL_NOVEMBRE 2024.csv")
df_coll = load_csv("1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.csv")
df_pv = load_csv("5 - INFO PV.csv")
df_th = load_csv("6 - INFO THERMIQUE.csv")

# Harmonisation colonnes UG
if "N° UG" in df_ug.columns and "N°UG" not in df_ug.columns:
    df_ug = df_ug.rename(columns={"N° UG": "N°UG"})

st.markdown("<h2>🏢 Assistant DPE logement – Socobat Asset</h2>", unsafe_allow_html=True)

# Sélection HP2 / UG
hp2_list = sorted(df_ug['GROUPE HP2'].dropna().unique())
col1, col2 = st.columns(2)
with col1:
    sel_h = st.selectbox("Groupe HP2", hp2_list, index=None, placeholder="Choisir...")
sel_u = None
if sel_h:
    ug_list = sorted(df_ug[df_ug['GROUPE HP2'] == sel_h]['N°UG'].dropna().unique())
    with col2:
        sel_u = st.selectbox("Unité UG", ug_list, index=None, placeholder="Choisir...")

# Affichage des données
if sel_h and sel_u:
    u_row = df_ug[(df_ug['GROUPE HP2'] == sel_h) & (df_ug['N°UG'] == sel_u)]
    if u_row.empty:
        st.warning("Aucune donnée UG trouvée.")
        st.stop()
    u_data = u_row.iloc[0]

    # Surfaces
    st.markdown(f"""
    <div class="alan-card">
        <div class="t-label">🏠 LOGEMENT (UG)</div>
        <div class="t-val">{u_data.get("SURFACE HABITABLE (SHA)", "NC")} m²</div>
        <div class="t-sub">Type {u_data.get("Type", "NC")} • Étage {u_data.get("Etage", "NC")}</div>
    </div>
    """, unsafe_allow_html=True)

    # Chauffage individuel
    st.markdown("### 🔥 Chauffage individuel")
    ind_rows = df_ind[df_ind["HP2"] == sel_h]
    if "N°UG" in ind_rows.columns:
        ind_rows = ind_rows[ind_rows["N°UG"] == sel_u]
    if ind_rows.empty:
        st.info("Pas de chauffage individuel.")
    else:
        for _, r in ind_rows.iterrows():
            st.markdown(f"""
            <div class="alan-card">
                <div class="t-label">Chaudière individuelle</div>
                <p>Modèle : {r.get("Modèles des chaudières", "NC")}<br>
                Type : {r.get("Type", "NC")}<br>
                Année : {r.get("Années (chaudières & chauffe-bains)", "NC")}<br>
                Nb équipements : {r.get("Nb d'équipements individuels gaz", "NC")}<br>
                Travaux : {r.get("Travaux réalisés", "NC")} – {r.get("Date d'achèvement travaux", "NC")}</p>
            </div>
            """, unsafe_allow_html=True)

    # Chauffage collectif
    st.markdown("### 🏢 Chauffage collectif")
    coll_rows = df_coll[df_coll["HP2"] == sel_h]
    if coll_rows.empty:
        st.info("Pas de chauffage collectif.")
    else:
        for _, r in coll_rows.iterrows():
            st.markdown(f"""
            <div class="alan-card">
                <div class="t-label">Chauffage collectif</div>
                <p>
                🏭 Système : {r.get("Système collectif", r.get("Type de système", "NC"))}<br>
                🔥 Type chaudière : {r.get("Type de chaudière", "NC")}<br>
                ⚡ Énergie : {r.get("Type d'énergie", "NC")}<br>
                Nb équipements : {r.get("Nb d'équipements collectifs", "NC")}<br>
                Travaux : {r.get("Travaux réalisés", "NC")} – {r.get("Date d'achèvement travaux", "NC")}
                </p>
            </div>
            """, unsafe_allow_html=True)

    # PV
    st.markdown("### ☀️ Panneaux solaires photovoltaïques")
    pv_rows = df_pv[df_pv["Code HP2"] == sel_h]
    if pv_rows.empty:
        st.info("Pas de PV.")
    else:
        for _, r in pv_rows.iterrows():
            st.markdown(f"""
            <div class="alan-card">
                <div class="t-label">PV – {r.get("Nom du groupe", "NC")}</div>
                <p>Surface : {r.get("Surface totale de capteurs", "NC")} m²<br>
                Nb capteurs : {r.get("Nb de capteurs", "NC")}<br>
                Type : {r.get("Type de capteurs", "NC")}<br>
                Inclinaison : {r.get("Inclinaison [�/hor]", "NC")}<br>
                Orientation : {r.get("Orientation [�/Sud]", "NC")}<br>
                État : {r.get("Etat de l'installation", "NC")}</p>
            </div>
            """, unsafe_allow_html=True)

    # Thermique
    st.markdown("### ♨️ Panneaux solaires thermiques")
    th_rows = df_th[df_th["Code HP2"] == sel_h]
    if th_rows.empty:
        st.info("Pas de solaire thermique.")
    else:
        for _, r in th_rows.iterrows():
            st.markdown(f"""
            <div class="alan-card">
                <div class="t-label">Thermique – {r.get("Nom", "NC")}</div>
                <p>Surface : {r.get("Surface totale des capteurs (m2)", "NC")} m²<br>
                Nb capteurs : {r.get("Nb de capteurs", "NC")}<br>
                Type : {r.get("Type de capteurs", "NC")}<br>
                Inclinaison : {r.get("Inclinaison  [�/hor]", "NC")}<br>
                Orientation : {r.get("Orientation", "NC")}<br>
                État : {r.get("Etat des lieux", "NC")}</p>
            </div>
            """, unsafe_allow_html=True)

    # Résumé des travaux
    st.markdown("### 🛠️ Résumé des travaux")
    resume = []
    for _, r in ind_rows.iterrows():
        resume.append(f"Individuel : {r.get('Travaux réalisés', 'NC')} ({r.get('Date d\'achèvement travaux', 'NC')})")
    for _, r in coll_rows.iterrows():
        resume.append(f"Collectif : {r.get('Travaux réalisés', 'NC')} ({r.get('Date d\'achèvement travaux', 'NC')})")
    for _, r in pv_rows.iterrows():
        resume.append(f"PV : {r.get('Etat de l\'installation', 'NC')}")
    for _, r in th_rows.iterrows():
        resume.append(f"Thermique : {r.get('Etat des lieux', 'NC')}")

    if resume:
        st.markdown("<div class='alan-card'><div class='t-label'>Résumé des travaux</div>", unsafe_allow_html=True)
        for line in resume:
            st.markdown(f"- {line}")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Aucun travail recensé pour ce HP2 / UG.")
