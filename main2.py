# ===============================
# APPLICATION NINEA - VERSION PRO MAX
# ===============================

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# -------------------------------
# CONFIGURATION
# -------------------------------
st.set_page_config(
    page_title="Application NINEA",
    page_icon="📊",
    layout="wide"
)

# -------------------------------
# STYLE
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
    /* Style pour les métriques interactives */
    .metric-container {
        background-color: white;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #003366;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

def show_main_title():
    st.markdown("""
    <div class="main-title">
        <h1>📊 DONNEE NINEA SRSD (FATICK)</h1>
        <p>Agence Nationale de la Statistique et de la Démographie - Région de Fatick</p>
    </div>
    """, unsafe_allow_html=True)

def regrouper_entreprise_individuelle(df, colonne):
    variantes = [
        "ENTREPRISE INDIVIDUELLE", "Entreprise Individuelle", "entreprise individuelle",
        "ENREPRISE INDIVIDUELLE", "ENTREPRISE INDIVIDUELE", "ENTREPRISE INDIVIDUEL",
        "ENTREPRISE INDIVID", "ENTREPRISE INDIVIDU", "ENTREPRISE INDIV",
        "ENTRE INDIVIDUELLE", "E. INDIVIDUELLE", "E.I", "EI", "entreprise ind",
        "ENTREPRISE INMOBILIELLE", "ENTREPRISE INCORPORELLE", "ENTREPRISE IMMOBILIER",
        "ENTREPRISE IMMOBILIERE", "INDIVIDUELLE", "INDIVIDUEL"
    ]
    for v in variantes:
        df[colonne] = df[colonne].replace(v, "ENTREPRISE INDIVIDUELLE")
    mask = df[colonne].str.contains("INDIVID|ENTREPRISE|EI|E.I", case=False, na=False)
    df.loc[mask, colonne] = "ENTREPRISE INDIVIDUELLE"
    return df

@st.cache_resource
def get_engine():
    return create_engine("postgresql+psycopg2://postgres:ansdfatick@localhost:5432/ANSD_FATICK")

engine = get_engine()

st.sidebar.title("📂 Navigation")
page = st.sidebar.radio(
    "Choisir une page",
    [
        "🏠 Accueil", "📄 Données NINEA", "🔍 Recherche par CNI",
        "📊 Statistiques", "📊 Analyse avancée", "📊 Activité dominante", "🗄️ Exploration base"
    ]
)
if st.sidebar.button("🔄 Rafraîchir les données"):
    st.cache_data.clear()
    st.rerun()

# ===============================
# ACCUEIL (sans bande NINEA, sans cartes métriques, secteurs modifiés)
# ===============================
if page == "🏠 Accueil":
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
        ("🚛", "Transports"), ("💧", "Eau Assainissement et Hygiène"), ("⚖️", "Justice"),
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
# DONNÉES NINEA
# ===============================
elif page == "📄 Données NINEA":
    show_main_title()
    st.title("📄 Données NINEA")
    df = pd.read_sql("SELECT * FROM ninea", engine)
    st.metric("Nombre total de lignes", df.shape[0])
    st.dataframe(df, use_container_width=True)

# ===============================
# RECHERCHE CNI
# ===============================
elif page == "🔍 Recherche par CNI":
    show_main_title()
    st.title("🔍 Recherche par CNI")
    cni = st.text_input("Entrer le numéro CNI")
    if cni:
        query = f"""
        SELECT n.nom_complet, n.telephone, n.cni, n.sexe, n.activite_principale, n.regime, n.forme_juridique, n.date_depot, c.nom AS commune, d.nom AS departement
        FROM ninea n
        JOIN commune c ON n.commune_id = c.id
        JOIN departement d ON c.departement_id = d.id
        WHERE n.cni = '{cni}'
        """
        resultat = pd.read_sql(query, engine)
        if not resultat.empty:
            st.success("Entreprise trouvée ✅")
            st.dataframe(resultat, use_container_width=True)
        else:
            st.error("Aucune donnée trouvée")

# ===============================
# STATISTIQUES - AVEC INTERACTIVITÉ SEXE
# ===============================
elif page == "📊 Statistiques":
    show_main_title()
    st.title("📊 Statistiques générales")
    df = pd.read_sql("SELECT * FROM ninea", engine)
    df["date_depot"] = pd.to_datetime(df["date_depot"], errors="coerce")
    annees = sorted(df["date_depot"].dt.year.dropna().unique())
    annee = st.selectbox("📅 Choisir une année", annees)
    df_filtre = df[df["date_depot"].dt.year == annee]

    # KPI existants (total entreprises année + total global)
    col1, col2 = st.columns(2)
    col1.metric(f"Entreprises {annee}", df_filtre.shape[0])
    col2.metric("Total entreprises", df.shape[0])

    # Répartition Physique / Morale
    st.subheader("📊 Répartition Physique / Morale")
    regime_counts = df_filtre["regime"].value_counts().reset_index()
    regime_counts.columns = ["Régime", "Nombre"]
    fig_regime = px.bar(regime_counts, x="Régime", y="Nombre", text="Nombre", color="Régime")
    st.plotly_chart(fig_regime, use_container_width=True)

    # Répartition des formes juridiques (diagramme en bandes)
    st.subheader("📊 Répartition des formes juridiques")
    df_filtre["forme_juridique"] = df_filtre["forme_juridique"].fillna("Non renseigné")
    df_filtre = regrouper_entreprise_individuelle(df_filtre, "forme_juridique")
    forme_counts = df_filtre["forme_juridique"].value_counts().reset_index()
    forme_counts.columns = ["Forme juridique", "Nombre"]
    forme_counts = forme_counts.sort_values("Nombre", ascending=True)
    fig_bar = px.bar(forme_counts, x="Nombre", y="Forme juridique", text="Nombre", color="Nombre",
                     orientation='h', color_continuous_scale='Blues')
    fig_bar.update_layout(xaxis_title="Nombre d'entreprises", yaxis_title="Forme juridique",
                          height=max(450, len(forme_counts)*40), showlegend=False)
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- SECTION INTERACTIVE PAR SEXE ---
    st.subheader("👥 Répartition par sexe et indicateurs clés")

    # Sélecteur de sexe
    sexe_options = ["Féminin", "Masculin", "Les deux"]
    sexe_choisi = st.radio(
        "Choisir un sexe à analyser :",
        sexe_options,
        horizontal=True
    )

    # Filtrer les données en fonction du sexe choisi
    if sexe_choisi == "Féminin":
        df_sexe = df_filtre[df_filtre["sexe"] == "Féminin"]
        titre_sexe = "Féminin"
    elif sexe_choisi == "Masculin":
        df_sexe = df_filtre[df_filtre["sexe"] == "Masculin"]
        titre_sexe = "Masculin"
    else:
        df_sexe = df_filtre
        titre_sexe = "les deux sexes"

    # Calcul des trois indicateurs
    total_sexe = df_sexe.shape[0]
    physique_sexe = df_sexe[df_sexe["regime"] == "Personne physique"].shape[0]
    morale_sexe = df_sexe[df_sexe["regime"] == "Personne morale"].shape[0]

    # Affichage des métriques
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{total_sexe}</div>
            <div class="metric-label">🏢 Total entreprises ({titre_sexe})</div>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{physique_sexe}</div>
            <div class="metric-label">👤 Personnes physiques ({titre_sexe})</div>
        </div>
        """, unsafe_allow_html=True)
    with col_c:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{morale_sexe}</div>
            <div class="metric-label">🏛️ Personnes morales ({titre_sexe})</div>
        </div>
        """, unsafe_allow_html=True)

    # Diagramme en bandes pour comparer les deux sexes
    st.markdown("### 📊 Comparaison des sexes")
    sexe_counts = df_filtre["sexe"].value_counts().reset_index()
    sexe_counts.columns = ["Sexe", "Nombre"]
    if not sexe_counts.empty:
        sexe_counts = sexe_counts.sort_values("Nombre", ascending=True)
        fig_sexe = px.bar(
            sexe_counts, 
            x="Nombre", 
            y="Sexe", 
            text="Nombre", 
            color="Sexe",
            orientation='h',
            color_discrete_sequence=['#1f77b4', '#ff7f0e']
        )
        fig_sexe.update_layout(
            xaxis_title="Nombre d'entreprises",
            yaxis_title="Sexe",
            height=350,
            showlegend=False
        )
        fig_sexe.update_traces(textposition='outside')
        st.plotly_chart(fig_sexe, use_container_width=True)
    else:
        st.info("Aucune information sur le sexe pour l'année sélectionnée.")

    # Affichage des détails supplémentaires
    with st.expander("📋 Voir le détail par sexe"):
        st.write("**Répartition par sexe (toutes entreprises confondues) :**")
        st.dataframe(sexe_counts, use_container_width=True)
        
        # Par sexe et régime
        st.write("**Détail par sexe et régime :**")
        sexe_regime = df_filtre.groupby(["sexe", "regime"]).size().reset_index(name="Nombre")
        st.dataframe(sexe_regime, use_container_width=True)

