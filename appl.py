# ===============================
# APPLICATION NINEA - VERSION PRO MAX
# ===============================

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# ===============================
# CONFIGURATION
# ===============================
st.set_page_config(
    page_title="Application NINEA",
    page_icon="📊",
    layout="wide"
)

# ===============================
# STYLE CSS
# ===============================
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

.stMetric {
    background-color: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.info-card {
    background-color: white;
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    text-align: center;
    margin-bottom: 1rem;
}

.hero-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 20px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.department-badge {
    background-color: #e8f4f8;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    font-weight: bold;
    color: #003366;
}

</style>
""", unsafe_allow_html=True)

# ===============================
# TITRE PRINCIPAL
# ===============================
def show_main_title():

    st.markdown("""
    <div class="main-title">
        <h1>📊 DONNEES NINEA SRSD FATICK</h1>
        <p>Agence Nationale de la Statistique et de la Démographie</p>
    </div>
    """, unsafe_allow_html=True)

# ===============================
# REGROUPEMENT ENTREPRISE INDIVIDUELLE
# ===============================
def regrouper_entreprise_individuelle(df, colonne):

    df[colonne] = (
        df[colonne]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    mask = df[colonne].str.contains(
        "INDIVID|EI|E.I|ENTREPRISE",
        case=False,
        na=False
    )

    df.loc[mask, colonne] = "ENTREPRISE INDIVIDUELLE"

    return df

# ===============================
# CONNEXION POSTGRESQL
# ===============================
@st.cache_resource
def get_engine():

    return create_engine(
        "postgresql+psycopg2://postgres:ansdfatick@localhost:5432/ANSD_FATICK"
    )

engine = get_engine()

# ===============================
# MENU
# ===============================
st.sidebar.title("📂 Navigation")

page = st.sidebar.radio(
    "Choisir une page",
    [
        "🏠 Accueil",
        "📄 Données NINEA",
        "🔍 Recherche par CNI",
        "📊 Statistiques",
        "📊 Analyse avancée",
        "📊 Activité dominante",
        "🗄️ Exploration base"
    ]
)

# ===============================
# BOUTON RAFRAICHIR
# ===============================
if st.sidebar.button("🔄 Rafraîchir les données"):

    st.cache_data.clear()
    st.rerun()

# ===============================
# ACCUEIL
# ===============================
if page == "🏠 Accueil":

    show_main_title()

    st.markdown("""
    <div class="hero-container">
        <h1>📊 ANSD FATICK</h1>
        <p>Système d’analyse des données NINEA</p>
        <p>Région de Fatick - Sénégal</p>
    </div>
    """, unsafe_allow_html=True)

    total = pd.read_sql(
        "SELECT COUNT(*) as total FROM ninea",
        engine
    )["total"].iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="info-card">
            <h2>🏢</h2>
            <h3>{total}</h3>
            <p>Entreprises</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
            <h2>📅</h2>
            <h3>2026</h3>
            <p>Données actualisées</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="info-card">
            <h2>📍</h2>
            <h3>3</h3>
            <p>Départements</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class="info-card">
            <h2>📊</h2>
            <h3>Temps réel</h3>
            <p>PostgreSQL</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("## 📍 Départements couverts")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="department-badge">
            🏙️ FATICK
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="department-badge">
            ⚓ FOUNDIOUGNE
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="department-badge">
            🌾 GOSSAS
        </div>
        """, unsafe_allow_html=True)

# ===============================
# DONNEES NINEA
# ===============================
elif page == "📄 Données NINEA":

    show_main_title()

    st.title("📄 Données NINEA")

    df = pd.read_sql(
        "SELECT * FROM ninea",
        engine
    )

    st.metric(
        "Nombre total de lignes",
        df.shape[0]
    )

    st.dataframe(
        df,
        use_container_width=True
    )

# ===============================
# RECHERCHE PAR CNI
# ===============================
elif page == "🔍 Recherche par CNI":

    show_main_title()

    st.title("🔍 Recherche par CNI")

    cni = st.text_input(
        "Entrer le numéro CNI"
    )

    if cni:

        query = f"""
        SELECT 
            n.nom_complet,
            n.telephone,
            n.cni,
            n.sexe,
            n.activite_principale,
            n.regime,
            n.forme_juridique,
            n.date_depot,
            c.nom AS commune,
            d.nom AS departement
        FROM ninea n
        JOIN commune c ON n.commune_id = c.id
        JOIN departement d ON c.departement_id = d.id
        WHERE n.cni = '{cni}'
        """

        resultat = pd.read_sql(
            query,
            engine
        )

        if not resultat.empty:

            st.success("Entreprise trouvée ✅")

            st.dataframe(
                resultat,
                use_container_width=True
            )

        else:
            st.error("Aucune donnée trouvée")

