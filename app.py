import streamlit as st
import pandas as pd
import os

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

# 4. CHARGEMENT DES DONNÉES (MAPPING DES FICHIERS)
FILES_MAPPING = {
    "ug": "4 - UG SURFACES - NOVEMBRE 2024.xlsx - SURFACES DES UG.csv",
    "batiments": "3 - BATIMENTS_SURFACES_NOVEMBRE 2024.xlsx - SURFACES BATIMENTS.csv",
    "ind": "2-EQUIPEMENTS CHAUFFAGE INDIVIDUEL_NOVEMBRE 2024.xlsx - BDD CIgaz.csv",
    "coll": "1-EQUIPEMENTS CHAUFFAGE COLLECTIF_NOVEMBRE 2024.xlsx - COLLECTIF + TRAVAUX.csv",
    "pv": "5 - PANNEAUX SOLAIRES_NOVEMBRE 2024.xlsx - InfoPV.csv",
    "th": "5 - PANNEAUX SOLAIRES_NOVEMBRE 2024.xlsx - Thermique.csv"
}

def clean_columns(df):
    """Nettoie les noms de colonnes (espaces en trop)"""
    df.columns = df.columns.str.strip()
    return df

@st.cache_data
def load_data():
    data = {}
    
    # --- 1. UG Surfaces ---
    if os.path.exists(FILES_MAPPING["ug"]):
        df = pd.read_csv(FILES_MAPPING["ug"], dtype=str)
        df = clean_columns(df)
        df = df.rename(columns={"N° UG": "N°UG", "GROUPE (HP2)": "GROUPE HP2"})
        data["ug"] = df
    else:
        st.error(f"Fichier manquant : {FILES_MAPPING['ug']}")
        return None

    # --- 2. Batiments ---
    if os.path.exists(FILES_MAPPING["batiments"]):
        df_bat = pd.read_csv(FILES_MAPPING["batiments"], dtype=str)
        df_bat = clean_columns(df_bat)
        df_bat = df_bat.rename(columns={"GROUPE (HP2)": "GROUPE HP2", "BATIMENTS (HP3)": "BATIMENT"})
        data["batiments"] = df_bat
    
    # --- 3. Chauffage Individuel ---
    if os.path.exists(FILES_MAPPING["ind"]):
        df = pd.read_csv(FILES_MAPPING["ind"], dtype=str, header=2)
        df = clean_columns(df)
        df = df.rename(columns={"HP2": "GROUPE HP2"})
        data["ind"] = df
    else:
        data["ind"] = pd.DataFrame()

    # --- 4. Chauffage Collectif ---
    if os.path.exists(FILES_MAPPING["coll"]):
        df = pd.read_csv(FILES_MAPPING["coll"], dtype=str)
        df = clean_columns(df)
        # On mappe explicitement les colonnes importantes pour le système et l'énergie
        df = df.rename(columns={
            "HP2": "GROUPE HP2", 
            "Type combustible": "Energie",
            "Type d'équipement": "Systeme_Type"
        })
        data["coll"] = df
    else:
        data["coll"] = pd.DataFrame()

    # --- 5. PV ---
    if os.path.exists(FILES_MAPPING["pv"]):
        df = pd.read_csv(FILES_MAPPING["pv"], dtype=str)
        df = clean_columns(df)
        if "Code HP2" in df.columns:
            df = df.rename(columns={"Code HP2": "GROUPE HP2"})
        data["pv"] = df
    else:
        data["pv"] = pd.DataFrame()

    # --- 6. Thermique ---
    if os.path.exists(FILES_MAPPING["th"]):
        df = pd.read_csv(FILES_MAPPING["th"], dtype=str)
        df = clean_columns(df)
        if "Code HP2" in df.columns:
            df = df.rename(columns={"Code HP2": "GROUPE HP2"})
        data["th"] = df
    else:
        data["th"] = pd.DataFrame()
        
    return data

datasets = load_data()

