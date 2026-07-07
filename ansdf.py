# ===============================
# APPLICATION - PLATEFORME SRSD FATICK
# ===============================

import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os
from datetime import datetime
from sqlalchemy import create_engine, text

# -------------------------------
# CONFIGURATION
# -------------------------------
st.set_page_config(
    page_title="Plateforme SRSD FATICK",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# STYLE
# -------------------------------
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .main-title {
        background: linear-gradient(135deg, #003366 0%, #0055a4 100%);
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .main-title h1 { color: white; font-size: 1.8rem; margin: 0; }
    .main-title p { color: #e0e0e0; margin: 0; font-size: 0.9rem; }
    h1, h2, h3 { color: #003366; font-weight: bold; }
    .hero-container {
        background: linear-gradient(135deg, #003366 0%, #006699 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .hero-title { font-size: 2.5rem; font-weight: bold; color: white; margin-bottom: 0.5rem; }
    .hero-subtitle { font-size: 1.2rem; color: #f0f0f0; }
    .hero-description { font-size: 1rem; color: #e0e0e0; margin-top: 1rem; }
    .sector-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        transition: transform 0.3s;
    }
    .sector-card:hover { transform: translateY(-5px); }
    .sector-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .sector-title { font-weight: bold; color: white; font-size: 0.9rem; }
    .info-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        text-align: center;
        transition: all 0.3s;
    }
    .info-card:hover { box-shadow: 0 4px 8px rgba(0,0,0,0.2); transform: translateY(-3px); }
    .info-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
    .info-title { font-size: 1.1rem; font-weight: bold; color: #003366; margin-bottom: 0.5rem; }
    .info-text { color: #666; font-size: 0.85rem; }
    .department-badge {
        background-color: #e8f4f8;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        color: #003366;
        margin: 0.5rem 0;
    }
    footer { text-align: center; padding: 2rem; color: #666; margin-top: 3rem; border-top: 1px solid #ddd; }
    .success-message { background-color: #d4edda; color: #155724; padding: 1rem; border-radius: 10px; margin: 1rem 0; }
    .warning-message { background-color: #fff3cd; color: #856404; padding: 1rem; border-radius: 10px; margin: 1rem 0; }
    .stButton button { width: 100%; }
    .form-section { 
        background-color: white; 
        padding: 1rem; 
        border-radius: 10px; 
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    hr { margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# TITRE PRINCIPAL (NOUVEAU)
# -------------------------------
def show_main_title():
    st.markdown("""
    <div class="main-title">
        <h1>📊 Plateforme de Système d'information SRSD FATICK</h1>
        <p>Service Régional de la Statistique et de la Démographie - Région de Fatick</p>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# BASE DE DONNÉES SQLITE LOCALE (NINEA)
# -------------------------------
DB_PATH = 'collecte_ninea.db'
DB_TRAVAIL_PATH = 'collecte_travail.db'

def init_ninea_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collecte_ninea (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_complet TEXT NOT NULL,
            cni TEXT NOT NULL UNIQUE,
            sexe TEXT NOT NULL,
            activite_principale TEXT NOT NULL,
            regime TEXT NOT NULL,
            forme_juridique TEXT NOT NULL,
            date_depot TEXT NOT NULL,
            commune TEXT NOT NULL,
            departement TEXT NOT NULL,
            secteur TEXT DEFAULT 'NINEA (Entreprises)',
            synchro INTEGER DEFAULT 0
        )
    ''')
    cursor.execute("PRAGMA table_info(collecte_ninea)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'secteur' not in columns:
        cursor.execute("ALTER TABLE collecte_ninea ADD COLUMN secteur TEXT DEFAULT 'NINEA (Entreprises)'")
    if 'synchro' not in columns:
        cursor.execute("ALTER TABLE collecte_ninea ADD COLUMN synchro INTEGER DEFAULT 0")
    conn.commit()
    conn.close()

def init_travail_db():
    """Table pour le secteur Travail (structure simplifiée)"""
    conn = sqlite3.connect(DB_TRAVAIL_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collecte_travail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            annee INTEGER NOT NULL,
            departement TEXT NOT NULL,
            -- Demandeurs d'emploi
            manoeuvres_hommes INTEGER DEFAULT 0,
            manoeuvres_femmes INTEGER DEFAULT 0,
            employes_hommes INTEGER DEFAULT 0,
            employes_femmes INTEGER DEFAULT 0,
            -- Établissements
            etablissements_ouverts INTEGER DEFAULT 0,
            etablissements_fermes INTEGER DEFAULT 0,
            -- Statut juridique
            ei INTEGER DEFAULT 0,
            sa INTEGER DEFAULT 0,
            sarl INTEGER DEFAULT 0,
            suarl INTEGER DEFAULT 0,
            gie INTEGER DEFAULT 0,
            ong INTEGER DEFAULT 0,
            autres_statuts INTEGER DEFAULT 0,
            -- Emplois
            emplois_generes INTEGER DEFAULT 0,
            emplois_perdus INTEGER DEFAULT 0,
            -- Contrats
            cdi_hommes INTEGER DEFAULT 0,
            cdi_femmes INTEGER DEFAULT 0,
            cdd_hommes INTEGER DEFAULT 0,
            cdd_femmes INTEGER DEFAULT 0,
            saisonnier_hommes INTEGER DEFAULT 0,
            saisonnier_femmes INTEGER DEFAULT 0,
            apprentissage_hommes INTEGER DEFAULT 0,
            apprentissage_femmes INTEGER DEFAULT 0,
            temporaire_hommes INTEGER DEFAULT 0,
            temporaire_femmes INTEGER DEFAULT 0,
            stage_hommes INTEGER DEFAULT 0,
            stage_femmes INTEGER DEFAULT 0,
            -- Conflits
            conflit_indiv_conciliation INTEGER DEFAULT 0,
            conflit_indiv_partielle INTEGER DEFAULT 0,
            conflit_indiv_non INTEGER DEFAULT 0,
            conflit_collectif_conciliation INTEGER DEFAULT 0,
            conflit_collectif_partielle INTEGER DEFAULT 0,
            conflit_collectif_non INTEGER DEFAULT 0,
            -- Métadonnées
            date_saisie TEXT DEFAULT CURRENT_TIMESTAMP,
            synchro INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def insert_travail(data):
    conn = sqlite3.connect(DB_TRAVAIL_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO collecte_travail 
        (annee, departement, manoeuvres_hommes, manoeuvres_femmes, employes_hommes, employes_femmes,
         etablissements_ouverts, etablissements_fermes, ei, sa, sarl, suarl, gie, ong, autres_statuts,
         emplois_generes, emplois_perdus, cdi_hommes, cdi_femmes, cdd_hommes, cdd_femmes,
         saisonnier_hommes, saisonnier_femmes, apprentissage_hommes, apprentissage_femmes,
         temporaire_hommes, temporaire_femmes, stage_hommes, stage_femmes,
         conflit_indiv_conciliation, conflit_indiv_partielle, conflit_indiv_non,
         conflit_collectif_conciliation, conflit_collectif_partielle, conflit_collectif_non,
         synchro)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    ''', data)
    conn.commit()
    conn.close()
    return True

def get_all_travail():
    conn = sqlite3.connect(DB_TRAVAIL_PATH)
    df = pd.read_sql_query("SELECT * FROM collecte_travail ORDER BY id DESC", conn)
    conn.close()
    return df

def delete_all_travail():
    conn = sqlite3.connect(DB_TRAVAIL_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM collecte_travail")
    conn.commit()
    conn.close()

# Initialisation des bases
init_ninea_db()
init_travail_db()

# -------------------------------
# FONCTIONS NINEA (existantes)
# -------------------------------
def get_all_ninea():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM collecte_ninea ORDER BY id", conn)
    conn.close()
    return df

def insert_ninea(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO collecte_ninea 
            (nom_complet, cni, sexe, activite_principale, regime, forme_juridique, date_depot, commune, departement, secteur, synchro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        ''', data)
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_all_ninea():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM collecte_ninea")
    conn.commit()
    conn.close()

# -------------------------------
# LISTES COMMUNES
# -------------------------------
communes = [
    "DIAKHAO", "DIAOULE", "DIARRERE", "DIOFIOR", "DIOUROUP", "DJILASSE", "FATICK",
    "FIMELA", "LOUL SESSENE", "MBELLACADIO", "NDIOB", "NGAKHOKHEME", "NIAKHAR",
    "PALMARIN FACAO", "PATAR SINE", "TATTAGUINE", "THIARE NDIALGUI", "BASSOUL",
    "DIAGANE BARKA", "DJILOR", "DJIRNDA", "DIOSSONG", "DIONEWAR", "FOUNDIOUGNE",
    "KARANG POSTE", "KEUR SALOUM DIANE", "KEUR SAMBA GUEYE", "MBAM", "NIASSENE",
    "NIORO ALASSANE FALL", "PASSY", "SOKONE", "SOUM", "TOUBACOUTA", "COLOBANE",
    "GOSSAS", "MBAR", "NDIENE LAGANE", "OUADIOUR", "PATAR LIA"
]
departements = ["Fatick", "Foundiougne", "Gossas", "Région"]

secteurs_liste = [
    "NINEA (Entreprises)", "Agriculture", "Aquaculture", "Eaux et forêts",
    "Élevage", "Service financier", "Pêche", "Santé", "Éducation", "Tourisme",
    "Transports", "Eau Assainissement et Hygiène", "Justice", "Météo", "BTP/Construction",
    "Travail"
]

# -------------------------------
# SESSION STATE
# -------------------------------
if 'confirm_delete' not in st.session_state:
    st.session_state.confirm_delete = False
if 'secteur_courant' not in st.session_state:
    st.session_state.secteur_courant = "NINEA (Entreprises)"
if 'annee_courante' not in st.session_state:
    st.session_state.annee_courante = "Tous"

# -------------------------------
# MENU
# -------------------------------
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio(
    "Choisir une page",
    [
        "🏠 Accueil",
        "📊 Données",
        "📅 Période",
        "📈 Visualisation",
        "🗄️ Base d'exploration"
    ]
)
if st.sidebar.button("🔄 Rafraîchir les données", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# ===============================
# PAGE ACCUEIL
# ===============================
if page == "🏠 Accueil":
    show_main_title()
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">📊 SRSD FATICK</div>
        <div class="hero-subtitle">Service Régional de la Statistique et de la Démographie</div>
        <div class="hero-description">
            Production, analyse et diffusion de données statistiques pour le développement de la région de Fatick
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🎯 Notre Mission")
    st.markdown("""
    <div style="background-color: #e8f4f8; padding: 1.5rem; border-radius: 15px; margin: 1rem 0; text-align: center;">
        <div style="font-size: 1.1rem; line-height: 1.6; color: #333;">
            Le Service Régional de la Statistique et de la Démographie (SRSD) de Fatick a pour mission de <strong>collecter, traiter, analyser et diffuser</strong> 
            les données statistiques dans tous les secteurs d'activité de la région.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Secteurs d'activité couverts")
    secteurs = [
        ("🌾", "Agriculture"), ("🐟", "Aquaculture"), ("🌲", "Eaux et forêts"),
        ("🐄", "Élevage"), ("💰", "Service financier"), ("🎣", "Pêche"),
        ("🏥", "Santé"), ("📚", "Éducation"), ("✈️", "Tourisme"),
        ("🚛", "Transports"), ("💧", "Eau Assainissement et Hygiène"), ("⚖️", "Justice"),
        ("🌤️", "Météo"), ("🏗️", "BTP/Construction"), ("📊", "NINEA (Entreprises)"),
        ("👔", "Travail")
    ]
    cols = st.columns(5)
    for i, (icon, title) in enumerate(secteurs):
        with cols[i % 5]:
            st.markdown(f'<div class="sector-card"><div class="sector-icon">{icon}</div><div class="sector-title">{title}</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎯 Nos Objectifs Stratégiques")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="info-card"><div class="info-icon">📈</div><div class="info-title">Aide à la décision</div><div class="info-text">Fournir des données fiables aux autorités</div></div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="info-card"><div class="info-icon">📢</div><div class="info-title">Diffusion de l'information</div><div class="info-text">Données accessibles à tous</div></div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="info-card"><div class="info-icon">🔬</div><div class="info-title">Recherche & Études</div><div class="info-text">Études sectorielles approfondies</div></div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="info-card"><div class="info-icon">🤝</div><div class="info-title">Partenariat</div><div class="info-text">Collaboration avec les acteurs locaux</div></div>
        """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📍 Territoire d'intervention")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="department-badge">🏙️ FATICK<br>Chef-lieu de région</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="department-badge">⚓ FOUNDIOUGNE<br>Zone économique</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="department-badge">🌾 GOSSAS<br>Zone agricole</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
    <footer>
        <p><strong>SRSD FATICK</strong> - Service Régional de la Statistique et de la Démographie</p>
        <p>© 2026 - ANSD | Région de Fatick - Sénégal</p>
    </footer>
    """, unsafe_allow_html=True)

# ===============================
# PAGE DONNÉES
# ===============================
elif page == "📊 Données":
    show_main_title()
    st.title("📊 Données par secteur")
    
    secteur = st.selectbox("Choisissez un secteur", secteurs_liste, 
                           index=secteurs_liste.index(st.session_state.secteur_courant) if st.session_state.secteur_courant in secteurs_liste else 0)
    st.session_state.secteur_courant = secteur
    
    if secteur == "Travail":
        df = get_all_travail()
        if df.empty:
            st.info(f"Aucune donnée pour le secteur **{secteur}**.")
        else:
            st.metric(f"Nombre d'enregistrements - {secteur}", len(df))
            df_afficher = df.drop(columns=['synchro'], errors='ignore')
            st.dataframe(df_afficher, use_container_width=True)
    else:
        df = get_all_ninea()
        if df.empty:
            st.info(f"Aucune donnée pour le secteur **{secteur}**.")
        else:
            df_filtre = df[df['secteur'] == secteur] if 'secteur' in df.columns else df
            st.metric(f"Nombre d'enregistrements - {secteur}", len(df_filtre))
            df_afficher = df_filtre.drop(columns=['secteur', 'synchro'], errors='ignore')
            st.dataframe(df_afficher, use_container_width=True)

# ===============================
# PAGE PÉRIODE
# ===============================
elif page == "📅 Période":
    show_main_title()
    st.title("📅 Analyse par période")
    
    annee_options = ["Tous", 2023, 2024, 2025, 2026]
    annee = st.selectbox("Sélectionnez une année", annee_options, index=annee_options.index(st.session_state.annee_courante) if st.session_state.annee_courante in annee_options else 0)
    st.session_state.annee_courante = annee
    st.info(f"Secteur actuel : **{st.session_state.secteur_courant}** – Année sélectionnée : **{annee}**")
    
    if st.session_state.secteur_courant == "Travail":
        df = get_all_travail()
        if not df.empty and annee != "Tous":
            df = df[df['annee'] == annee]
        if df.empty:
            st.info(f"Aucune donnée pour cette combinaison.")
        else:
            st.metric(f"Nombre d'enregistrements", len(df))
            df_afficher = df.drop(columns=['synchro'], errors='ignore')
            st.dataframe(df_afficher, use_container_width=True)
    else:
        df = get_all_ninea()
        if not df.empty and annee != "Tous":
            df['date_depot'] = pd.to_datetime(df['date_depot'], errors='coerce')
            df = df[df['date_depot'].dt.year == annee]
        df_filtre = df[df['secteur'] == st.session_state.secteur_courant] if 'secteur' in df.columns else df
        if df_filtre.empty:
            st.info(f"Aucune donnée pour cette combinaison.")
        else:
            st.metric(f"Nombre d'enregistrements", len(df_filtre))
            df_afficher = df_filtre.drop(columns=['secteur', 'synchro'], errors='ignore')
            st.dataframe(df_afficher, use_container_width=True)

# ===============================
# PAGE VISUALISATION
# ===============================
elif page == "📈 Visualisation":
    show_main_title()
    st.title("📈 Visualisation et recherche")
    
    if st.session_state.secteur_courant == "Travail":
        df = get_all_travail()
        if st.session_state.annee_courante != "Tous":
            df = df[df['annee'] == st.session_state.annee_courante]
        if df.empty:
            st.warning(f"Aucune donnée pour le secteur **Travail** et l'année **{st.session_state.annee_courante}**.")
        else:
            st.dataframe(df.drop(columns=['synchro'], errors='ignore'), use_container_width=True)
    else:
        df = get_all_ninea()
        if st.session_state.annee_courante != "Tous":
            df['date_depot'] = pd.to_datetime(df['date_depot'], errors='coerce')
            df = df[df['date_depot'].dt.year == st.session_state.annee_courante]
        df_filtre = df[df['secteur'] == st.session_state.secteur_courant] if 'secteur' in df.columns else df
        if df_filtre.empty:
            st.warning(f"Aucune donnée pour le secteur **{st.session_state.secteur_courant}** et l'année **{st.session_state.annee_courante}**.")
        else:
            st.dataframe(df_filtre.drop(columns=['secteur', 'synchro'], errors='ignore'), use_container_width=True)

# ===============================
# PAGE BASE D'EXPLORATION
# ===============================
elif page == "🗄️ Base d'exploration":
    show_main_title()
    
    secteur_choisi = st.selectbox("📌 Choisir le secteur de collecte", secteurs_liste)
    
    # ==================== FORMULAIRE NINEA ====================
    if secteur_choisi == "NINEA (Entreprises)":
        st.markdown(f"### 📝 Formulaire de collecte - {secteur_choisi}")
        with st.form(key="formulaire_ninea", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nom_complet = st.text_input("Nom complet *", placeholder="Ex: GIE ANDOUN SERVICES")
                cni = st.text_input("Numéro CNI *", placeholder="Ex: 146220010114")
            with col2:
                sexe = st.radio("Sexe *", ["Masculin", "Féminin"], horizontal=True)
                activite_principale = st.text_input("Activité principale *", placeholder="Ex: AGRICULTURE")
            
            col3, col4 = st.columns(2)
            with col3:
                regime = st.radio("Régime *", ["Personne physique", "Personne morale"], horizontal=True)
            with col4:
                forme_juridique = st.selectbox("Forme juridique *", [
                    "ENTREPRISE INDIVIDUELLE", "GIE", "SARL", "SAS", "SNC",
                    "COOPERATIVE", "ASSOCIATION", "ONG", "ENTREPRISE PUBLIQUE"
                ])
            
            col5, col6 = st.columns(2)
            with col5:
                date_depot = st.date_input("Date de dépôt *", datetime.today())
            with col6:
                commune = st.selectbox("Commune *", communes)
            
            departement = st.selectbox("Département *", departements[:-1])  # Sans Région pour NINEA
            
            st.markdown("** * champs obligatoires**")
            submitted = st.form_submit_button("✅ Enregistrer la collecte")
            
            if submitted:
                if not nom_complet or not cni or not activite_principale:
                    st.error("❌ Veuillez remplir tous les champs obligatoires")
                else:
                    data = (nom_complet, cni, sexe, activite_principale, regime,
                            forme_juridique, date_depot.strftime("%Y-%m-%d"), commune, departement, secteur_choisi)
                    success = insert_ninea(data)
                    if success:
                        st.markdown(f'<div class="success-message">✅ Données enregistrées avec succès dans le secteur **{secteur_choisi}**</div>', unsafe_allow_html=True)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Ce CNI existe déjà dans la base")
    
    # ==================== FORMULAIRE TRAVAIL ====================
    elif secteur_choisi == "Travail":
        st.markdown(f"### 📝 Formulaire de collecte - {secteur_choisi}")
        
        with st.form(key="formulaire_travail", clear_on_submit=True):
            # Année et Département
            col1, col2 = st.columns(2)
            with col1:
                annee = st.selectbox("Année *", [2023, 2024, 2025, 2026])
            with col2:
                departement = st.selectbox("Département / Région *", departements)
            
            st.markdown("---")
            
            # Demandeurs d'emploi
            st.markdown("**Demandeurs d'emploi**")
            col1, col2 = st.columns(2)
            with col1:
                manoeuvres_hommes = st.number_input("Manœuvres - Hommes", min_value=0, step=1, value=0)
                employes_hommes = st.number_input("Employés - Hommes", min_value=0, step=1, value=0)
            with col2:
                manoeuvres_femmes = st.number_input("Manœuvres - Femmes", min_value=0, step=1, value=0)
                employes_femmes = st.number_input("Employés - Femmes", min_value=0, step=1, value=0)
            
            st.markdown("---")
            
            # Établissements
            st.markdown("**Établissements**")
            col1, col2 = st.columns(2)
            with col1:
                etablissements_ouverts = st.number_input("Établissements ouverts", min_value=0, step=1, value=0)
            with col2:
                etablissements_fermes = st.number_input("Établissements fermés", min_value=0, step=1, value=0)
            
            st.markdown("---")
            
            # Statut juridique
            st.markdown("**Statut juridique (établissements ouverts)**")
            col1, col2, col3 = st.columns(3)
            with col1:
                ei = st.number_input("EI", min_value=0, step=1, value=0)
                sarl = st.number_input("SARL", min_value=0, step=1, value=0)
                gie = st.number_input("GIE", min_value=0, step=1, value=0)
            with col2:
                sa = st.number_input("SA", min_value=0, step=1, value=0)
                suarl = st.number_input("SUARL", min_value=0, step=1, value=0)
                ong = st.number_input("ONG", min_value=0, step=1, value=0)
            with col3:
                autres_statuts = st.number_input("Autres", min_value=0, step=1, value=0)
            
            st.markdown("---")
            
            # Emplois générés/perdus
            st.markdown("**Emplois**")
            col1, col2 = st.columns(2)
            with col1:
                emplois_generes = st.number_input("Emplois générés", min_value=0, step=1, value=0)
            with col2:
                emplois_perdus = st.number_input("Emplois perdus", min_value=0, step=1, value=0)
            
            st.markdown("---")
            
            # Contrats de travail
            st.markdown("**Contrats de travail**")
            
            # CDI
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**CDI**")
                cdi_hommes = st.number_input("CDI - Hommes", min_value=0, step=1, value=0, key="cdi_h")
                cdd_hommes = st.number_input("CDD - Hommes", min_value=0, step=1, value=0, key="cdd_h")
                saisonnier_hommes = st.number_input("Saisonnier - Hommes", min_value=0, step=1, value=0, key="sais_h")
                apprentissage_hommes = st.number_input("Apprentissage - Hommes", min_value=0, step=1, value=0, key="app_h")
                temporaire_hommes = st.number_input("Temporaire - Hommes", min_value=0, step=1, value=0, key="temp_h")
                stage_hommes = st.number_input("Stage - Hommes", min_value=0, step=1, value=0, key="stage_h")
            with col2:
                st.markdown("**CDI**")
                cdi_femmes = st.number_input("CDI - Femmes", min_value=0, step=1, value=0, key="cdi_f")
                cdd_femmes = st.number_input("CDD - Femmes", min_value=0, step=1, value=0, key="cdd_f")
                saisonnier_femmes = st.number_input("Saisonnier - Femmes", min_value=0, step=1, value=0, key="sais_f")
                apprentissage_femmes = st.number_input("Apprentissage - Femmes", min_value=0, step=1, value=0, key="app_f")
                temporaire_femmes = st.number_input("Temporaire - Femmes", min_value=0, step=1, value=0, key="temp_f")
                stage_femmes = st.number_input("Stage - Femmes", min_value=0, step=1, value=0, key="stage_f")
            
            st.markdown("---")
            
            # Conflits de travail
            st.markdown("**Conflits de travail**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Individuels**")
                conflit_indiv_conciliation = st.number_input("Conciliation", min_value=0, step=1, value=0, key="ind_conc")
                conflit_indiv_partielle = st.number_input("Conciliation partielle", min_value=0, step=1, value=0, key="ind_part")
                conflit_indiv_non = st.number_input("Non conciliation", min_value=0, step=1, value=0, key="ind_non")
            with col2:
                st.markdown("**Collectifs**")
                conflit_collectif_conciliation = st.number_input("Conciliation", min_value=0, step=1, value=0, key="col_conc")
                conflit_collectif_partielle = st.number_input("Conciliation partielle", min_value=0, step=1, value=0, key="col_part")
                conflit_collectif_non = st.number_input("Non conciliation", min_value=0, step=1, value=0, key="col_non")
            
            st.markdown("** * champs obligatoires**")
            submitted = st.form_submit_button("✅ Enregistrer la collecte")
            
            if submitted:
                data = (
                    annee, departement,
                    manoeuvres_hommes, manoeuvres_femmes, employes_hommes, employes_femmes,
                    etablissements_ouverts, etablissements_fermes,
                    ei, sa, sarl, suarl, gie, ong, autres_statuts,
                    emplois_generes, emplois_perdus,
                    cdi_hommes, cdi_femmes, cdd_hommes, cdd_femmes,
                    saisonnier_hommes, saisonnier_femmes,
                    apprentissage_hommes, apprentissage_femmes,
                    temporaire_hommes, temporaire_femmes,
                    stage_hommes, stage_femmes,
                    conflit_indiv_conciliation, conflit_indiv_partielle, conflit_indiv_non,
                    conflit_collectif_conciliation, conflit_collectif_partielle, conflit_collectif_non
                )
                insert_travail(data)
                st.markdown(f'<div class="success-message">✅ Données enregistrées avec succès dans le secteur **{secteur_choisi}**</div>', unsafe_allow_html=True)
                st.balloons()
                st.rerun()
    
    # ==================== AUTRES SECTEURS ====================
    else:
        st.markdown(f"### 📝 Formulaire de collecte - {secteur_choisi}")
        st.info(f"Formulaire pour le secteur **{secteur_choisi}** en cours de développement.")
    
    # ==================== AFFICHAGE DES DONNÉES COLLECTÉES ====================
    st.markdown("---")
    st.markdown("### 📊 Données déjà collectées")
    
    if secteur_choisi == "Travail":
        df_collecte = get_all_travail()
        if df_collecte.empty:
            st.info("📭 Aucune donnée collectée pour le secteur Travail.")
        else:
            st.metric("📋 Nombre total d'enregistrements", len(df_collecte))
            df_afficher = df_collecte.drop(columns=['synchro'], errors='ignore')
            st.dataframe(df_afficher, use_container_width=True)
    else:
        df_collecte = get_all_ninea()
        df_filtre = df_collecte[df_collecte['secteur'] == secteur_choisi] if 'secteur' in df_collecte.columns else df_collecte
        if df_filtre.empty:
            st.info(f"📭 Aucune donnée collectée pour le secteur {secteur_choisi}.")
        else:
            st.metric("📋 Nombre total d'enregistrements", len(df_filtre))
            df_afficher = df_filtre.drop(columns=['secteur', 'synchro'], errors='ignore')
            st.dataframe(df_afficher, use_container_width=True)
    
    # ==================== QUATRE BOUTONS EN BAS ====================
    st.markdown("---")
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    
    with col_btn1:
        if secteur_choisi == "Travail":
            if not df_collecte.empty:
                csv_data = df_collecte.drop(columns=['synchro'], errors='ignore').to_csv(index=False)
                st.download_button("📥 Exporter CSV", csv_data, f"export_travail_{datetime.now():%Y%m%d_%H%M%S}.csv", "text/csv")
            else:
                st.button("📥 Exporter CSV", disabled=True)
        else:
            if not df_filtre.empty:
                csv_data = df_filtre.drop(columns=['synchro', 'id'], errors='ignore').to_csv(index=False)
                st.download_button("📥 Exporter CSV", csv_data, f"export_{secteur_choisi}_{datetime.now():%Y%m%d_%H%M%S}.csv", "text/csv")
            else:
                st.button("📥 Exporter CSV", disabled=True)
    
    with col_btn2:
        st.info("📂 Import CSV - À venir")
    
    with col_btn3:
        if st.button("🗑️ Vider toutes les données", key="btn_vider"):
            st.session_state.confirm_delete = True
    
    with col_btn4:
        st.info("🔄 Synchronisation - À venir")
    
    if st.session_state.confirm_delete:
        st.markdown('<div class="warning-message">⚠️ Attention : suppression définitive de TOUTES les données. Confirmez ?</div>', unsafe_allow_html=True)
        col_yes, col_no = st.columns(2)
        if col_yes.button("✅ Oui, tout supprimer"):
            if secteur_choisi == "Travail":
                delete_all_travail()
            else:
                delete_all_ninea()
            st.session_state.confirm_delete = False
            st.success("✅ Base vidée avec succès.")
            st.rerun()
        if col_no.button("❌ Annuler"):
            st.session_state.confirm_delete = False
            st.rerun()

# ===============================
# FIN
# ===============================