# ===============================
# STATISTIQUES
# ===============================
elif page == "📊 Statistiques":

    show_main_title()

    st.title("📊 Statistiques générales")

    df = pd.read_sql(
        "SELECT * FROM ninea",
        engine
    )

    df["date_depot"] = pd.to_datetime(
        df["date_depot"],
        errors="coerce"
    )

    annees = sorted(
        df["date_depot"]
        .dt.year
        .dropna()
        .unique()
    )

    annee = st.selectbox(
        "📅 Choisir une année",
        annees
    )

    df_filtre = df[
        df["date_depot"].dt.year == annee
    ]

    col1, col2 = st.columns(2)

    col1.metric(
        f"Entreprises {annee}",
        df_filtre.shape[0]
    )

    col2.metric(
        "Total entreprises",
        df.shape[0]
    )

    st.subheader("📊 Répartition Physique / Morale")

    regime_counts = (
        df_filtre["regime"]
        .value_counts()
        .reset_index()
    )

    regime_counts.columns = [
        "Régime",
        "Nombre"
    ]

    fig_regime = px.bar(
        regime_counts,
        x="Régime",
        y="Nombre",
        text="Nombre",
        color="Régime"
    )

    st.plotly_chart(
        fig_regime,
        use_container_width=True
    )

    st.subheader("📊 Répartition des formes juridiques")

    df_filtre["forme_juridique"] = (
        df_filtre["forme_juridique"]
        .fillna("Non renseigné")
    )

    df_filtre = regrouper_entreprise_individuelle(
        df_filtre,
        "forme_juridique"
    )

    forme_counts = (
        df_filtre["forme_juridique"]
        .value_counts()
        .reset_index()
    )

    forme_counts.columns = [
        "Forme juridique",
        "Nombre"
    ]

    fig_forme = px.bar(
        forme_counts,
        x="Nombre",
        y="Forme juridique",
        text="Nombre",
        orientation="h",
        color="Nombre",
        color_continuous_scale="Blues"
    )

    st.plotly_chart(
        fig_forme,
        use_container_width=True
    )

# ===============================
# ANALYSE AVANCEE
# ===============================
elif page == "📊 Analyse avancée":

    show_main_title()

    st.title("📊 Analyse territoriale")

    query = """
    SELECT
        n.regime,
        n.activite_principale,
        c.nom AS commune,
        d.nom AS departement
    FROM ninea n
    JOIN commune c ON n.commune_id = c.id
    JOIN departement d ON c.departement_id = d.id
    """

    df = pd.read_sql(
        query,
        engine
    )

    # ===============================
    # CORRECTION FOUNDIOUGNE
    # ===============================
    df["departement"] = (
        df["departement"]
        .astype(str)
        .str.strip()
    )

    df["departement"] = df["departement"].replace({
        "Fondation": "Foundiougne",
        "FOUNDATION": "Foundiougne",
        "fondation": "Foundiougne",
        "FOUNDIOUGNE ": "Foundiougne",
        "foundiougne": "Foundiougne"
    })

    st.subheader("📍 Répartition par département")

    repart_dep = (
        df["departement"]
        .value_counts()
        .reset_index()
    )

    repart_dep.columns = [
        "Département",
        "Nombre"
    ]

    fig_dep = px.bar(
        repart_dep,
        x="Département",
        y="Nombre",
        text="Nombre",
        color="Département"
    )

    st.plotly_chart(
        fig_dep,
        use_container_width=True
    )

    departements = sorted(
        df["departement"].unique()
    )

    choix_dep = st.selectbox(
        "Choisir un département",
        departements
    )

    df_dep = df[
        df["departement"] == choix_dep
    ]

    st.metric(
        "Nombre total",
        df_dep.shape[0]
    )

    st.subheader("📍 Répartition par commune")

    repart_com = (
        df_dep["commune"]
        .value_counts()
        .reset_index()
    )

    repart_com.columns = [
        "Commune",
        "Nombre"
    ]

    fig_com = px.bar(
        repart_com,
        x="Commune",
        y="Nombre",
        text="Nombre",
        color="Commune"
    )

    st.plotly_chart(
        fig_com,
        use_container_width=True
    )

# ===============================
# ACTIVITE DOMINANTE
# ===============================
elif page == "📊 Activité dominante":

    show_main_title()

    st.title("📊 Activités dominantes")

    query = """
    SELECT
        n.activite_principale,
        c.nom AS commune,
        d.nom AS departement
    FROM ninea n
    JOIN commune c ON n.commune_id = c.id
    JOIN departement d ON c.departement_id = d.id
    """

    df = pd.read_sql(
        query,
        engine
    )

    # ===============================
    # CORRECTION FOUNDIOUGNE
    # ===============================
    df["departement"] = (
        df["departement"]
        .astype(str)
        .str.strip()
    )

    df["departement"] = df["departement"].replace({
        "Fondation": "Foundiougne",
        "FOUNDATION": "Foundiougne",
        "fondation": "Foundiougne",
        "FOUNDIOUGNE ": "Foundiougne",
        "foundiougne": "Foundiougne"
    })

    top = (
        df["activite_principale"]
        .value_counts()
        .head(4)
        .index
    )

    df_top = df[
        df["activite_principale"]
        .isin(top)
    ]

    dep_counts = (
        df_top.groupby(
            ["departement", "activite_principale"]
        )
        .size()
        .reset_index(name="Nombre")
    )

    fig = px.bar(
        dep_counts,
        x="departement",
        y="Nombre",
        color="activite_principale",
        barmode="group"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# ===============================
# EXPLORATION BASE
# ===============================
elif page == "🗄️ Exploration base":

    show_main_title()

    st.title("🗄️ Exploration base")

    tables = pd.read_sql(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        """,
        engine
    )

    table = st.selectbox(
        "Choisir une table",
        tables["table_name"]
    )

    if table:

        df = pd.read_sql(
            f"SELECT * FROM {table}",
            engine
        )

        st.success(
            f"Table {table} chargée ✅"
        )

        st.metric(
            "Nombre de lignes",
            df.shape[0]
        )

        st.dataframe(
            df.head(50),
            use_container_width=True
        )