# ===============================
# ANALYSE AVANCÉE
# ===============================
elif page == "📊 Analyse avancée":
    show_main_title()
    st.title("📊 Analyse territoriale")
    query = """
    SELECT n.regime, n.activite_principale, c.nom AS commune, d.nom AS departement
    FROM ninea n
    JOIN commune c ON n.commune_id = c.id
    JOIN departement d ON c.departement_id = d.id
    """
    df = pd.read_sql(query, engine)
    df["departement"] = df["departement"].replace("Fondation", "Foundiougne")
    st.subheader("📍 Répartition par département")
    repart_dep = df["departement"].value_counts().reset_index()
    repart_dep.columns = ["Département", "Nombre"]
    fig_dep = px.bar(repart_dep, x="Département", y="Nombre", text="Nombre", color="Département")
    st.plotly_chart(fig_dep, use_container_width=True)
    departements = sorted(df["departement"].unique())
    choix_dep = st.selectbox("Choisir un département", departements)
    df_dep = df[df["departement"] == choix_dep]
    total_dep = df_dep.shape[0]
    regime_counts = df_dep["regime"].value_counts()
    st.info(f"**Département : {choix_dep}**")
    st.metric("📊 Nombre total d'entreprises", total_dep)
    for regime, count in regime_counts.items():
        st.metric(label=f"🏢 {regime}", value=count)
    st.subheader("📍 Répartition par commune")
    repart_commune = df_dep["commune"].value_counts().reset_index()
    repart_commune.columns = ["Commune", "Nombre"]
    fig_com = px.bar(repart_commune, x="Commune", y="Nombre", text="Nombre", color="Commune")
    st.plotly_chart(fig_com, use_container_width=True)
    communes = sorted(df_dep["commune"].unique())
    choix_com = st.selectbox("Choisir une commune", communes)
    df_com = df_dep[df_dep["commune"] == choix_com]
    total_com = df_com.shape[0]
    regime_counts_com = df_com["regime"].value_counts()
    st.success(f"**Commune : {choix_com}**")
    st.metric("📊 Nombre total d'entreprises", total_com)
    for regime, count in regime_counts_com.items():
        st.metric(label=f"🏢 {regime}", value=count)

