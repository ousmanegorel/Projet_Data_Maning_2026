# ===============================
# app.py - Connexion PostgreSQL
# ===============================

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# -------------------------------
# Configuration de la page
# -------------------------------
st.set_page_config(
    page_title="Application NINEA",
    layout="wide"
)

st.title("📊 Application NINEA - ANSD FATICK")
st.write("Connexion à PostgreSQL...")

# -------------------------------
# Connexion PostgreSQL
# -------------------------------
try:
    engine = create_engine(
        "postgresql+psycopg2://postgres:ansdfatick@localhost:5432/ANSD_FATICK"
    )

    # -------------------------------
    # Charger les données
    # -------------------------------
    query = "SELECT * FROM ninea"
    df = pd.read_sql(query, engine)

    st.success("Connexion réussie à PostgreSQL ✅")

    # -------------------------------
    # Affichage
    # -------------------------------
    st.subheader("📄 Aperçu des données NINEA")
    st.dataframe(df.head())

    st.subheader("📊 Informations")
    st.write("Nombre de lignes :", df.shape[0])
    st.write("Nombre de colonnes :", df.shape[1])

except Exception as e:
    st.error("Erreur de connexion ❌")
    st.write(e)