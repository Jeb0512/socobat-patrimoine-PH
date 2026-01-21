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
    </style>
""", unsafe_allow_html=True)

# 3. CHARGEMENT DES DONNÉES
@st.cache_data
def load_csv(path):
    return pd.read_csv(path, dtype=str)

df_ug = load_csv("ug_surfaces.csv")
df_ind = load_csv("chauffage_individuel.csv")
df_coll = load_csv("chauffage_collectif.csv")
df_pv = load_csv("pv.csv")
df_th = load_csv("thermique.csv")

# Harmonisation colonnes
if "N° UG" in df_ug.columns and "N°UG" not in df_ug.columns:
    df_ug = df_ug.rename(columns={"N° UG": "N°UG"})

# 4. TITRE
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

# 6. AFFICHAGE DES DONNÉES
if sel_h and sel_u:

    u_row = df_ug[(df_ug['GROUPE HP2'] == sel_h) & (df_ug['N°UG'] == sel_u)]
    if u_row.empty:
        st.warning("Aucune donnée UG trouvée pour cette combinaison.")
        st.stop()

    u_data = u_row.iloc[0]

    # SHA numérique
    df_ug["SHA_NUM"] = pd.to_numeric(df_ug.get("SURFACE HABITABLE (SHA)", pd.Series([None]*len(df_ug))), errors="coerce")
    total_immeuble = df_ug[df_ug["GROUPE HP2"] == sel_h]["SHA_NUM"].sum()

    adresse_col = "Adresse" if "Adresse" in df_ug.columns else None
    if adresse_col:
        adresse_ug = u_data[adresse_col]
        mask_same_addr = (df_ug["GROUPE HP2"] == sel_h) & (df_ug[adresse_col] == adresse_ug)
        total_addr = df_ug[mask_same_addr]["SHA_NUM"].sum()
        nb_ug_addr = mask_same_addr.sum()
    else:
        adresse_ug = "Adresse non disponible"
        total_addr = None
        nb_ug_addr = None

    # --- SURFACES ---
    st.markdown("""
    <div class="alan-card">
        <div class="t-label">🏠 LOGEMENT (UG)</div>
        <div class="t-val">{sha} m²</div>
        <div class="t-sub">Type {typ} • Étage {etg}</div>
    </div>
    """.format(
        sha=u_data.get("SURFACE HABITABLE (SHA)", "NC"),
        typ=u_data.get("Type", "NC"),
        etg=u_data.get("Etage", "NC")
    ), unsafe_allow_html=True)

    st.markdown("""
    <div class="alan-card">
        <div class="t-label">🏢 IMMEUBLE (HP2)</div>
        <div class="t-val">{tot} m²</div>
        <div class="t-sub">{nb} logements</div>
    </div>
    """.format(
        tot=int(total_immeuble) if pd.notna(total_immeuble) else "NC",
        nb=len(df_ug[df_ug["GROUPE HP2"] == sel_h])
    ), unsafe_allow_html=True)

    if adresse_col:
        st.markdown("""
        <div class="alan-card">
            <div class="t-label">📏 SOMME DES SURFACES PAR ADRESSE</div>
            <div class="t-val">{tot} m²</div>
            <div class="t-sub">{nb} UG • {addr}</div>
        </div>
        """.format(
            tot=int(total_addr) if pd.notna(total_addr) else "NC",
            nb=nb_ug_addr,
            addr=adresse_ug
        ), unsafe_allow_html=True)

    # --- CHAUFFAGE INDIVIDUEL ---
    st.markdown("### 🔥 Chauffage individuel")
    ind_rows = df_ind[df_ind["GROUPE HP2"] == sel_h]
    if "N°UG" in ind_rows.columns:
        ind_rows = ind_rows[ind_rows["N°UG"] == sel_u]

    if ind_rows.empty:
        st.info("Pas de chauffage individuel pour cette UG.")
    else:
        for _, r in ind_rows.iterrows():
            st.markdown("""
            <div class="alan-card">
                <div class="t-label">Chaudière individuelle</div>
                <p>Modèle : {mod}<br>
                Type : {typ}<br>
                Année : {an}<br>
                Nb équipements : {nb}<br>
                Travaux : {trav} – {date}</p>
            </div>
            """.format(
                mod=r.get("Modèle", r.get("Modèles des chaudières", "NC")),
                typ=r.get("Type", "NC"),
                an=r.get("Années (chaudières & chauffe-bains)", "NC"),
                nb=r.get("Nb d'équipements individuels gaz", "NC"),
                trav=r.get("Travaux réalisés", "NC"),
                date=r.get("Date d'achèvement travaux", "NC")
            ), unsafe_allow_html=True)

    # --- CHAUFFAGE COLLECTIF ---
    st.markdown("### 🏢 Chauffage collectif")
    coll_rows = df_coll[df_coll["GROUPE HP2"] == sel_h]

    if coll_rows.empty:
        st.info("Pas de chauffage collectif pour ce HP2.")
    else:
        for _, r in coll_rows.iterrows():
            st.markdown("""
            <div class="alan-card">
                <div class="t-label">Chauffage collectif</div>
                <p>
                🏭 Système : {sys}<br>
                🔥 Type chaudière : {typ}<br>
                ⚡ Énergie : {ene}<br>
                Nb équipements : {nb}<br>
                Travaux : {trav} – {date}
                </p>
            </div>
            """.format(
                sys=r.get("Système collectif", r.get("Type de système", "NC")),
                typ=r.get("Type de chaudière", "NC"),
                ene=r.get("Type d'énergie", "NC"),
                nb=r.get("Nb d'équipements collectifs", "NC"),
                trav=r.get("Travaux réalisés", "NC"),
                date=r.get("Date d'achèvement travaux", "NC")
            ), unsafe_allow_html=True)

    # --- PV ---
    st.markdown("### ☀️ Panneaux solaires photovoltaïques")
    pv_rows = df_pv[df_pv["Code HP2"] == sel_h]
    if pv_rows.empty:
        st.info("Pas de PV pour ce HP2.")
    else:
        for _, r in pv_rows.iterrows