# ===============================
# ACTIVITÉ DOMINANTE
# ===============================
elif page == "📊 Activité dominante":
    show_main_title()
    st.title("📊 Activités dominantes")
    query = """
    SELECT n.activite_principale, c.nom AS commune, d.nom AS departement
    FROM ninea n
    JOIN commune c ON n.commune_id = c.id
    JOIN departement d ON c.departement_id = d.id
    """
    df = pd.read_sql(query, engine)
    df["departement"] = df["departement"].replace("Fondation", "Foundiougne")
    st.subheader("📍 Top 4 activités dominantes par département")
    top = df["activite_principale"].value_counts().head(4).index
    df_top = df[df["activite_principale"].isin(top)]
    dep_counts = df_top.groupby(["departement", "activite_principale"]).size().reset_index(name="Nombre")
    fig_dep = px.bar(dep_counts, x="departement", y="Nombre", color="activite_principale", barmode="group")
    fig_dep.update_layout(xaxis_title="Département", yaxis_title="Nombre d'entreprises", legend_title="Activité")
    st.plotly_chart(fig_dep, use_container_width=True)
    st.subheader("📍 Top 4 activités dominantes par commune")
    deps = sorted(df["departement"].unique())
    choix_dep = st.selectbox("Choisir un département", deps, key="dep_act")
    df_dep = df[df["departement"] == choix_dep]
    communes = sorted(df_dep["commune"].unique())
    choix_com = st.selectbox("Choisir une commune", communes, key="com_act")
    df_com = df_dep[df_dep["commune"] == choix_com]
    top_com = df_com["activite_principale"].value_counts().head(4).reset_index()
    top_com.columns = ["Activité", "Nombre"]
    if not top_com.empty:
        fig_com = px.bar(top_com, x="Activité", y="Nombre", text="Nombre", color="Activité")
        fig_com.update_layout(xaxis_title="Activité", yaxis_title="Nombre d'entreprises")
        st.plotly_chart(fig_com, use_container_width=True)
    else:
        st.info(f"Aucune activité pour {choix_com}")

# ===============================
# EXPLORATION BASE
# ===============================
elif page == "🗄️ Exploration base":
    show_main_title()
    st.title("🗄️ Exploration de la base")
    tables = pd.read_sql("SELECT table_name FROM information_schema.tables WHERE table_schema='public'", engine)
    table = st.selectbox("Choisir une table", tables["table_name"])
    if table:
        df = pd.read_sql(f"SELECT * FROM {table}", engine)
        st.success(f"Table {table} chargée ✅")
        st.metric("Nombre de lignes", df.shape[0])
        st.dataframe(df.head(50), use_container_width=True)