if datasets and "ug" in datasets:
    df_ug = datasets["ug"]
    df_bat = datasets.get("batiments", pd.DataFrame())
    df_ind = datasets["ind"]
    df_coll = datasets["coll"]
    df_pv = datasets["pv"]
    df_th = datasets["th"]

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
                <div class="t-label">🏢 GROUPE (HP2)</div>
                <div class="t-val">{int(total_immeuble)} m²</div>
                <div class="t-sub">{nb_ug_addr} logements • {adresse_ug}</div>
            </div>
            """, unsafe_allow_html=True)

        # 7. CHAUFFAGE INDIVIDUEL
        st.markdown("### 🔥 Chauffage individuel")
        ind_rows = pd.DataFrame()
        if not df_ind.empty and 'GROUPE HP2' in df_ind.columns:
            ind_rows = df_ind[df_ind['GROUPE HP2'] == sel_h]
            
        if not ind_rows.empty:
            for _, r in ind_rows.iterrows():
                modele = r.get('Modèle', r.get('Modèles des chaudières', 'Non spécifié'))
                if pd.isna(modele): modele = "Modèle non détecté"
                
                st.markdown(f"""
                <div class="alan-card">
                    <div class="t-label">Chaudière Individuelle</div>
                    <div class="t-sub">{modele}</div>
                    <p>Année : {r.get('Années (chaudières & chauffe-bains)\nà titre indicatif', 'NC')}<br>
                    Nb équipements : {r.get("Nb d'équipements individuels gaz", 'NC')}<br>
                    Travaux : {r.get('Travaux réalisés', 'NC')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Pas de chauffage individuel gaz recensé pour ce groupe.")

        # 8. CHAUFFAGE COLLECTIF
        st.markdown("### 🏢 Chauffage collectif")
        coll_rows = pd.DataFrame()
        if not df_coll.empty and 'GROUPE HP2' in df_coll.columns:
            coll_rows = df_coll[df_coll['GROUPE HP2'] == sel_h]

        if not coll_rows.empty:
            for _, r in coll_rows.iterrows():
                # Récupération détaillée du système
                systeme = r.get('Systeme_Type', 'NC')
                marque = r.get('Marque', '')
                modele = r.get('Modèle', '')
                
                # Construction de la chaîne complète pour le système
                desc_systeme = f"{systeme}"
                if pd.notna(marque) and marque:
                    desc_systeme += f" - {marque}"
                if pd.notna(modele) and modele:
                    desc_systeme += f" ({modele})"
                
                energie = r.get('Energie', 'NC')

                st.markdown(f"""
                <div class="alan-card">
                    <div class="t-label">Chaufferie Collective</div>
                    <div class="t-sub">Système : {desc_systeme}</div>
                    <div class="t-val" style="font-size: 1.5rem !important;">Énergie : {energie}</div>
                    <p style="margin-top:10px;">Travaux : {r.get('Travaux réalisés', 'Aucun travaux récents')}<br>
                    Date : {r.get("Date d'achèvement travaux", '-')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Pas de chauffage collectif recensé pour ce HP2.")

        # 9. PV
        st.markdown("### ☀️ Panneaux solaires PV")
        pv_rows = pd.DataFrame()
        if not df_pv.empty and 'GROUPE HP2' in df_pv.columns:
            pv_rows = df_pv[df_pv['GROUPE HP2'] == sel_h]

        if not pv_rows.empty:
            for _, r in pv_rows.iterrows():
                st.markdown(f"""
                <div class="alan-card">
                    <div class="t-label">Photovoltaïque</div>
                    <p>Surface : {r.get('Surface totale de capteurs', 'NC')} m²<br>
                    Orientation : {r.get('Orientation [°/Sud]', 'NC')}<br>
                    État : {r.get("Etat de l'installation", 'NC')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Pas de PV.")

        # 10. THERMIQUE
        st.markdown("### ♨️ Solaire Thermique")
        th_rows = pd.DataFrame()
        if not df_th.empty and 'GROUPE HP2' in df_th.columns:
            th_rows = df_th[df_th['GROUPE HP2'] == sel_h]

        if not th_rows.empty:
            for _, r in th_rows.iterrows():
                st.markdown(f"""
                <div class="alan-card">
                    <div class="t-label">Solaire Thermique</div>
                    <p>Surface : {r.get('Surface totale des capteurs (m2)', 'NC')} m²<br>
                    État : {r.get('Etat des lieux', 'NC')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Pas de solaire thermique.")

except Exception as e:
    st.error(f"Une erreur est survenue : {e}")
