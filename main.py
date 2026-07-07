# ===============================
# APPLICATION NINEA - VERSION PRO MAX AVEC COLLECTE LOCALE
# ===============================

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from sqlalchemy import create_engine
from datetime import datetime
import os

# -------------------------------
# CONFIGURATION
# -------------------------------
st.set_page_config(
    page_title="Application NINEA SRSD FATICK",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# STYLE (gardé identique)
# -------------------------------
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .main-title {
        background: linear-gradient(135deg, #003366 0%, #0055a4 100%);
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .main-title h1 {
        color: white;
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    .main-title p {
        color: #e0e0e0;
        margin: 0;
        font-size: 0.9rem;
    }
    h1, h2, h3 {
        color: #003366;
        font-weight: bold;
    }
    .hero-container {
        background: linear-gradient(135deg, #003366 0%, #006699 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .hero-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: white;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        color: #f0f0f0;
    }
    .hero-description {
        font-size: 1rem;
        color: #e0e0e0;
        margin-top: 1rem;
    }
    .sector-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        transition: transform 0.3s;
    }
    .sector-card:hover {
        transform: translateY(-5px);
    }
    .sector-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    .sector-title {
        font-weight: bold;
        color: white;
        font-size: 0.9rem;
    }
    .info-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        text-align: center;
        transition: all 0.3s;
    }
    .info-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transform: translateY(-3px);
    }
    .info-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .info-title {
        font-size: 1.1rem;
        font-weight: bold;
        color: #003366;
        margin-bottom: 0.5rem;
    }
    .info-text {
        color: #666;
        font-size: 0.85rem;
    }
    .department-badge {
        background-color: #e8f4f8;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        color: #003366;
        margin: 0.5rem 0;
    }
    footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        margin-top: 3rem;
        border-top: 1px solid #ddd;
    }
    .highlight {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
    }
    .mission-text {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #333;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# FONCTIONS DE BASE DE DONNÉES (SQLite locale)
# -------------------------------
def init_local_db():
    """Initialise la base SQLite locale"""
    conn = sqlite3.connect('ninea_local.db')
    cursor = conn.cursor()
    
    # Création de la table ninea
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ninea (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_complet TEXT NOT NULL,
            cni TEXT NOT NULL,
            sexe TEXT NOT NULL,
            activite_principale TEXT NOT NULL,
            regime TEXT NOT NULL,
            forme_juridique TEXT NOT NULL,
            date_depot TEXT NOT NULL,
            commune TEXT NOT NULL,
            date_saisie TEXT NOT NULL,
            synchronise INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_ninea_local(data):
    """Insère une entreprise dans la base locale SQLite"""
    conn = sqlite3.connect('ninea_local.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO ninea (nom_complet, cni, sexe, activite_principale, regime, 
                          forme_juridique, date_depot, commune, date_saisie, synchronise)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    ''', data)
    
    conn.commit()
    conn.close()

def get_all_ninea_local():
    """Récupère toutes les entreprises de la base locale"""
    conn = sqlite3.connect('ninea_local.db')
    df = pd.read_sql_query("SELECT * FROM ninea ORDER BY id DESC", conn)
    conn.close()
    return df

def get_stats_local():
    """Récupère les statistiques locales"""
    conn = sqlite3.connect('ninea_local.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM ninea")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ninea WHERE synchronise = 1")
    synchronise = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ninea WHERE synchronise = 0")
    non_synchronise = cursor.fetchone()[0]
    
    conn.close()
    return total, synchronise, non_synchronise

def synchroniser_vers_postgresql():
    """Synchronise les données non synchronisées vers PostgreSQL"""
    conn_local = sqlite3.connect('ninea_local.db')
    df_non_sync = pd.read_sql_query("SELECT * FROM ninea WHERE synchronise = 0", conn_local)
    conn_local.close()
    
    if df_non_sync.empty:
        return 0
    
    try:
        engine = create_engine("postgresql+psycopg2://postgres:ansdfatick@localhost:5432/ANSD_FATICK")
        
        for _, row in df_non_sync.iterrows():
            # Vérifier si le CNI existe déjà
            check_query = f"SELECT COUNT(*) FROM ninea WHERE cni = '{row['cni']}'"
            exists = pd.read_sql(check_query, engine).iloc[0, 0]
            
            if exists == 0:
                insert_query = f"""
                INSERT INTO ninea (nom_complet, cni, sexe, activite_principale, regime, 
                                   forme_juridique, date_depot, commune_id)
                VALUES ('{row['nom_complet']}', '{row['cni']}', '{row['sexe']}', 
                        '{row['activite_principale']}', '{row['regime']}', 
                        '{row['forme_juridique']}', '{row['date_depot']}', 
                        (SELECT id FROM commune WHERE nom = '{row['commune']}'))
                """
                engine.execute(insert_query)
        
        # Marquer comme synchronisées
        conn_local = sqlite3.connect('ninea_local.db')
        cursor = conn_local.cursor()
        cursor.execute("UPDATE ninea SET synchronise = 1 WHERE synchronise = 0")
        conn_local.commit()
        conn_local.close()
        
        return len(df_non_sync)
    except Exception as e:
        st.error(f"Erreur de synchronisation : {str(e)}")
        return -1

# -------------------------------
# TITRE PRINCIPAL FIXE
# -------------------------------
def show_main_title():
    st.markdown("""
    <div class="main-title">
        <h1>📊 SRSD FATICK - SYSTÈME D'INFORMATION STATISTIQUE</h1>
        <p>Agence Nationale de la Statistique et de la Démographie - Région de Fatick</p>
    </div>
    """, unsafe_allow_html=True)

# -------------------------------
# COMMUNAUTÉ (liste des communes)
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

# -------------------------------
# FONCTION POUR REGROUPER ENTREPRISE INDIVIDUELLE
# -------------------------------
def regrouper_entreprise_individuelle(df, colonne):
    variantes = [
        "ENTREPRISE INDIVIDUELLE", "Entreprise Individuelle", "entreprise individuelle",
        "ENREPRISE INDIVIDUELLE", "ENTREPRISE INDIVIDUELE", "ENTREPRISE INDIVIDUEL"
    ]
    for v in variantes:
        df[colonne] = df[colonne].replace(v, "ENTREPRISE INDIVIDUELLE")
    return df

# -------------------------------
# INITIALISATION DE LA BASE LOCALE
# -------------------------------
init_local_db()

# -------------------------------
# MENU
# -------------------------------
st.sidebar.title("📂 Navigation")

page = st.sidebar.radio(
    "Choisir une page",
    [
        "🏠 Accueil",
        "📝 Collecte NINEA",
        "📄 Données stockées",
        "📊 Visualisation & Analyse",
        "🔄 Synchronisation PostgreSQL",
        "🗄️ Exploration base"
    ]
)

# Bouton rafraîchissement
if st.sidebar.button("🔄 Rafraîchir les données"):
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
    
    # Statistiques locales
    total, sync, non_sync = get_stats_local()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Entreprises collectées", total)
    with col2:
        st.metric("✅ Synchronisées", sync)
    with col3:
        st.metric("⏳ En attente", non_sync)
    
    st.markdown("### 🎯 Notre Mission")
    st.markdown("""
    <div class="highlight">
        <div class="mission-text">
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
        ("🚛", "Transports"), ("💧", "Eau, Assainissement et Hygiène"), ("⚖️", "Justice"),
        ("🌤️", "Météo"), ("🏗️", "BTP/Construction"), ("📊", "NINEA (ENTREPRISES)")
    ]
    cols = st.columns(5)
    for i, (icon, title) in enumerate(secteurs):
        with cols[i % 5]:
            st.markdown(f'<div class="sector-card"><div class="sector-icon">{icon}</div><div class="sector-title">{title}</div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎯 Nos Objectifs Stratégiques")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="info-card"><div class="info-icon">📈</div><div class="info-title">Aide à la décision</div><div class="info-text">Fournir des données fiables aux autorités</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="info-card"><div class="info-icon">🔬</div><div class="info-title">Recherche & Études</div><div class="info-text">Études sectorielles approfondies</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="info-card"><div class="info-icon">📢</div><div class="info-title">Diffusion de l\'information</div><div class="info-text">Données accessibles à tous</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="info-card"><div class="info-icon">🤝</div><div class="info-title">Partenariat</div><div class="info-text">Collaboration avec les acteurs locaux</div></div>', unsafe_allow_html=True)
    
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
    st.markdown('<footer><p><strong>SRSD FATICK</strong> - ANSD | Région de Fatick - Sénégal</p></footer>', unsafe_allow_html=True)

# ===============================
# PAGE COLLECTE NINEA (FORMULAIRE)
# ===============================
elif page == "📝 Collecte NINEA":
    show_main_title()
    st.title("📝 Formulaire de collecte - NINEA (SRSD FATICK)")
    
    with st.form("formulaire_ninea", clear_on_submit=True):
        st.markdown("### Informations de l'entreprise")
        
        col1, col2 = st.columns(2)
        with col1:
            nom_complet = st.text_input("Nom complet de l'entreprise / promoteur *", placeholder="Ex: GIE ANDOUN SERVICES")
            cni = st.text_input("Numéro CNI *", placeholder="Ex: 146220010114")
            sexe = st.radio("Sexe *", ["Masculin", "Féminin"], horizontal=True)
        
        with col2:
            activite_principale = st.text_input("Activité principale *", placeholder="Ex: AGRICULTURE, COMMERCE...")
            regime = st.radio("Régime *", ["Personne physique", "Personne morale"], horizontal=True)
        
        forme_juridique = st.selectbox("Forme juridique *", [
            "ENTREPRISE INDIVIDUELLE", "GIE (Groupement d'intérêt Economique)",
            "SARL (Société à Responsabilité Limitée)", "SAS (Société par Action Simplifiée)",
            "SNC (Societe en nom collectif)", "COOPERATIVE", "ASSOCIATION", "ONG", "ENTREPRISE PUBLIQUE"
        ])
        
        col3, col4 = st.columns(2)
        with col3:
            date_depot = st.date_input("Date de dépôt *", datetime.today())
        with col4:
            commune = st.selectbox("Commune *", communes)
        
        st.markdown("* = champ obligatoire")
        
        submitted = st.form_submit_button("✅ Enregistrer l'entreprise")
        
        if submitted:
            if not nom_complet or not cni or not activite_principale:
                st.error("Veuillez remplir tous les champs obligatoires (nom, CNI, activité)")
            else:
                # Insertion dans SQLite locale
                data = (
                    nom_complet, cni, sexe, activite_principale, regime,
                    forme_juridique, date_depot.strftime("%Y-%m-%d"), commune,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                insert_ninea_local(data)
                
                st.markdown('<div class="success-message">✅ Entreprise enregistrée avec succès dans la base locale !</div>', unsafe_allow_html=True)
                st.balloons()

# ===============================
# PAGE DONNÉES STOCKÉES
# ===============================
elif page == "📄 Données stockées":
    show_main_title()
    st.title("📄 Entreprises collectées (stockage local SQLite)")
    
    df = get_all_ninea_local()
    
    if df.empty:
        st.info("Aucune donnée collectée pour le moment. Utilisez le formulaire de collecte.")
    else:
        st.metric("Nombre total d'entreprises collectées", df.shape[0])
        
        # Filtres
        col1, col2 = st.columns(2)
        with col1:
            if 'commune' in df.columns:
                communes_filter = st.multiselect("Filtrer par commune", df['commune'].unique())
                if communes_filter:
                    df = df[df['commune'].isin(communes_filter)]
        with col2:
            if 'sexe' in df.columns:
                sexe_filter = st.multiselect("Filtrer par sexe", df['sexe'].unique())
                if sexe_filter:
                    df = df[df['sexe'].isin(sexe_filter)]
        
        st.dataframe(df, use_container_width=True)
        
        # Export CSV
        csv = df.to_csv(index=False)
        st.download_button("📥 Exporter en CSV", csv, "export_ninea.csv", "text/csv")

# ===============================
# PAGE VISUALISATION & ANALYSE
# ===============================
elif page == "📊 Visualisation & Analyse":
    show_main_title()
    st.title("📊 Visualisation interactive des données")
    
    df = get_all_ninea_local()
    
    if df.empty:
        st.warning("Aucune donnée disponible. Veuillez d'abord collecter des données via le formulaire.")
    else:
        # Conversion date
        if 'date_depot' in df.columns:
            df["date_depot"] = pd.to_datetime(df["date_depot"], errors="coerce")
        
        # KPI
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total entreprises", df.shape[0])
        with col2:
            st.metric("Communes couvertes", df['commune'].nunique() if 'commune' in df.columns else 0)
        
        # Répartition Physique / Morale
        if 'regime' in df.columns:
            st.subheader("📊 Répartition Physique / Morale")
            regime_counts = df["regime"].value_counts().reset_index()
            regime_counts.columns = ["Régime", "Nombre"]
            fig_regime = px.bar(regime_counts, x="Régime", y="Nombre", text="Nombre", color="Régime")
            st.plotly_chart(fig_regime, use_container_width=True)
        
        # Répartition par sexe
        if 'sexe' in df.columns:
            st.subheader("👥 Répartition par sexe")
            sexe_counts = df["sexe"].value_counts().reset_index()
            sexe_counts.columns = ["Sexe", "Nombre"]
            fig_sexe = px.bar(sexe_counts, x="Sexe", y="Nombre", text="Nombre", color="Sexe")
            st.plotly_chart(fig_sexe, use_container_width=True)
        
        # Répartition par commune
        if 'commune' in df.columns:
            st.subheader("📍 Top 15 communes")
            commune_counts = df["commune"].value_counts().head(15).reset_index()
            commune_counts.columns = ["Commune", "Nombre"]
            fig_commune = px.bar(commune_counts, x="Commune", y="Nombre", text="Nombre", color="Commune")
            st.plotly_chart(fig_commune, use_container_width=True)
        
        # Formes juridiques
        if 'forme_juridique' in df.columns:
            st.subheader("📊 Répartition des formes juridiques")
            df_temp = df.copy()
            df_temp["forme_juridique"] = df_temp["forme_juridique"].fillna("Non renseigné")
            df_temp = regrouper_entreprise_individuelle(df_temp, "forme_juridique")
            forme_counts = df_temp["forme_juridique"].value_counts().reset_index()
            forme_counts.columns = ["Forme juridique", "Nombre"]
            forme_counts = forme_counts.sort_values("Nombre", ascending=True)
            
            fig_forme = px.bar(forme_counts, x="Nombre", y="Forme juridique", text="Nombre",
                               orientation='h', color_continuous_scale='Blues')
            fig_forme.update_layout(xaxis_title="Nombre d'entreprises", yaxis_title="Forme juridique",
                                     height=max(400, len(forme_counts)*35), showlegend=False)
            fig_forme.update_traces(textposition='outside')
            st.plotly_chart(fig_forme, use_container_width=True)

# ===============================
# PAGE SYNCHRONISATION POSTGRESQL
# ===============================
elif page == "🔄 Synchronisation PostgreSQL":
    show_main_title()
    st.title("🔄 Synchronisation vers le serveur PostgreSQL")
    
    total, sync, non_sync = get_stats_local()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Total collecté", total)
    with col2:
        st.metric("✅ Déjà synchronisées", sync)
    with col3:
        st.metric("⏳ En attente de synchronisation", non_sync)
    
    if non_sync > 0:
        st.warning(f"⚠️ {non_sync} entreprise(s) en attente de synchronisation vers PostgreSQL")
        
        if st.button("🚀 Lancer la synchronisation maintenant"):
            with st.spinner("Synchronisation en cours..."):
                result = synchroniser_vers_postgresql()
                if result > 0:
                    st.success(f"✅ {result} entreprise(s) synchronisée(s) avec succès vers PostgreSQL !")
                    st.rerun()
                elif result == 0:
                    st.info("Aucune nouvelle donnée à synchroniser.")
                else:
                    st.error("❌ Erreur lors de la synchronisation. Vérifiez la connexion PostgreSQL.")
    else:
        st.success("✅ Toutes les données sont déjà synchronisées avec PostgreSQL !")
    
    st.markdown("---")
    st.info("""
    **Configuration PostgreSQL requise :**
    - Hôte : localhost
    - Port : 5432
    - Base : ANSD_FATICK
    - Utilisateur : postgres
    - Mot de passe : ansdfatick
    
    Assurez-vous que PostgreSQL est démarré avant la synchronisation.
    """)

# ===============================
# PAGE EXPLORATION BASE LOCALE
# ===============================
elif page == "🗄️ Exploration base":
    show_main_title()
    st.title("🗄️ Exploration de la base locale SQLite")
    
    conn = sqlite3.connect('ninea_local.db')
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
    conn.close()
    
    if not tables.empty:
        table = st.selectbox("Choisir une table", tables['name'])
        if table:
            conn = sqlite3.connect('ninea_local.db')
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            conn.close()
            st.success(f"Table {table} chargée ✅")
            st.metric("Nombre de lignes", df.shape[0])
            st.dataframe(df.head(50), use_container_width=True)
    else:
        st.info("Aucune table trouvée dans la base locale.")