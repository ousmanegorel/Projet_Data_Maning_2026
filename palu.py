# ===============================
# APPLICATION DE SUIVI DU PALUDISME - SÉNÉGAL
# ===============================

import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import os
import io
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from scipy import stats
from scipy.stats import shapiro, normaltest, kstest, poisson, chi2_contingency, f_oneway, kruskal, spearmanr, pearsonr
from statsmodels.formula.api import glm, ols
from statsmodels.genmod.families import Poisson, NegativeBinomial, Binomial
from statsmodels.genmod.generalized_linear_model import GLM
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import statsmodels.api as sm
import json
import urllib.request
warnings.filterwarnings('ignore')

# ===============================
# PAGE DE CONNEXION
# ===============================
PASSWORD = "ousmanesow555"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.set_page_config(page_title="Paludisme Sénégal - Connexion", page_icon="🦟", layout="wide")
    st.markdown("""
    <style>
        .login-container {
            max-width: 450px;
            margin: 0 auto;
            padding: 2rem 1.5rem;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            text-align: center;
            margin-top: 3rem;
        }
        .login-title {
            background: linear-gradient(135deg, #1a5276 0%, #2e86c1 100%);
            padding: 1.5rem;
            border-radius: 15px;
            margin-bottom: 1.5rem;
        }
        .login-title h1 { color: white; font-size: 1.8rem; margin: 0; }
        .login-title p { color: #e0e0e0; font-size: 0.95rem; margin: 0.3rem 0 0 0; }
        .login-subtitle { font-size: 1.05rem; color: #333; margin-bottom: 1.5rem; line-height: 1.6; }
        .login-subtitle strong { color: #1a5276; }
        .stButton button {
            background: linear-gradient(135deg, #1a5276 0%, #2e86c1 100%) !important;
            color: white !important;
            font-weight: bold !important;
            width: 100% !important;
            padding: 0.7rem !important;
            border-radius: 10px !important;
            border: none !important;
            font-size: 1.1rem !important;
        }
        .stButton button:hover { opacity: 0.9 !important; transform: scale(1.02); }
        .error-message { background-color: #f8d7da; color: #721c24; padding: 0.75rem; border-radius: 10px; margin-bottom: 1rem; font-size: 1rem; }
        .footer-login { text-align: center; color: #999; font-size: 0.85rem; margin-top: 1.5rem; }
        div[data-testid="stForm"] { border: none; padding: 0; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="login-container">
        <div class="login-title">
            <h1>🦟 SUI PALUDISME SÉNÉGAL</h1>
            <p>Plateforme de Suivi et d'Analyse des Données Paludisme</p>
        </div>
        <div class="login-subtitle">
            <strong>Suivi épidémiologique du paludisme au Sénégal</strong><br>
            Analyse des tendances, des cas confirmés et des indicateurs clés
        </div>
    """, unsafe_allow_html=True)
    with st.form(key="login_form", clear_on_submit=False):
        password_input = st.text_input("Mot de passe", type="password", placeholder="Entrez le mot de passe")
        submit_button = st.form_submit_button("Connexion")
        if submit_button:
            if password_input == PASSWORD:
                st.session_state.authenticated = True
                st.success("Connexion réussie ! Redirection en cours...")
                st.rerun()
            else:
                st.markdown('<div class="error-message">Mot de passe incorrect. Veuillez réessayer.</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="footer-login">© 2026 - Programme National de Lutte contre le Paludisme | Sénégal</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ===============================
# CONFIGURATION PRINCIPALE
# ===============================
st.set_page_config(page_title="Suivi Paludisme Sénégal", page_icon="🦟", layout="wide")

st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .main-title {
        background: linear-gradient(135deg, #1a5276 0%, #2e86c1 100%);
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .main-title h1 { color: white; font-size: 1.8rem; margin: 0; }
    .main-title p { color: #e0e0e0; margin: 0; font-size: 0.9rem; }
    h1, h2, h3 { color: #1a5276; font-weight: bold; }
    
    .hero-container {
        background: linear-gradient(135deg, #1a5276 0%, #2e86c1 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .hero-title { font-size: 2.5rem; font-weight: bold; color: white; margin-bottom: 0.5rem; }
    .hero-subtitle { font-size: 1.2rem; color: #f0f0f0; }
    .hero-description { font-size: 1rem; color: #e0e0e0; margin-top: 1rem; }
    
    .drs-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        transition: transform 0.3s;
    }
    .drs-card:hover { transform: translateY(-5px); }
    .drs-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .drs-name { font-weight: bold; color: white; font-size: 0.9rem; }
    
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
    .info-title { font-size: 1.1rem; font-weight: bold; color: #1a5276; margin-bottom: 0.5rem; }
    .info-text { color: #666; font-size: 0.85rem; }
    
    .mission-container {
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
    .mission-text strong {
        color: #1a5276;
    }
    
    footer { text-align: center; padding: 2rem; color: #666; margin-top: 3rem; border-top: 1px solid #ddd; }
    .success-message { background-color: #d4edda; color: #155724; padding: 1rem; border-radius: 10px; margin: 1rem 0; }
    .warning-message { background-color: #fff3cd; color: #856404; padding: 1rem; border-radius: 10px; margin: 1rem 0; }
    .stButton button { width: 100%; }
    div[data-testid="stForm"] { border: none; padding: 0; }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f0f4f8 0%, #d9e2ec 100%);
        padding-top: 0.5rem;
    }
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] {
        gap: 2px !important;
        padding: 4px 8px !important;
    }
    [data-testid="stSidebar"] .stRadio [role="radio"] {
        padding: 2px 6px !important;
        margin: 1px 0 !important;
        border-radius: 8px !important;
        border: none !important;
        background: transparent !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        padding: 6px 10px !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #1a5276 !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(26, 82, 118, 0.08) !important;
    }
    [data-testid="stSidebar"] .stRadio [role="radio"][aria-checked="true"] {
        background: linear-gradient(135deg, #1a5276 0%, #2e86c1 100%) !important;
        box-shadow: 0 2px 10px rgba(26, 82, 118, 0.3) !important;
    }
    [data-testid="stSidebar"] .stRadio [role="radio"][aria-checked="true"] label {
        color: white !important;
    }
    [data-testid="stSidebar"] .stRadio [role="radio"][aria-checked="true"] label:hover {
        background: transparent !important;
    }
    [data-testid="stSidebar"] .sidebar-title {
        font-size: 1.1rem !important;
        color: #1a5276;
        font-weight: bold;
        margin-bottom: 0.3rem !important;
        padding-left: 8px;
    }
    [data-testid="stSidebar"] .stButton button {
        font-size: 0.95rem !important;
        font-weight: bold !important;
        padding: 0.5rem !important;
        border-radius: 8px !important;
        background: linear-gradient(135deg, #1a5276 0%, #2e86c1 100%) !important;
        color: white !important;
        border: none !important;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        opacity: 0.9 !important;
        transform: scale(1.02);
    }
    .quality-header {
        background: linear-gradient(135deg, #1a5276 0%, #2e86c1 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .quality-score {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .quality-good { 
        color: #155724; 
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    .quality-medium { 
        color: #856404; 
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
    }
    .quality-bad { 
        color: #721c24; 
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
    }
    .stat-header {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .model-box {
        background: linear-gradient(135deg, #e8f4f8 0%, #f0f8ff 100%);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #1a5276;
        margin: 1rem 0;
    }
    .dispersion-ok {
        background-color: #d4edda;
        border-left: 5px solid #27ae60;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .dispersion-warning {
        background-color: #fff3cd;
        border-left: 5px solid #f39c12;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .model-comparison {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #1a5276;
        margin: 1rem 0;
    }
    .conclusion-box {
        background: linear-gradient(135deg, #1a5276 0%, #2e86c1 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    .conclusion-box h3 { color: white; margin-top: 0; }
    .conclusion-box p { color: #f0f0f0; line-height: 1.6; }
    .variable-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #3498db;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .variable-signif {
        border-left-color: #27ae60;
        background-color: #f0fff4;
    }
    .variable-non-signif {
        border-left-color: #e74c3c;
        background-color: #fff5f5;
    }
    .test-result-box {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 5px solid #3498db;
        margin: 0.8rem 0;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }
    .test-signif {
        border-left-color: #27ae60;
        background: #f0fff4;
    }
    .test-non-signif {
        border-left-color: #e74c3c;
        background: #fff5f5;
    }
    .test-header-section {
        background: linear-gradient(135deg, #16a085 0%, #1abc9c 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def show_main_title():
    st.markdown("""
    <div class="main-title">
        <h1>🦟 Plateforme de Suivi du Paludisme - Sénégal</h1>
        <p>Programme National de Lutte contre le Paludisme | Données épidémiologiques</p>
    </div>
    """, unsafe_allow_html=True)

# ===============================
# DONNÉES INTÉGRÉES
# ===============================
def get_drs_data():
    drs_list = ['DAKAR', 'DIOURBEL', 'FATICK', 'KAFFRINE', 'KAOLLACK', 'KEDOUGOU', 'KOLDA',
                'LOUGA', 'MATAM', 'SAINT_LOUIS', 'SEDHIOU', 'TAMBACOUNDA', 'THIES', 'ZIGUINCHOR']
    return drs_list

# ===============================
# BASE DE DONNÉES SQLITE
# ===============================
DB_PATH = 'paludisme.db'

def init_paludisme_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collecte_paludisme (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            DRS TEXT NOT NULL,
            ANNEE INTEGER NOT NULL,
            Mois TEXT NOT NULL,
            Consultations INTEGER DEFAULT 0,
            Cas_suspects INTEGER DEFAULT 0,
            Tests_realises INTEGER DEFAULT 0,
            Cas_confirmes INTEGER DEFAULT 0,
            Taux_positivite REAL DEFAULT 0,
            Traitement_approprié INTEGER DEFAULT 0,
            Taux_traitement REAL DEFAULT 0,
            GE_realises INTEGER DEFAULT 0,
            GE_positifs INTEGER DEFAULT 0,
            Taux_positivite_GE REAL DEFAULT 0,
            Hospitalisations INTEGER DEFAULT 0,
            Hospitalisations_traitees INTEGER DEFAULT 0,
            TDR_realises INTEGER DEFAULT 0,
            TDR_positifs INTEGER DEFAULT 0,
            Taux_positivite_TDR REAL DEFAULT 0,
            Deces INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def verify_and_repair_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='collecte_paludisme'")
        table_exists = cursor.fetchone()
        if not table_exists:
            cursor.execute('''
                CREATE TABLE collecte_paludisme (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    DRS TEXT NOT NULL,
                    ANNEE INTEGER NOT NULL,
                    Mois TEXT NOT NULL,
                    Consultations INTEGER DEFAULT 0,
                    Cas_suspects INTEGER DEFAULT 0,
                    Tests_realises INTEGER DEFAULT 0,
                    Cas_confirmes INTEGER DEFAULT 0,
                    Taux_positivite REAL DEFAULT 0,
                    Traitement_approprié INTEGER DEFAULT 0,
                    Taux_traitement REAL DEFAULT 0,
                    GE_realises INTEGER DEFAULT 0,
                    GE_positifs INTEGER DEFAULT 0,
                    Taux_positivite_GE REAL DEFAULT 0,
                    Hospitalisations INTEGER DEFAULT 0,
                    Hospitalisations_traitees INTEGER DEFAULT 0,
                    TDR_realises INTEGER DEFAULT 0,
                    TDR_positifs INTEGER DEFAULT 0,
                    Taux_positivite_TDR REAL DEFAULT 0,
                    Deces INTEGER DEFAULT 0
                )
            ''')
            conn.commit()
        conn.close()
        return True
    except Exception:
        return False

def insert_paludisme(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO collecte_paludisme (
            DRS, ANNEE, Mois, Consultations, Cas_suspects, Tests_realises,
            Cas_confirmes, Taux_positivite, Traitement_approprié, Taux_traitement,
            GE_realises, GE_positifs, Taux_positivite_GE,
            Hospitalisations, Hospitalisations_traitees,
            TDR_realises, TDR_positifs, Taux_positivite_TDR, Deces
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()
    conn.close()

def get_all_paludisme_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM collecte_paludisme ORDER BY id DESC", conn)
    conn.close()
    return df

def delete_all_paludisme():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM collecte_paludisme")
    conn.commit()
    conn.close()

def delete_paludisme_by_id(id_record):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM collecte_paludisme WHERE id = ?", (id_record,))
    conn.commit()
    conn.close()

def update_paludisme(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE collecte_paludisme SET
            DRS = ?, ANNEE = ?, Mois = ?,
            Consultations = ?, Cas_suspects = ?, Tests_realises = ?,
            Cas_confirmes = ?, Taux_positivite = ?, Traitement_approprié = ?,
            Taux_traitement = ?, GE_realises = ?, GE_positifs = ?,
            Taux_positivite_GE = ?, Hospitalisations = ?,
            Hospitalisations_traitees = ?, TDR_realises = ?,
            TDR_positifs = ?, Taux_positivite_TDR = ?, Deces = ?
        WHERE id = ?
    ''', data)
    conn.commit()
    conn.close()

def replace_all_paludisme(df):
    delete_all_paludisme()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    inserted = 0
    errors = 0
    
    for _, row in df.iterrows():
        try:
            cursor.execute('''
                INSERT INTO collecte_paludisme (
                    DRS, ANNEE, Mois, Consultations, Cas_suspects, Tests_realises,
                    Cas_confirmes, Taux_positivite, Traitement_approprié, Taux_traitement,
                    GE_realises, GE_positifs, Taux_positivite_GE,
                    Hospitalisations, Hospitalisations_traitees,
                    TDR_realises, TDR_positifs, Taux_positivite_TDR, Deces
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['DRS'] if pd.notna(row['DRS']) else 'INCONNU',
                int(row['ANNEE']) if pd.notna(row['ANNEE']) else None,
                row['Mois'] if pd.notna(row['Mois']) else 'INCONNU',
                int(row['Consultations']) if pd.notna(row['Consultations']) else None,
                int(row['Cas_suspects']) if pd.notna(row['Cas_suspects']) else None,
                int(row['Tests_realises']) if pd.notna(row['Tests_realises']) else None,
                int(row['Cas_confirmes']) if pd.notna(row['Cas_confirmes']) else None,
                float(row['Taux_positivite']) if pd.notna(row['Taux_positivite']) else None,
                int(row['Traitement_approprié']) if pd.notna(row['Traitement_approprié']) else None,
                float(row['Taux_traitement']) if pd.notna(row['Taux_traitement']) else None,
                int(row['GE_realises']) if pd.notna(row['GE_realises']) else None,
                int(row['GE_positifs']) if pd.notna(row['GE_positifs']) else None,
                float(row['Taux_positivite_GE']) if pd.notna(row['Taux_positivite_GE']) else None,
                int(row['Hospitalisations']) if pd.notna(row['Hospitalisations']) else None,
                int(row['Hospitalisations_traitees']) if pd.notna(row['Hospitalisations_traitees']) else None,
                int(row['TDR_realises']) if pd.notna(row['TDR_realises']) else None,
                int(row['TDR_positifs']) if pd.notna(row['TDR_positifs']) else None,
                float(row['Taux_positivite_TDR']) if pd.notna(row['Taux_positivite_TDR']) else None,
                int(row['Deces']) if pd.notna(row['Deces']) else None
            ))
            inserted += 1
        except Exception as e:
            errors += 1
            print(f"Erreur ligne {_}: {e}")
    
    conn.commit()
    conn.close()
    return inserted, errors

# ===============================
# STANDARDISATION DES NOMS DE COLONNES
# ===============================
def standardize_column_names(df):
    df.columns = df.columns.str.strip()
    
    column_mapping = {
        'DRS': 'DRS', 'drs': 'DRS',
        'Annes': 'ANNEE', 'ANNEE': 'ANNEE', 'Annee': 'ANNEE', 'annee': 'ANNEE',
        'Année': 'ANNEE', 'Années': 'ANNEE',
        'Mois': 'Mois', 'mois': 'Mois',
        'Consultations': 'Consultations', 'consultations': 'Consultations',
        'Consultation': 'Consultations', 'CONSULTATIONS': 'Consultations',
        'Cas_suspects': 'Cas_suspects', 'Cas suspects': 'Cas_suspects',
        'cas_suspects': 'Cas_suspects', 'CAS_SUSPECTS': 'Cas_suspects',
        'Tests_réalisés': 'Tests_realises', 'Tests_realises': 'Tests_realises',
        'Tests réalisés': 'Tests_realises', 'tests_realises': 'Tests_realises',
        'TESTS_REALISES': 'Tests_realises',
        'Cas_confirmes': 'Cas_confirmes', 'Cas confirmés': 'Cas_confirmes',
        'cas_confirmes': 'Cas_confirmes', 'Cas_confirmés': 'Cas_confirmes',
        'CAS_CONFIRMES': 'Cas_confirmes',
        'Taux_Positivite': 'Taux_positivite', 'Taux_positivite': 'Taux_positivite',
        'Taux Positivité': 'Taux_positivite', 'taux_positivite': 'Taux_positivite',
        'Taux Positif': 'Taux_positivite', 'TAUX_POSITIVITE': 'Taux_positivite',
        'Traitement_approprié': 'Traitement_approprié',
        'Traitement approprié': 'Traitement_approprié',
        'traitement_approprié': 'Traitement_approprié',
        'TRAITEMENT_APPROPRIE': 'Traitement_approprié',
        'Taux_traitement': 'Taux_traitement', 'Taux traitement': 'Taux_traitement',
        'taux_traitement': 'Taux_traitement', 'TAUX_TRAITEMENT': 'Taux_traitement',
        'GE_realises': 'GE_realises', 'GE réalisés': 'GE_realises',
        'ge_realises': 'GE_realises', 'GE_REALISES': 'GE_realises',
        'GE_positifs': 'GE_positifs', 'GE positifs': 'GE_positifs',
        'ge_positifs': 'GE_positifs', 'GE_POSITIFS': 'GE_positifs',
        'Taux_Positivite_GE': 'Taux_positivite_GE',
        'Taux_positivite_GE': 'Taux_positivite_GE',
        'Taux Positivité GE': 'Taux_positivite_GE',
        'taux_positivite_ge': 'Taux_positivite_GE',
        'TAUX_POSITIVITE_GE': 'Taux_positivite_GE',
        'Hospitalisations': 'Hospitalisations', 'hospitalisations': 'Hospitalisations',
        'HOSPITALISATIONS': 'Hospitalisations',
        'Hospitalisations_traitees': 'Hospitalisations_traitees',
        'Hospitalisations traitées': 'Hospitalisations_traitees',
        'hospitalisations_traitees': 'Hospitalisations_traitees',
        'Hospitalisations_traitées': 'Hospitalisations_traitees',
        'HOSPITALISATIONS_TRAITEES': 'Hospitalisations_traitees',
        'TDR_realisees': 'TDR_realises', 'TDR_realises': 'TDR_realises',
        'TDR réalisées': 'TDR_realises', 'tdr_realises': 'TDR_realises',
        'TDR_REALISEES': 'TDR_realises', 'TDR_REALISES': 'TDR_realises',
        'TDR_positifs': 'TDR_positifs', 'TDR positifs': 'TDR_positifs',
        'tdr_positifs': 'TDR_positifs', 'TDR_POSITIFS': 'TDR_positifs',
        'Taux_Positivite_TDR': 'Taux_positivite_TDR',
        'Taux_positivite_TDR': 'Taux_positivite_TDR',
        'Taux Positivité TDR': 'Taux_positivite_TDR',
        'taux_positivite_tdr': 'Taux_positivite_TDR',
        'TAUX_POSITIVITE_TDR': 'Taux_positivite_TDR',
        'Deces': 'Deces', 'Décès': 'Deces', 'deces': 'Deces', 'DECES': 'Deces'
    }
    
    df_renamed = df.rename(columns=column_mapping)
    
    required_cols = ['DRS', 'ANNEE', 'Mois', 'Consultations', 'Cas_suspects', 'Tests_realises',
                     'Cas_confirmes', 'Taux_positivite', 'Traitement_approprié', 'Taux_traitement',
                     'GE_realises', 'GE_positifs', 'Taux_positivite_GE', 'Hospitalisations',
                     'Hospitalisations_traitees', 'TDR_realises', 'TDR_positifs', 
                     'Taux_positivite_TDR', 'Deces']
    
    for col in required_cols:
        if col not in df_renamed.columns:
            df_renamed[col] = None
    
    return df_renamed

def convert_decimal_comma(df):
    for col in df.columns:
        if df[col].dtype == 'object':
            sample = df[col].dropna()
            if len(sample) > 0:
                if sample.astype(str).str.contains(',').any():
                    try:
                        df[col] = df[col].astype(str).str.replace(',', '.').str.replace(' ', '')
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    except:
                        pass
    return df

# ===============================
# FONCTIONS QUALITÉ DES DONNÉES
# ===============================
def check_quality_rules(df):
    errors = []
    warnings_list = []
    
    if 'Cas_confirmes' in df.columns and 'Cas_suspects' in df.columns:
        mask = df['Cas_confirmes'].notna() & df['Cas_suspects'].notna()
        temp_df = df[mask]
        invalid = temp_df[temp_df['Cas_confirmes'] > temp_df['Cas_suspects']]
        if not invalid.empty:
            errors.append({
                'regle': 'Cas confirmés > Cas suspects',
                'nombre': len(invalid),
                'details': invalid[['DRS', 'ANNEE', 'Mois', 'Cas_suspects', 'Cas_confirmes']].head(10).to_dict('records')
            })
    
    if 'Tests_realises' in df.columns and 'Cas_suspects' in df.columns:
        mask = df['Tests_realises'].notna() & df['Cas_suspects'].notna()
        temp_df = df[mask]
        invalid = temp_df[temp_df['Tests_realises'] > temp_df['Cas_suspects']]
        if not invalid.empty:
            errors.append({
                'regle': 'Tests réalisés > Cas suspects',
                'nombre': len(invalid),
                'details': invalid[['DRS', 'ANNEE', 'Mois', 'Cas_suspects', 'Tests_realises']].head(10).to_dict('records')
            })
    
    if 'Tests_realises' in df.columns and 'Cas_confirmes' in df.columns:
        mask = df['Tests_realises'].notna() & df['Cas_confirmes'].notna()
        temp_df = df[mask]
        invalid = temp_df[temp_df['Tests_realises'] < temp_df['Cas_confirmes']]
        if not invalid.empty:
            errors.append({
                'regle': 'Tests réalisés < Cas confirmés',
                'nombre': len(invalid),
                'details': invalid[['DRS', 'ANNEE', 'Mois', 'Tests_realises', 'Cas_confirmes']].head(10).to_dict('records')
            })
    
    if 'Deces' in df.columns and 'Cas_confirmes' in df.columns:
        mask = df['Deces'].notna() & df['Cas_confirmes'].notna()
        temp_df = df[mask]
        invalid = temp_df[temp_df['Deces'] > temp_df['Cas_confirmes']]
        if not invalid.empty:
            errors.append({
                'regle': 'Décès > Cas confirmés',
                'nombre': len(invalid),
                'details': invalid[['DRS', 'ANNEE', 'Mois', 'Deces', 'Cas_confirmes']].head(10).to_dict('records')
            })
    
    if 'Traitement_approprié' in df.columns and 'Cas_confirmes' in df.columns:
        mask = df['Traitement_approprié'].notna() & df['Cas_confirmes'].notna()
        temp_df = df[mask]
        invalid = temp_df[temp_df['Traitement_approprié'] > temp_df['Cas_confirmes']]
        if not invalid.empty:
            errors.append({
                'regle': 'Traitement approprié > Cas confirmés',
                'nombre': len(invalid),
                'details': invalid[['DRS', 'ANNEE', 'Mois', 'Cas_confirmes', 'Traitement_approprié']].head(10).to_dict('records')
            })
    
    if 'Taux_positivite' in df.columns:
        mask = df['Taux_positivite'].notna()
        temp_df = df[mask]
        invalid = temp_df[(temp_df['Taux_positivite'] > 100) | (temp_df['Taux_positivite'] < 0)]
        if not invalid.empty:
            errors.append({
                'regle': 'Taux de positivité hors intervalle [0-100]',
                'nombre': len(invalid),
                'details': invalid[['DRS', 'ANNEE', 'Mois', 'Taux_positivite']].head(10).to_dict('records')
            })
    
    if 'Taux_traitement' in df.columns:
        mask = df['Taux_traitement'].notna()
        temp_df = df[mask]
        invalid = temp_df[(temp_df['Taux_traitement'] > 100) | (temp_df['Taux_traitement'] < 0)]
        if not invalid.empty:
            errors.append({
                'regle': 'Taux de traitement hors intervalle [0-100]',
                'nombre': len(invalid),
                'details': invalid[['DRS', 'ANNEE', 'Mois', 'Taux_traitement']].head(10).to_dict('records')
            })
    
    if 'Taux_positivite_GE' in df.columns:
        mask = df['Taux_positivite_GE'].notna()
        temp_df = df[mask]
        invalid = temp_df[(temp_df['Taux_positivite_GE'] > 100) | (temp_df['Taux_positivite_GE'] < 0)]
        if not invalid.empty:
            errors.append({
                'regle': 'Taux de positivité GE hors intervalle [0-100]',
                'nombre': len(invalid),
                'details': invalid[['DRS', 'ANNEE', 'Mois', 'Taux_positivite_GE']].head(10).to_dict('records')
            })
    
    if 'Taux_positivite_TDR' in df.columns:
        mask = df['Taux_positivite_TDR'].notna()
        temp_df = df[mask]
        invalid = temp_df[(temp_df['Taux_positivite_TDR'] > 100) | (temp_df['Taux_positivite_TDR'] < 0)]
        if not invalid.empty:
            errors.append({
                'regle': 'Taux de positivité TDR hors intervalle [0-100]',
                'nombre': len(invalid),
                'details': invalid[['DRS', 'ANNEE', 'Mois', 'Taux_positivite_TDR']].head(10).to_dict('records')
            })
    
    if 'Hospitalisations_traitees' in df.columns and 'Hospitalisations' in df.columns:
        mask = df['Hospitalisations_traitees'].notna() & df['Hospitalisations'].notna()
        temp_df = df[mask]
        invalid = temp_df[temp_df['Hospitalisations_traitees'] > temp_df['Hospitalisations']]
        if not invalid.empty:
            errors.append({
                'regle': 'Hospitalisations traitées > Hospitalisations',
                'nombre': len(invalid),
                'details': invalid[['DRS', 'ANNEE', 'Mois', 'Hospitalisations', 'Hospitalisations_traitees']].head(10).to_dict('records')
            })
    
    if 'Deces' in df.columns and 'Hospitalisations' in df.columns:
        mask = df['Deces'].notna() & df['Hospitalisations'].notna()
        temp_df = df[mask]
        invalid = temp_df[temp_df['Deces'] > temp_df['Hospitalisations']]
        if not invalid.empty:
            errors.append({
                'regle': 'Décès > Hospitalisations',
                'nombre': len(invalid),
                'details': invalid[['DRS', 'ANNEE', 'Mois', 'Deces', 'Hospitalisations']].head(10).to_dict('records')
            })
    
    if 'GE_positifs' in df.columns and 'GE_realises' in df.columns:
        mask = df['GE_positifs'].notna() & df['GE_realises'].notna()
        temp_df = df[mask]
        invalid = temp_df[temp_df['GE_positifs'] > temp_df['GE_realises']]
        if not invalid.empty:
            errors.append({
                'regle': 'GE positifs > GE réalisés',
                'nombre': len(invalid),
                'details': invalid[['DRS', 'ANNEE', 'Mois', 'GE_realises', 'GE_positifs']].head(10).to_dict('records')
            })
    
    if 'TDR_positifs' in df.columns and 'TDR_realises' in df.columns:
        mask = df['TDR_positifs'].notna() & df['TDR_realises'].notna()
        temp_df = df[mask]
        invalid = temp_df[temp_df['TDR_positifs'] > temp_df['TDR_realises']]
        if not invalid.empty:
            errors.append({
                'regle': 'TDR positifs > TDR réalisés',
                'nombre': len(invalid),
                'details': invalid[['DRS', 'ANNEE', 'Mois', 'TDR_realises', 'TDR_positifs']].head(10).to_dict('records')
            })
    
    numeric_cols = ['Consultations', 'Cas_suspects', 'Tests_realises', 'Cas_confirmes', 
                    'Traitement_approprié', 'Hospitalisations', 'TDR_realises', 'TDR_positifs', 'Deces']
    for col in numeric_cols:
        if col in df.columns:
            mask = df[col].notna()
            temp_df = df[mask]
            invalid = temp_df[temp_df[col] < 0]
            if not invalid.empty:
                errors.append({
                    'regle': f'Valeurs négatives dans {col}',
                    'nombre': len(invalid),
                    'details': invalid[['DRS', 'ANNEE', 'Mois', col]].head(10).to_dict('records')
                })
    
    return errors, warnings_list

def detect_outliers_iqr(df, column):
    if column not in df.columns:
        return pd.DataFrame()
    data = df[column].dropna()
    if len(data) < 4:
        return pd.DataFrame()
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    return outliers[['DRS', 'ANNEE', 'Mois', column]].copy()

def detect_outliers_zscore(df, column, threshold=3):
    if column not in df.columns:
        return pd.DataFrame()
    data = df[column].dropna()
    if len(data) < 4:
        return pd.DataFrame()
    mean = data.mean()
    std = data.std()
    if std == 0:
        return pd.DataFrame()
    z_scores = np.abs((df[column] - mean) / std)
    outliers = df[z_scores > threshold]
    return outliers[['DRS', 'ANNEE', 'Mois', column]].copy()

def detect_anomalies_isolation_forest(df, columns):
    if len(df) < 10:
        return pd.DataFrame()
    data = df[columns].copy()
    for col in columns:
        data[col] = data[col].fillna(data[col].median())
    scaler = (data - data.mean()) / data.std()
    scaler = scaler.fillna(0)
    iso_forest = IsolationForest(contamination=0.1, random_state=42)
    predictions = iso_forest.fit_predict(scaler)
    anomalies = df[predictions == -1]
    return anomalies[['DRS', 'ANNEE', 'Mois'] + columns].copy()

def detect_anomalies_lof(df, columns):
    if len(df) < 20:
        return pd.DataFrame()
    data = df[columns].copy()
    for col in columns:
        data[col] = data[col].fillna(data[col].median())
    scaler = (data - data.mean()) / data.std()
    scaler = scaler.fillna(0)
    lof = LocalOutlierFactor(contamination=0.1, novelty=False)
    predictions = lof.fit_predict(scaler)
    anomalies = df[predictions == -1]
    return anomalies[['DRS', 'ANNEE', 'Mois'] + columns].copy()

def calculate_completeness(df):
    completeness = {}
    for col in df.columns:
        if col == 'id':
            continue
        total = len(df)
        non_null = df[col].notna().sum()
        completeness[col] = (non_null / total * 100) if total > 0 else 0
    return completeness

def calculate_drs_score(df_quality):
    scores = []
    
    numeric_cols = ['Consultations', 'Cas_suspects', 'Tests_realises', 'Cas_confirmes', 
                    'Taux_positivite', 'Traitement_approprié', 'Taux_traitement',
                    'GE_realises', 'GE_positifs', 'Taux_positivite_GE',
                    'Hospitalisations', 'Hospitalisations_traitees',
                    'TDR_realises', 'TDR_positifs', 'Taux_positivite_TDR', 'Deces']
    
    for drs in sorted(df_quality['DRS'].unique()):
        drs_data = df_quality[df_quality['DRS'] == drs]
        
        completude_values = []
        for col in numeric_cols:
            if col in drs_data.columns:
                taux = (drs_data[col].notna().sum() / len(drs_data)) * 100
                completude_values.append(taux)
        
        completude = sum(completude_values) / len(completude_values) if completude_values else 0
        score_A = completude * 0.70
        
        errors_drs, _ = check_quality_rules(drs_data)
        nb_erreurs = sum(err['nombre'] for err in errors_drs)
        
        if nb_erreurs <= 10:
            score_B = 30
        elif nb_erreurs <= 50:
            score_B = 25
        elif nb_erreurs <= 100:
            score_B = 10
        else:
            score_B = 0
        
        score_C = score_A + score_B
        
        scores.append({
            'DRS': drs,
            'Complétude T1 2026 (%)': round(completude, 2),
            'Nb. erreurs': nb_erreurs,
            'Score corrigé C': round(score_C, 2),
            '_score_C_raw': score_C
        })
    
    df_scores = pd.DataFrame(scores)
    df_scores['Rang'] = df_scores['_score_C_raw'].rank(ascending=False, method='min').astype(int)
    df_scores = df_scores.sort_values('Rang').reset_index(drop=True)
    
    return df_scores

# Initialiser la base
init_paludisme_db()
verify_and_repair_db()

# ===============================
# SESSION STATE
# ===============================
if 'confirm_delete_paludisme' not in st.session_state:
    st.session_state.confirm_delete_paludisme = False
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None

# ===============================
# MENU
# ===============================
st.sidebar.markdown('<div class="sidebar-title">📂 Navigation</div>', unsafe_allow_html=True)
page = st.sidebar.radio(
    "",
    [
        "🏠 Accueil",
        "📝 Saisie des données",
        "🔍 Qualité des données",
        "📊 Visualisation",
        "📈 Modélisation Statistique"
    ]
)
if st.sidebar.button("🔄 Rafraîchir", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

drs_list = get_drs_data()

# ===============================
# PAGE ACCUEIL
# ===============================
if page == "🏠 Accueil":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🦟 Suivi du Paludisme - Sénégal</div>
        <div class="hero-subtitle">Programme National de Lutte contre le Paludisme</div>
        <div class="hero-description">
            Production, analyse et diffusion des données épidémiologiques pour le contrôle du paludisme au Sénégal
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    df_stats = get_all_paludisme_data()
    if not df_stats.empty:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📋 Total enregistrements", len(df_stats))
        with col2:
            st.metric("🏥 DRS couverts", df_stats['DRS'].nunique())
        with col3:
            st.metric("🦟 Cas confirmés", f"{df_stats['Cas_confirmes'].sum():,}")
        with col4:
            st.metric("💀 Décès", df_stats['Deces'].sum())
    
    st.markdown("### 🎯 Notre Mission")
    st.markdown("""
    <div class="mission-container">
        <div class="mission-text">
            Le Programme National de Lutte contre le Paludisme (PNLP) a pour mission de <strong>collecter, traiter, analyser et diffuser</strong> 
            les données épidémiologiques du paludisme dans l'ensemble des districts sanitaires du Sénégal.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🏥 DRS couverts (14 Directions Régionales de la Santé)")
    
    drs_icons = [
        ("🏙️", "DAKAR"), ("🏛️", "DIOURBEL"), ("🌾", "FATICK"), ("🌿", "KAFFRINE"),
        ("🌊", "KAOLLACK"), ("🌳", "KEDOUGOU"), ("🏗️", "KOLDA"), ("🌴", "LOUGA"),
        ("🏜️", "MATAM"), ("🌊", "SAINT-LOUIS"), ("🌾", "SEDHIOU"), ("🌳", "TAMBACOUNDA"),
        ("🏙️", "THIES"), ("🌴", "ZIGUINCHOR")
    ]
    
    cols = st.columns(5)
    for i, (icon, title) in enumerate(drs_icons):
        with cols[i % 5]:
            st.markdown(f"""
            <div class="drs-card">
                <div class="drs-icon">{icon}</div>
                <div class="drs-name">{title}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🎯 Nos Objectifs Stratégiques")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="info-card">
            <div class="info-icon">📈</div>
            <div class="info-title">Aide à la décision</div>
            <div class="info-text">Fournir des données fiables aux autorités sanitaires pour la lutte contre le paludisme</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="info-card">
            <div class="info-icon">📢</div>
            <div class="info-title">Diffusion de l'information</div>
            <div class="info-text">Données épidémiologiques accessibles à tous les acteurs de la lutte</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="info-card">
            <div class="info-icon">🔬</div>
            <div class="info-title">Recherche & Études</div>
            <div class="info-text">Analyses approfondies des tendances et indicateurs du paludisme</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="info-card">
            <div class="info-icon">🤝</div>
            <div class="info-title">Partenariat</div>
            <div class="info-text">Collaboration avec les partenaires du programme national</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <footer>
        <p><strong>Programme National de Lutte contre le Paludisme (PNLP)</strong></p>
        <p>© 2026 - Ministère de la Santé | Sénégal</p>
    </footer>
    """, unsafe_allow_html=True)

# ===============================
# PAGE SAISIE DES DONNÉES
# ===============================
elif page == "📝 Saisie des données":
    show_main_title()
    st.title("📝 Saisie des données - Formulaire de collecte")
    
    with st.form(key="formulaire_collecte", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            drs = st.selectbox("DRS *", sorted(drs_list))
        with col2:
            annee = st.selectbox("Année *", [2025, 2026])
        with col3:
            mois = st.selectbox("Mois *", ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                                           'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            consultations = st.number_input("Consultations", min_value=0, step=1, value=0)
        with col2:
            cas_suspects = st.number_input("Cas suspects", min_value=0, step=1, value=0)
        with col3:
            tests_realises = st.number_input("Tests réalisés", min_value=0, step=1, value=0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            cas_confirmes = st.number_input("Cas confirmés", min_value=0, step=1, value=0)
        with col2:
            taux_positivite = st.number_input("Taux positivité (%)", min_value=0.0, step=0.01, value=0.0, format="%.2f")
        with col3:
            traitement_approprié = st.number_input("Traitement approprié", min_value=0, step=1, value=0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            taux_traitement = st.number_input("Taux traitement (%)", min_value=0.0, step=0.01, value=0.0, format="%.2f")
        with col2:
            ge_realises = st.number_input("GE réalisés", min_value=0, step=1, value=0)
        with col3:
            ge_positifs = st.number_input("GE positifs", min_value=0, step=1, value=0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            taux_positivite_ge = st.number_input("Taux positivité GE (%)", min_value=0.0, step=0.01, value=0.0, format="%.2f")
        with col2:
            hospitalisations = st.number_input("Hospitalisations", min_value=0, step=1, value=0)
        with col3:
            hospitalisations_traitees = st.number_input("Hospitalisations traitées", min_value=0, step=1, value=0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            tdr_realises = st.number_input("TDR réalisés", min_value=0, step=1, value=0)
        with col2:
            tdr_positifs = st.number_input("TDR positifs", min_value=0, step=1, value=0)
        with col3:
            taux_positivite_tdr = st.number_input("Taux positivité TDR (%)", min_value=0.0, step=0.01, value=0.0, format="%.2f")
        
        deces = st.number_input("Décès", min_value=0, step=1, value=0)
        
        submitted = st.form_submit_button("✅ Enregistrer", use_container_width=True)
        
        if submitted:
            if not drs or not mois:
                st.error("❌ Veuillez remplir DRS, Année et Mois")
            else:
                data = (
                    drs, annee, mois, 
                    consultations, cas_suspects, tests_realises,
                    cas_confirmes, taux_positivite, traitement_approprié,
                    taux_traitement, ge_realises, ge_positifs,
                    taux_positivite_ge, hospitalisations, hospitalisations_traitees,
                    tdr_realises, tdr_positifs, taux_positivite_tdr, deces
                )
                
                try:
                    insert_paludisme(data)
                    st.markdown(f'<div class="success-message">✅ Données enregistrées - {drs}</div>', unsafe_allow_html=True)
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")
    
    st.markdown("---")
    st.markdown("### 📊 Données collectées")
    
    df_collecte = get_all_paludisme_data()
    
    if df_collecte.empty:
        st.info("ℹ️ Aucune donnée collectée")
    else:
        nb_total = len(df_collecte)
        nb_colonnes = len(df_collecte.columns)
        
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        col_stats1.metric("📋 Total", nb_total)
        col_stats2.metric("🏥 DRS", df_collecte['DRS'].nunique())
        col_stats3.metric("📊 Colonnes", nb_colonnes)
        
        st.dataframe(df_collecte, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### ✏️ Modifier / Supprimer")
    
    if not df_collecte.empty:
        col_edit1, col_edit2 = st.columns(2)
        
        with col_edit1:
            id_a_modifier = st.number_input("ID à modifier", min_value=1, step=1, key="edit_id_input")
            if st.button("🔍 Charger", key="load_edit"):
                record = df_collecte[df_collecte['id'] == id_a_modifier]
                if not record.empty:
                    st.session_state.edit_mode = True
                    st.session_state.edit_id = id_a_modifier
                    st.rerun()
                else:
                    st.warning(f"⚠️ ID {id_a_modifier} non trouvé")
        
        with col_edit2:
            id_a_supprimer = st.number_input("ID à supprimer", min_value=1, step=1, key="delete_id_input")
            if st.button("🗑️ Supprimer", key="delete_record"):
                if id_a_supprimer in df_collecte['id'].values:
                    delete_paludisme_by_id(id_a_supprimer)
                    st.success(f"✅ ID {id_a_supprimer} supprimé")
                    st.rerun()
                else:
                    st.error(f"❌ ID {id_a_supprimer} non trouvé")
        
        if st.session_state.edit_mode:
            st.markdown("#### Modifier l'enregistrement")
            record = df_collecte[df_collecte['id'] == st.session_state.edit_id].iloc[0]
            
            with st.form(key="edit_form_collecte"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_drs = st.selectbox("DRS", sorted(drs_list), 
                                          index=sorted(drs_list).index(record['DRS']) if record['DRS'] in sorted(drs_list) else 0)
                with col2:
                    new_annee = st.selectbox("Année", [2025, 2026], 
                                            index=0 if record['ANNEE'] == 2025 else 1)
                with col3:
                    mois_list = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                                'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
                    new_mois = st.selectbox("Mois", mois_list,
                                           index=mois_list.index(record['Mois']) if record['Mois'] in mois_list else 0)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_consultations = st.number_input("Consultations", value=record['Consultations'], step=1)
                    new_cas_confirmes = st.number_input("Cas confirmés", value=record['Cas_confirmes'], step=1)
                    new_taux_traitement = st.number_input("Taux traitement (%)", value=record['Taux_traitement'], step=0.01, format="%.2f")
                    new_taux_positivite_ge = st.number_input("Taux positivité GE (%)", value=record['Taux_positivite_GE'], step=0.01, format="%.2f")
                    new_tdr_positifs = st.number_input("TDR positifs", value=record['TDR_positifs'], step=1)
                
                with col2:
                    new_cas_suspects = st.number_input("Cas suspects", value=record['Cas_suspects'], step=1)
                    new_taux_positivite = st.number_input("Taux positivité (%)", value=record['Taux_positivite'], step=0.01, format="%.2f")
                    new_ge_realises = st.number_input("GE réalisés", value=record['GE_realises'], step=1)
                    new_hospitalisations = st.number_input("Hospitalisations", value=record['Hospitalisations'], step=1)
                    new_tdr_realises = st.number_input("TDR réalisés", value=record['TDR_realises'], step=1)
                
                with col3:
                    new_tests_realises = st.number_input("Tests réalisés", value=record['Tests_realises'], step=1)
                    new_traitement_approprié = st.number_input("Traitement approprié", value=record['Traitement_approprié'], step=1)
                    new_ge_positifs = st.number_input("GE positifs", value=record['GE_positifs'], step=1)
                    new_hospitalisations_traitees = st.number_input("Hospitalisations traitées", value=record['Hospitalisations_traitees'], step=1)
                    new_taux_positivite_tdr = st.number_input("Taux positivité TDR (%)", value=record['Taux_positivite_TDR'], step=0.01, format="%.2f")
                    new_deces = st.number_input("Décès", value=record['Deces'], step=1)
                
                col_submit, col_cancel = st.columns(2)
                with col_submit:
                    if st.form_submit_button("✅ Enregistrer"):
                        data = (
                            new_drs, new_annee, new_mois, new_consultations,
                            new_cas_suspects, new_tests_realises, new_cas_confirmes,
                            new_taux_positivite, new_traitement_approprié,
                            new_taux_traitement, new_ge_realises, new_ge_positifs,
                            new_taux_positivite_ge, new_hospitalisations,
                            new_hospitalisations_traitees, new_tdr_realises, new_tdr_positifs,
                            new_taux_positivite_tdr, new_deces, st.session_state.edit_id
                        )
                        update_paludisme(data)
                        st.session_state.edit_mode = False
                        st.session_state.edit_id = None
                        st.success("✅ Modifié")
                        st.rerun()
                with col_cancel:
                    if st.form_submit_button("❌ Annuler"):
                        st.session_state.edit_mode = False
                        st.session_state.edit_id = None
                        st.rerun()
    
    st.markdown("---")
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    
    with col_btn1:
        if not df_collecte.empty:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export = df_collecte.copy()
                df_export.to_excel(writer, index=False, sheet_name='Paludisme_Senegal')
            excel_data = output.getvalue()
            st.download_button(
                "📥 Exporter XLSX",
                excel_data,
                f"paludisme_senegal_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.button("📥 Exporter XLSX", disabled=True, use_container_width=True)
    
    with col_btn2:
        file_type = st.radio("Type de fichier", ["CSV", "XLSX"], horizontal=True, key="file_type_import")
        
        if file_type == "CSV":
            uploaded_file = st.file_uploader("📂 Importer CSV", type=["csv"], key="import_csv")
            if uploaded_file is not None:
                try:
                    try:
                        df_import = pd.read_csv(uploaded_file, encoding='latin-1', sep=None, engine='python', keep_default_na=True, na_values=['NA', 'NaN', ''])
                    except:
                        uploaded_file.seek(0)
                        df_import = pd.read_csv(uploaded_file, encoding='latin-1', sep=';', keep_default_na=True, na_values=['NA', 'NaN', ''])
                    
                    st.success(f"✅ Fichier CSV lu - {len(df_import)} lignes")
                    
                    df_import = standardize_column_names(df_import)
                    df_import = convert_decimal_comma(df_import)
                    
                    with st.expander("🔍 Aperçu du fichier", expanded=True):
                        st.write(f"**Colonnes :** {list(df_import.columns)}")
                        st.write(f"**Lignes :** {len(df_import)}")
                        st.dataframe(df_import.head(5), use_container_width=True)
                    
                    required_cols = ['DRS', 'ANNEE', 'Mois', 'Consultations', 'Cas_suspects', 'Tests_realises', 'Cas_confirmes']
                    missing_cols = [col for col in required_cols if col not in df_import.columns]
                    
                    if missing_cols:
                        st.error(f"❌ Colonnes manquantes : {missing_cols}")
                    else:
                        mode = st.radio("Mode d'import", ["Remplacer", "Ajouter (sans doublons)"], horizontal=True, key="mode_import_csv")
                        if st.button("🚀 Lancer l'import CSV", key="btn_import_csv"):
                            with st.spinner("Import en cours..."):
                                if mode == "Remplacer":
                                    ins, err = replace_all_paludisme(df_import)
                                    if err > 0:
                                        st.warning(f"⚠️ {ins} lignes importées, {err} erreurs")
                                    else:
                                        st.success(f"✅ {ins} lignes importées avec succès")
                                        st.balloons()
                                else:
                                    st.info("ℹ️ Fonction d'ajout en développement")
                                st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur CSV : {e}")
        
        else:
            uploaded_file = st.file_uploader("📂 Importer XLSX", type=["xlsx", "xls"], key="import_xlsx")
            if uploaded_file is not None:
                try:
                    df_import = pd.read_excel(uploaded_file, engine='openpyxl', keep_default_na=True, na_values=['NA', 'NaN', ''])
                    st.success(f"✅ Fichier XLSX lu - {len(df_import)} lignes")
                    
                    df_import = standardize_column_names(df_import)
                    df_import = convert_decimal_comma(df_import)
                    
                    with st.expander("🔍 Aperçu du fichier", expanded=True):
                        st.write(f"**Colonnes :** {list(df_import.columns)}")
                        st.write(f"**Lignes :** {len(df_import)}")
                        st.dataframe(df_import.head(5), use_container_width=True)
                    
                    required_cols = ['DRS', 'ANNEE', 'Mois', 'Consultations', 'Cas_suspects', 'Tests_realises', 'Cas_confirmes']
                    missing_cols = [col for col in required_cols if col not in df_import.columns]
                    
                    if missing_cols:
                        st.error(f"❌ Colonnes manquantes : {missing_cols}")
                    else:
                        mode = st.radio("Mode d'import", ["Remplacer", "Ajouter (sans doublons)"], horizontal=True, key="mode_import_xlsx")
                        if st.button("🚀 Lancer l'import XLSX", key="btn_import_xlsx"):
                            with st.spinner("Import en cours..."):
                                if mode == "Remplacer":
                                    ins, err = replace_all_paludisme(df_import)
                                    if err > 0:
                                        st.warning(f"⚠️ {ins} lignes importées, {err} erreurs")
                                    else:
                                        st.success(f"✅ {ins} lignes importées avec succès")
                                        st.balloons()
                                else:
                                    st.info("ℹ️ Fonction d'ajout en développement")
                                st.rerun()
                except Exception as e:
                    st.error(f"❌ Erreur XLSX : {e}")
    
    with col_btn3:
        if st.button("🗑️ Vider", key="btn_vider", use_container_width=True):
            st.session_state.confirm_delete_paludisme = True
    
    with col_btn4:
        if st.button("🔄 Synchroniser", key="btn_sync", use_container_width=True):
            with st.spinner("Synchronisation..."):
                st.info("ℹ️ Fonction en développement")
    
    if st.session_state.confirm_delete_paludisme:
        st.markdown('<div class="warning-message">⚠️ Supprimer TOUTES les données ?</div>', unsafe_allow_html=True)
        col_yes, col_no = st.columns(2)
        if col_yes.button("✅ Oui", key="confirm_yes"):
            delete_all_paludisme()
            st.session_state.confirm_delete_paludisme = False
            st.success("🗑️ Base vidée")
            st.rerun()
        if col_no.button("❌ Non", key="confirm_no"):
            st.session_state.confirm_delete_paludisme = False
            st.rerun()

# ===============================
# PAGE QUALITÉ DES DONNÉES
# ===============================
elif page == "🔍 Qualité des données":
    show_main_title()
    st.markdown("""
    <div class="quality-header">
        <h2 style="color: white; margin: 0;">🔍 Contrôle Qualité des Données</h2>
        <p style="color: #e0e0e0; margin: 0.3rem 0 0 0;">Vérification automatique de l'intégrité des données collectées</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = get_all_paludisme_data()
    
    if df.empty:
        st.warning("⚠️ Aucune donnée disponible pour l'analyse qualité. Veuillez d'abord importer des données.")
    else:
        # MODIFICATION ICI : Remplacement de selectbox par multiselect
        drs_options = sorted(df['DRS'].unique().tolist())
        selected_drs = st.multiselect("🏥 Filtrer par DRS (Sélection multiple)", drs_options, default=[])
        
        if selected_drs:
            df_filtered = df[df['DRS'].isin(selected_drs)]
        else:
            df_filtered = df
        
        if df_filtered.empty:
            st.info(f"Aucune donnée pour les DRS sélectionnés.")
        else:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📋 Total enregistrements", len(df_filtered))
            with col2:
                st.metric("🏥 DRS", df_filtered['DRS'].nunique())
            with col3:
                st.metric("📅 Années", df_filtered['ANNEE'].nunique())
            with col4:
                st.metric("📊 Colonnes", len(df_filtered.columns))
            
            st.markdown("---")
            
            # 1. RÈGLES DE VALIDATION
            st.markdown("### ✅ Règles de validation")
            
            errors, warnings_list = check_quality_rules(df_filtered)
            
            if errors:
                st.error(f"⚠️ {len(errors)} erreur(s) détectée(s)")
                for err in errors:
                    with st.expander(f"❌ Erreur : {err['regle']} - {err['nombre']} enregistrement(s)"):
                        if err['details']:
                            st.dataframe(pd.DataFrame(err['details']), use_container_width=True)
                            st.caption(f"Affichage des {min(len(err['details']), 10)} premiers enregistrements sur {err['nombre']}")
            else:
                st.success("✅ Aucune erreur détectée dans les règles de validation")
            
            st.markdown("---")
            
            # 2. VALEURS MANQUANTES
            st.markdown("### 📊 Valeurs manquantes")
            
            missing_data = df_filtered.isnull().sum()
            missing_data = missing_data[missing_data > 0]
            missing_percent = (missing_data / len(df_filtered) * 100).round(1)
            
            if not missing_data.empty:
                missing_df = pd.DataFrame({
                    'Colonne': missing_data.index,
                    'Manquants': missing_data.values,
                    '%': missing_percent.values
                })
                st.dataframe(missing_df, use_container_width=True)
                
                fig_missing = px.bar(missing_df, x='Colonne', y='%', 
                                    title="Pourcentage de valeurs manquantes",
                                    color='%', color_continuous_scale='Reds')
                fig_missing.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig_missing, use_container_width=True)
            else:
                st.success("✅ Aucune valeur manquante détectée")
            
            st.markdown("---")
            
            # 3. DOUBLONS
            st.markdown("### 🔍 Doublons")
            
            if 'DRS' in df_filtered.columns and 'ANNEE' in df_filtered.columns and 'Mois' in df_filtered.columns:
                duplicates = df_filtered.duplicated(subset=['DRS', 'ANNEE', 'Mois'], keep=False)
                nb_duplicates = duplicates.sum()
                
                if nb_duplicates > 0:
                    st.error(f"⚠️ {nb_duplicates} enregistrements en double (DRS + Année + Mois)")
                    st.dataframe(df_filtered[duplicates], use_container_width=True)
                else:
                    st.success("✅ Aucun doublon détecté")
            else:
                st.info("Colonnes DRS, ANNEE, Mois non disponibles pour la détection de doublons")
            
            st.markdown("---")
            
            # 4. VALEURS ABERRANTES
            st.markdown("### 📈 Détection des valeurs aberrantes")
            
            numeric_cols = ['Consultations', 'Cas_suspects', 'Tests_realises', 'Cas_confirmes', 
                           'Taux_positivite', 'Traitement_approprié', 'Taux_traitement',
                           'GE_realises', 'GE_positifs', 'Taux_positivite_GE',
                           'Hospitalisations', 'Hospitalisations_traitees',
                           'TDR_realises', 'TDR_positifs', 'Taux_positivite_TDR', 'Deces']
            available_cols = [col for col in numeric_cols if col in df_filtered.columns]
            
            if available_cols:
                selected_col = st.selectbox("Choisir une colonne pour l'analyse des outliers", available_cols)
                
                if selected_col:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig_box = px.box(df_filtered, y=selected_col, 
                                        title=f"Boxplot - {selected_col}",
                                        points="all")
                        fig_box.update_layout(height=400)
                        st.plotly_chart(fig_box, use_container_width=True)
                    
                    with col2:
                        fig_hist = px.histogram(df_filtered, x=selected_col, 
                                               title=f"Distribution - {selected_col}",
                                               nbins=30)
                        fig_hist.update_layout(height=400)
                        st.plotly_chart(fig_hist, use_container_width=True)
                    
                    outliers_iqr = detect_outliers_iqr(df_filtered, selected_col)
                    outliers_zscore = detect_outliers_zscore(df_filtered, selected_col)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Méthode IQR** - {len(outliers_iqr)} outliers")
                        if not outliers_iqr.empty:
                            st.dataframe(outliers_iqr, use_container_width=True)
                        else:
                            st.info("Aucun outlier détecté par IQR")
                    
                    with col2:
                        st.write(f"**Méthode Z-score** - {len(outliers_zscore)} outliers")
                        if not outliers_zscore.empty:
                            st.dataframe(outliers_zscore, use_container_width=True)
                        else:
                            st.info("Aucun outlier détecté par Z-score")
            
            st.markdown("---")
            
            # 5. VALEURS ATYPIQUES
            st.markdown("### 🔍 Détection des valeurs atypiques")
            
            selected_cols = st.multiselect(
                "Sélectionner les colonnes pour la détection d'anomalies",
                available_cols,
                default=available_cols[:3] if len(available_cols) >= 3 else available_cols
            )
            
            if len(selected_cols) >= 2:
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("🔍 Isolation Forest", use_container_width=True):
                        with st.spinner("Analyse en cours avec Isolation Forest..."):
                            anomalies_if = detect_anomalies_isolation_forest(df_filtered, selected_cols)
                            st.write(f"**Isolation Forest** - {len(anomalies_if)} anomalies détectées")
                            if not anomalies_if.empty:
                                st.dataframe(anomalies_if, use_container_width=True)
                            else:
                                st.info("Aucune anomalie détectée")
                
                with col2:
                    if st.button("🔍 Local Outlier Factor", use_container_width=True):
                        with st.spinner("Analyse en cours avec Local Outlier Factor..."):
                            anomalies_lof = detect_anomalies_lof(df_filtered, selected_cols)
                            st.write(f"**Local Outlier Factor** - {len(anomalies_lof)} anomalies détectées")
                            if not anomalies_lof.empty:
                                st.dataframe(anomalies_lof, use_container_width=True)
                            else:
                                st.info("Aucune anomalie détectée")
            else:
                st.info("ℹ️ Sélectionnez au moins 2 colonnes pour la détection d'anomalies")
            
            st.markdown("---")
            
            # ==========================================
            # 6. SCORE DE QUALITÉ PAR DRS
            # ==========================================
            st.markdown("### 🏆 Score de qualité par DRS")
            st.markdown("""
            **Méthodologie du score :**
            - **Score A** = Complétude × 0,70 (une complétude de 100% équivaut à 70 points)
            - **Score B** selon le nombre d'erreurs :
              - 0 à 10 erreurs → **B = 30**
              - 11 à 50 erreurs → **B = 25**
              - 51 à 100 erreurs → **B = 10**
              - Plus de 100 erreurs → **B = 0**
            - **Score final C = A + B**
            """)
            
            scores_df = calculate_drs_score(df_filtered)
            
            col_table, col_points = st.columns([2, 1])
            
            with col_table:
                st.markdown("#### 📋 Classement des DRS selon la complétude et les erreurs")
                
                df_affichage = scores_df[['DRS', 'Complétude T1 2026 (%)', 'Nb. erreurs', 'Score corrigé C', 'Rang']].copy()
                
                def color_rank(val):
                    if val == 1:
                        return 'background-color: #d4edda; font-weight: bold; color: #155724;'
                    elif val <= 3:
                        return 'background-color: #e8f4f8; font-weight: bold; color: #1a5276;'
                    elif val >= len(scores_df) - 1:
                        return 'background-color: #f8d7da; font-weight: bold; color: #721c24;'
                    return ''
                
                styled_scores = df_affichage.style.map(color_rank, subset=['Rang'])
                
                st.dataframe(styled_scores, use_container_width=True, hide_index=True)
            
            with col_points:
                st.markdown("#### 💡 Points clés")
                
                top_drs = scores_df.head(3)
                bottom_drs = scores_df.tail(3)
                
                top_name = top_drs.iloc[0]['DRS']
                top_score = top_drs.iloc[0]['Score corrigé C']
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                            padding: 1rem; border-radius: 10px; margin-bottom: 1rem;
                            border-left: 4px solid #27ae60;">
                    <p style="margin: 0; font-weight: bold; color: #155724;">🥇 En tête du classement</p>
                    <p style="margin: 0.5rem 0 0 0; color: #333;">
                        <strong>{top_name}</strong> est en tête du classement des DRS,
                        avec un score corrigé de <strong>{top_score:.2f}/100</strong>.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                bottom_names = ", ".join(bottom_drs['DRS'].tolist())
                bottom_max_score = bottom_drs.iloc[0]['Score corrigé C']
                
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
                            padding: 1rem; border-radius: 10px; margin-bottom: 1rem;
                            border-left: 4px solid #e74c3c;">
                    <p style="margin: 0; font-weight: bold; color: #721c24;">⚠️ En bas du classement</p>
                    <p style="margin: 0.5rem 0 0 0; color: #333;">
                        <strong>{bottom_names}</strong> ferment le classement,
                        avec des scores inférieurs à <strong>{bottom_max_score:.2f}/100</strong>.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                score_moyen = scores_df['Score corrigé C'].mean()
                compl_moyenne = scores_df['Complétude T1 2026 (%)'].mean()
                nb_erreurs_total = scores_df['Nb. erreurs'].sum()
                
                st.markdown(f"""
                <div style="background-color: #e8f4f8; padding: 1rem; border-radius: 10px;
                            border-left: 4px solid #3498db;">
                    <p style="margin: 0; font-weight: bold; color: #1a5276;">📊 Statistiques globales</p>
                    <p style="margin: 0.5rem 0 0 0; color: #333; font-size: 0.9rem;">
                        • Score moyen : <strong>{score_moyen:.2f}/100</strong><br>
                        • Complétude moyenne : <strong>{compl_moyenne:.2f}%</strong><br>
                        • Total erreurs : <strong>{nb_erreurs_total:,}</strong>
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")

# ===============================
# PAGE VISUALISATION
# ===============================
elif page == "📊 Visualisation":
    show_main_title()
    st.title("📊 Visualisation et recherche")
    
    df = get_all_paludisme_data()
    
    if df.empty:
        st.warning("⚠️ Aucune donnée disponible pour la visualisation. Veuillez d'abord importer des données.")
    else:
        col_f1, col_f2 = st.columns(2)
        
        # MODIFICATION ICI : Remplacement de selectbox par multiselect pour le DRS
        with col_f1:
            drs_options = sorted(df['DRS'].unique().tolist())
            selected_drs = st.multiselect("🏥 DRS (Sélection multiple)", drs_options, default=[])
        
        # MODIFICATION ICI : Remplacement de selectbox par multiselect pour l'Année
        with col_f2:
            annees = sorted(df['ANNEE'].unique().tolist())
            selected_annee = st.multiselect("📆 Année (Sélection multiple)", annees, default=[])
        
        df_filtered = df.copy()
        
        # Application des filtres si des cases sont cochées
        if selected_drs:
            df_filtered = df_filtered[df_filtered['DRS'].isin(selected_drs)]
        if selected_annee:
            df_filtered = df_filtered[df_filtered['ANNEE'].isin(selected_annee)]
        
        if df_filtered.empty:
            st.warning("⚠️ Aucune donnée ne correspond aux filtres sélectionnés.")
        else:
            display_type = st.selectbox(
                "Choisissez le type d'affichage",
                [
                    "Recherche", "Colonne", "Colonne bande", "Colonne empilée",
                    "Bar", "Bar empilé", "Ligne", "Secteur (camembert)",
                    "Radar", "Zone", "Zone empilée", "Tarte", "Jaguar",
                    "Année après année (ligne)", "Année après année (colonne)",
                    "Valeur unique", "Dispersion", "Carte"
                ]
            )
            
            if display_type == "Recherche":
                st.markdown("### 🔍 Recherche textuelle")
                colonnes_recherche = ['DRS', 'ANNEE', 'Mois']
                colonne_choisie = st.selectbox("Colonne à filtrer", colonnes_recherche)
                texte_recherche = st.text_input("Texte à rechercher (contient)", "")
                
                if texte_recherche:
                    df_filtre = df_filtered[df_filtered[colonne_choisie].astype(str).str.contains(texte_recherche, case=False, na=False)]
                else:
                    df_filtre = df_filtered
                
                st.dataframe(df_filtre, use_container_width=True)
                st.caption(f"{len(df_filtre)} ligne(s) trouvée(s)")
            
            else:
                indicateurs = {
                    'Consultations': 'Consultations',
                    'Cas suspects': 'Cas_suspects',
                    'Tests réalisés': 'Tests_realises',
                    'Cas confirmés': 'Cas_confirmes',
                    'Taux de positivité (%)': 'Taux_positivite',
                    'Traitement approprié': 'Traitement_approprié',
                    'Taux de traitement (%)': 'Taux_traitement',
                    'GE réalisés': 'GE_realises',
                    'GE positifs': 'GE_positifs',
                    'Taux positivité GE (%)': 'Taux_positivite_GE',
                    'Hospitalisations': 'Hospitalisations',
                    'Hospitalisations traitées': 'Hospitalisations_traitees',
                    'TDR réalisés': 'TDR_realises',
                    'TDR positifs': 'TDR_positifs',
                    'Taux positivité TDR (%)': 'Taux_positivite_TDR',
                    'Décès': 'Deces'
                }
                
                if 'periodname' not in df_filtered.columns:
                    df_filtered['periodname'] = df_filtered['Mois'] + ' ' + df_filtered['ANNEE'].astype(str)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    indicateur = st.selectbox("📊 Choisir un indicateur", list(indicateurs.keys()))
                    y_col = indicateurs[indicateur]
                
                with col2:
                    x_options = ['periodname', 'Mois', 'DRS', 'ANNEE']
                    x_col = st.selectbox("📅 Axe X", x_options)
                
                if display_type == "Colonne":
                    fig = px.bar(df_filtered, x=x_col, y=y_col, 
                                title=f"Répartition de {indicateur}",
                                text_auto=True, color=y_col, color_continuous_scale='Blues')
                    fig.update_layout(yaxis_tickformat=',.0f')
                    st.plotly_chart(fig, use_container_width=True)
                
                elif display_type == "Colonne bande":
                    fig = px.bar(df_filtered, x=x_col, y=y_col,
                                title=f"Répartition de {indicateur}",
                                text_auto=True, color=y_col,
                                color_continuous_scale='Reds', barmode='relative')
                    fig.update_layout(yaxis_tickformat=',.0f')
                    st.plotly_chart(fig, use_container_width=True)
                
                elif display_type == "Colonne empilée":
                    if x_col != 'DRS' and 'DRS' in df_filtered.columns:
                        fig = px.bar(df_filtered, x=x_col, y=y_col,
                                    title=f"Répartition de {indicateur} par DRS",
                                    text_auto=True, color='DRS', barmode='stack')
                        fig.update_layout(yaxis_tickformat=',.0f')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Sélectionnez un axe X différent pour voir les colonnes empilées")
                
                elif display_type == "Bar":
                    fig = px.bar(df_filtered, y=x_col, x=y_col, orientation='h',
                                title=f"Répartition de {indicateur}",
                                text_auto=True, color=y_col, color_continuous_scale='Blues')
                    fig.update_layout(xaxis_tickformat=',.0f')
                    st.plotly_chart(fig, use_container_width=True)
                
                elif display_type == "Bar empilé":
                    if x_col != 'DRS' and 'DRS' in df_filtered.columns:
                        fig = px.bar(df_filtered, y=x_col, x=y_col, orientation='h',
                                    title=f"Répartition de {indicateur} par DRS",
                                    text_auto=True, color='DRS', barmode='stack')
                        fig.update_layout(xaxis_tickformat=',.0f')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Sélectionnez un axe X différent pour voir les barres empilées")
                
                elif display_type == "Ligne":
                    fig = px.line(df_filtered, x=x_col, y=y_col, markers=True,
                                 title=f"Évolution de {indicateur}")
                    if 'Taux' in indicateur:
                        fig.update_layout(yaxis_tickformat='.2f')
                    else:
                        fig.update_layout(yaxis_tickformat=',.0f')
                    st.plotly_chart(fig, use_container_width=True)
                
                elif display_type == "Secteur (camembert)":
                    df_pie = df_filtered.groupby(x_col)[y_col].sum().reset_index()
                    fig = px.pie(df_pie, names=x_col, values=y_col,
                                title=f"Part de {indicateur}")
                    st.plotly_chart(fig, use_container_width=True)
                
                elif display_type == "Radar":
                    df_radar = df_filtered.groupby(x_col)[y_col].mean().reset_index()
                    fig = px.line_polar(df_radar, r=y_col, theta=x_col, 
                                       title=f"Radar - {indicateur}", line_close=True)
                    st.plotly_chart(fig, use_container_width=True)
                
                elif display_type == "Zone":
                    fig = px.area(df_filtered, x=x_col, y=y_col,
                                 title=f"Zone - Évolution de {indicateur}")
                    if 'Taux' in indicateur:
                        fig.update_layout(yaxis_tickformat='.2f')
                    else:
                        fig.update_layout(yaxis_tickformat=',.0f')
                    st.plotly_chart(fig, use_container_width=True)
                
                elif display_type == "Zone empilée":
                    if 'DRS' in df_filtered.columns:
                        fig = px.area(df_filtered, x=x_col, y=y_col,
                                     title=f"Zone empilée - {indicateur}", color='DRS')
                        if 'Taux' in indicateur:
                            fig.update_layout(yaxis_tickformat='.2f')
                        else:
                            fig.update_layout(yaxis_tickformat=',.0f')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("La colonne DRS est nécessaire pour ce graphique")
                
                elif display_type == "Tarte":
                    df_tarte = df_filtered.groupby(x_col)[y_col].sum().reset_index()
                    fig = px.pie(df_tarte, names=x_col, values=y_col,
                                title=f"Tarte - {indicateur}", hole=0.3)
                    st.plotly_chart(fig, use_container_width=True)
                
                elif display_type == "Jaguar":
                    if len(df_filtered) > 0:
                        fig = px.scatter(df_filtered, x=x_col, y=y_col,
                                        title=f"Jaguar - {indicateur}",
                                        size=y_col,
                                        color='DRS' if 'DRS' in df_filtered.columns else None,
                                        hover_data=['ANNEE', 'Mois'])
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Données insuffisantes pour ce graphique")
                
                elif display_type == "Année après année (ligne)":
                    if 'ANNEE' in df_filtered.columns:
                        df_annuel = df_filtered.groupby(['ANNEE', x_col])[y_col].sum().reset_index()
                        fig = px.line(df_annuel, x=x_col, y=y_col, color='ANNEE',
                                     title=f"Année après année - {indicateur}", markers=True)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("La colonne ANNEE est nécessaire pour ce graphique")
                
                elif display_type == "Année après année (colonne)":
                    if 'ANNEE' in df_filtered.columns:
                        df_annuel = df_filtered.groupby(['ANNEE', x_col])[y_col].sum().reset_index()
                        fig = px.bar(df_annuel, x=x_col, y=y_col, color='ANNEE',
                                    title=f"Année après année - {indicateur}", barmode='group')
                        fig.update_layout(yaxis_tickformat=',.0f')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("La colonne ANNEE est nécessaire pour ce graphique")
                
                elif display_type == "Valeur unique":
                    total = df_filtered[y_col].sum()
                    moyenne = df_filtered[y_col].mean()
                    max_val = df_filtered[y_col].max()
                    min_val = df_filtered[y_col].min()
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total", f"{total:,.0f}")
                    with col2:
                        st.metric("Moyenne", f"{moyenne:,.2f}")
                    with col3:
                        st.metric("Maximum", f"{max_val:,.0f}")
                    with col4:
                        st.metric("Minimum", f"{min_val:,.0f}")
                
                elif display_type == "Dispersion":
                    col1, col2 = st.columns(2)
                    with col1:
                        x_ind = st.selectbox("Axe X", list(indicateurs.keys()), key='x_ind')
                    with col2:
                        y_ind = st.selectbox("Axe Y", list(indicateurs.keys()), key='y_ind')
                    
                    if st.button("🔍 Afficher"):
                        fig = px.scatter(df_filtered, x=indicateurs[x_ind], y=indicateurs[y_ind],
                                       text='periodname',
                                       title=f"Relation entre {x_ind} et {y_ind}",
                                       color='DRS' if 'DRS' in df_filtered.columns else None)
                        fig.update_traces(textposition='top center')
                        st.plotly_chart(fig, use_container_width=True)
                
                elif display_type == "Carte":
                    st.info("🗺️ La carte du Sénégal est disponible dans l'onglet 'Qualité des données'")
                    st.markdown("""
                    <div style="background-color: #e8f4f8; padding: 1.5rem; border-radius: 10px; text-align: center;">
                        <p style="font-size: 1.2rem; color: #1a5276;">
                            📍 Consultez l'onglet <strong>"Qualité des données"</strong> pour voir la carte du Sénégal
                        </p>
                        <p style="color: #666;">Les scores qualité par DRS y sont affichés sur une carte interactive</p>
                    </div>
                    """, unsafe_allow_html=True)

# ===============================
# PAGE MODÉLISATION STATISTIQUE
# ===============================
elif page == "📈 Modélisation Statistique":
    show_main_title()
    st.markdown("""
    <div class="stat-header">
        <h2 style="color: white; margin: 0;">📈 Modélisation Statistique</h2>
        <p style="color: #e0e0e0; margin: 0.3rem 0 0 0;">Tests statistiques et modélisation interactive</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = get_all_paludisme_data()
    
    if df.empty:
        st.warning("⚠️ Aucune donnée disponible pour l'analyse. Veuillez d'abord importer des données.")
    else:
        # ==========================================
        # MODULE : TESTS STATISTIQUES
        # ==========================================
        st.markdown("""
        <div class="test-header-section">
            <h3 style="color: white; margin: 0;">🔬 Tests statistiques</h3>
            <p style="color: #f0f0f0; margin: 0.3rem 0 0 0;">
                Sélectionnez une variable et un test pour explorer les propriétés statistiques des données
            </p>
        </div>
        """, unsafe_allow_html=True)

        variables_numeriques = {
            'Consultations': 'Consultations',
            'Cas suspects': 'Cas_suspects',
            'Tests réalisés': 'Tests_realises',
            'Cas confirmés': 'Cas_confirmes',
            'Taux de positivité (%)': 'Taux_positivite',
            'Traitement approprié': 'Traitement_approprié',
            'Taux de traitement (%)': 'Taux_traitement',
            'GE réalisés': 'GE_realises',
            'GE positifs': 'GE_positifs',
            'Taux positivité GE (%)': 'Taux_positivite_GE',
            'Hospitalisations': 'Hospitalisations',
            'Hospitalisations traitées': 'Hospitalisations_traitees',
            'TDR réalisés': 'TDR_realises',
            'TDR positifs': 'TDR_positifs',
            'Taux positivité TDR (%)': 'Taux_positivite_TDR',
            'Décès': 'Deces'
        }

        variables_categorielles = {
            'DRS': 'DRS',
            'Année': 'ANNEE',
            'Mois': 'Mois'
        }

        tests_disponibles = [
            'Shapiro-Wilk (normalité)',
            'Kolmogorov-Smirnov (normalité)',
            'Chi² d\'indépendance',
            'ANOVA (comparaison de moyennes)',
            'Kruskal-Wallis (comparaison de rangs)',
            'Corrélation de Pearson',
            'Corrélation de Spearman',
            'Test de surdispersion (Poisson / Binomiale Négative)'
        ]

        col_test1, col_test2 = st.columns(2)

        with col_test1:
            test_choisi = st.selectbox(
                "🧪 Choisissez le test statistique",
                tests_disponibles,
                index=0
            )

        with col_test2:
            if test_choisi in ['Shapiro-Wilk (normalité)', 'Kolmogorov-Smirnov (normalité)',
                               'Test de surdispersion (Poisson / Binomiale Négative)']:
                var_label = st.selectbox(
                    "📊 Variable à analyser",
                    list(variables_numeriques.keys()),
                    index=0
                )
                var_principale = variables_numeriques[var_label]
            else:
                var_label = st.selectbox(
                    "📊 Variable principale (numérique)",
                    list(variables_numeriques.keys()),
                    index=0
                )
                var_principale = variables_numeriques[var_label]

        data_test = df.copy()
        for col in data_test.columns:
            if col not in ['DRS', 'Mois', 'id']:
                data_test[col] = pd.to_numeric(data_test[col], errors='coerce')
        
        data_test = data_test.dropna(subset=[var_principale])

        if len(data_test) < 5:
            st.warning("⚠️ Pas assez de données valides pour ce test (minimum 5 observations).")
        else:
            valeurs = data_test[var_principale].dropna()
            
            st.caption(f"Variable sélectionnée : **{var_label}** — {len(valeurs)} observations valides")

            if test_choisi == 'Shapiro-Wilk (normalité)':
                st.markdown("#### 📐 Test de Shapiro-Wilk")
                st.markdown("""
                **Hypothèses :**
                - H₀ : La variable suit une loi normale
                - H₁ : La variable ne suit pas une loi normale
                """)
                
                if len(valeurs) < 3:
                    st.warning("⚠️ Effectif trop faible pour Shapiro-Wilk (minimum 3).")
                else:
                    try:
                        stat, p_value = shapiro(valeurs)
                        
                        interpretation = "✅ On ne rejette pas H₀ : la distribution semble normale." if p_value >= 0.05 \
                                         else "❌ On rejette H₀ : la distribution ne suit pas une loi normale."
                        
                        classe = "test-signif" if p_value < 0.05 else "test-non-signif"
                        
                        st.markdown(f"""
                        <div class="test-result-box {classe}">
                            <h4>Résultat du test de Shapiro-Wilk</h4>
                            <p><strong>Statistique W :</strong> {stat:.4f}</p>
                            <p><strong>p-value :</strong> {p_value:.4f}</p>
                            <p><strong>Décision (seuil α = 0,05) :</strong> {interpretation}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            fig_hist = px.histogram(
                                x=valeurs, nbins=min(30, len(valeurs)),
                                title=f"Distribution de {var_label}",
                                labels={'x': var_label, 'y': 'Fréquence'}
                            )
                            st.plotly_chart(fig_hist, use_container_width=True)
                        with col2:
                            (osm, osr), (slope, intercept, r) = stats.probplot(valeurs, dist="norm")
                            fig_qq = go.Figure()
                            fig_qq.add_trace(go.Scatter(x=osm, y=osr, mode='markers', name='Données'))
                            fig_qq.add_trace(go.Scatter(x=osm, y=slope*osm + intercept, mode='lines',
                                                       name='Droite théorique', line=dict(color='red', dash='dash')))
                            fig_qq.update_layout(title=f"QQ-plot - {var_label}",
                                                xaxis_title="Quantiles théoriques",
                                                yaxis_title="Quantiles observés")
                            st.plotly_chart(fig_qq, use_container_width=True)
                    except Exception as e:
                        st.error(f"Erreur lors de l'exécution du test : {e}")

            elif test_choisi == 'Kolmogorov-Smirnov (normalité)':
                st.markdown("#### 📐 Test de Kolmogorov-Smirnov")
                st.markdown("""
                **Hypothèses :**
                - H₀ : La variable suit une loi normale
                - H₁ : La variable ne suit pas une loi normale
                """)
                
                if len(valeurs) < 3:
                    st.warning("⚠️ Effectif trop faible pour K-S (minimum 3).")
                else:
                    try:
                        valeurs_std = (valeurs - valeurs.mean()) / valeurs.std(ddof=1)
                        stat, p_value = kstest(valeurs_std, 'norm')
                        
                        interpretation = "✅ On ne rejette pas H₀ : la distribution semble normale." if p_value >= 0.05 \
                                         else "❌ On rejette H₀ : la distribution ne suit pas une loi normale."
                        
                        classe = "test-signif" if p_value < 0.05 else "test-non-signif"
                        
                        st.markdown(f"""
                        <div class="test-result-box {classe}">
                            <h4>Résultat du test de Kolmogorov-Smirnov</h4>
                            <p><strong>Statistique D :</strong> {stat:.4f}</p>
                            <p><strong>p-value :</strong> {p_value:.4f}</p>
                            <p><strong>Décision (seuil α = 0,05) :</strong> {interpretation}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        valeurs_std_sorted = np.sort(valeurs_std)
                        n = len(valeurs_std_sorted)
                        ecdf = np.arange(1, n+1) / n
                        cdf_theorique = stats.norm.cdf(valeurs_std_sorted)
                        
                        fig_ks = go.Figure()
                        fig_ks.add_trace(go.Scatter(x=valeurs_std_sorted, y=ecdf, mode='lines', name='ECDF'))
                        fig_ks.add_trace(go.Scatter(x=valeurs_std_sorted, y=cdf_theorique, mode='lines',
                                                    name='CDF théorique (normale)', line=dict(dash='dash')))
                        fig_ks.update_layout(title=f"Kolmogorov-Smirnov - {var_label}",
                                            xaxis_title="Valeurs standardisées",
                                            yaxis_title="Probabilité cumulée")
                        st.plotly_chart(fig_ks, use_container_width=True)
                    except Exception as e:
                        st.error(f"Erreur lors de l'exécution du test : {e}")

            elif test_choisi == 'Chi² d\'indépendance':
                st.markdown("#### 📐 Test du Chi² d'indépendance")
                st.markdown("""
                **Hypothèses :**
                - H₀ : Les deux variables catégorielles sont indépendantes
                - H₁ : Les deux variables sont dépendantes (associées)
                """)
                
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    var1_label = st.selectbox("Variable catégorielle 1", list(variables_categorielles.keys()), index=0)
                with col_c2:
                    var2_label = st.selectbox("Variable catégorielle 2", list(variables_categorielles.keys()), index=1)
                
                var1 = variables_categorielles[var1_label]
                var2 = variables_categorielles[var2_label]
                
                if var1 == var2:
                    st.warning("⚠️ Veuillez choisir deux variables différentes.")
                else:
                    data_chi = data_test.dropna(subset=[var1, var2])
                    
                    if len(data_chi) < 5:
                        st.warning("⚠️ Pas assez de données pour le Chi².")
                    else:
                        contingency = pd.crosstab(data_chi[var1], data_chi[var2])
                        
                        st.markdown("##### Table de contingence")
                        st.dataframe(contingency, use_container_width=True)
                        
                        if contingency.shape[0] < 2 or contingency.shape[1] < 2:
                            st.warning("⚠️ La table de contingence doit avoir au moins 2 lignes et 2 colonnes.")
                        else:
                            try:
                                chi2, p_value, dof, expected = chi2_contingency(contingency)
                                
                                interpretation = "✅ On ne rejette pas H₀ : les variables semblent indépendantes." if p_value >= 0.05 \
                                                 else "❌ On rejette H₀ : les variables sont dépendantes (associées)."
                                
                                classe = "test-signif" if p_value < 0.05 else "test-non-signif"
                                
                                st.markdown(f"""
                                <div class="test-result-box {classe}">
                                    <h4>Résultat du test du Chi²</h4>
                                    <p><strong>Statistique χ² :</strong> {chi2:.4f}</p>
                                    <p><strong>Degrés de liberté :</strong> {dof}</p>
                                    <p><strong>p-value :</strong> {p_value:.4f}</p>
                                    <p><strong>Décision (seuil α = 0,05) :</strong> {interpretation}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                fig_chi = px.imshow(contingency, text_auto=True,
                                                   title=f"Table de contingence {var1_label} × {var2_label}",
                                                   labels=dict(x=var2_label, y=var1_label, color="Effectif"),
                                                   color_continuous_scale='Blues')
                                st.plotly_chart(fig_chi, use_container_width=True)
                            except Exception as e:
                                st.error(f"Erreur lors du test : {e}")

            elif test_choisi == 'ANOVA (comparaison de moyennes)':
                st.markdown("#### 📐 ANOVA à un facteur")
                st.markdown("""
                **Hypothèses :**
                - H₀ : Les moyennes de la variable numérique sont égales entre les groupes
                - H₁ : Au moins une moyenne diffère
                """)
                
                var_groupe_label = st.selectbox("Variable de regroupement (catégorielle)", list(variables_categorielles.keys()), index=0)
                var_groupe = variables_categorielles[var_groupe_label]
                
                data_anova = data_test.dropna(subset=[var_principale, var_groupe])
                
                if len(data_anova) < 5:
                    st.warning("⚠️ Pas assez de données pour l'ANOVA.")
                else:
                    groupes = [data_anova[data_anova[var_groupe] == g][var_principale].dropna() for g in data_anova[var_groupe].unique()]
                    groupes = [g for g in groupes if len(g) >= 2]
                    
                    if len(groupes) < 2:
                        st.warning("⚠️ Il faut au moins deux groupes avec au moins 2 observations chacun.")
                    else:
                        try:
                            f_stat, p_value = f_oneway(*groupes)
                            
                            interpretation = "✅ On ne rejette pas H₀ : les moyennes ne diffèrent pas significativement." if p_value >= 0.05 \
                                             else "❌ On rejette H₀ : au moins une moyenne diffère significativement."
                            
                            classe = "test-signif" if p_value < 0.05 else "test-non-signif"
                            
                            st.markdown(f"""
                            <div class="test-result-box {classe}">
                                <h4>Résultat de l'ANOVA</h4>
                                <p><strong>Statistique F :</strong> {f_stat:.4f}</p>
                                <p><strong>p-value :</strong> {p_value:.4f}</p>
                                <p><strong>Nombre de groupes :</strong> {len(groupes)}</p>
                                <p><strong>Décision (seuil α = 0,05) :</strong> {interpretation}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            fig_anova = px.box(data_anova, x=var_groupe, y=var_principale,
                                              title=f"{var_label} selon {var_groupe_label}",
                                              color=var_groupe)
                            st.plotly_chart(fig_anova, use_container_width=True)
                        except Exception as e:
                            st.error(f"Erreur lors de l'ANOVA : {e}")

            elif test_choisi == 'Kruskal-Wallis (comparaison de rangs)':
                st.markdown("#### 📐 Test de Kruskal-Wallis")
                st.markdown("""
                **Hypothèses :**
                - H₀ : Les distributions de la variable numérique sont identiques entre les groupes
                - H₁ : Au moins une distribution diffère
                """)
                
                var_groupe_label = st.selectbox("Variable de regroupement (catégorielle)", list(variables_categorielles.keys()), index=0)
                var_groupe = variables_categorielles[var_groupe_label]
                
                data_kw = data_test.dropna(subset=[var_principale, var_groupe])
                
                if len(data_kw) < 5:
                    st.warning("⚠️ Pas assez de données pour Kruskal-Wallis.")
                else:
                    groupes = [data_kw[data_kw[var_groupe] == g][var_principale].dropna() for g in data_kw[var_groupe].unique()]
                    groupes = [g for g in groupes if len(g) >= 2]
                    
                    if len(groupes) < 2:
                        st.warning("⚠️ Il faut au moins deux groupes avec au moins 2 observations chacun.")
                    else:
                        try:
                            h_stat, p_value = kruskal(*groupes)
                            
                            interpretation = "✅ On ne rejette pas H₀ : les distributions ne diffèrent pas significativement." if p_value >= 0.05 \
                                             else "❌ On rejette H₀ : au moins une distribution diffère significativement."
                            
                            classe = "test-signif" if p_value < 0.05 else "test-non-signif"
                            
                            st.markdown(f"""
                            <div class="test-result-box {classe}">
                                <h4>Résultat du test de Kruskal-Wallis</h4>
                                <p><strong>Statistique H :</strong> {h_stat:.4f}</p>
                                <p><strong>p-value :</strong> {p_value:.4f}</p>
                                <p><strong>Nombre de groupes :</strong> {len(groupes)}</p>
                                <p><strong>Décision (seuil α = 0,05) :</strong> {interpretation}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            fig_kw = px.box(data_kw, x=var_groupe, y=var_principale,
                                           title=f"{var_label} selon {var_groupe_label}",
                                           color=var_groupe)
                            st.plotly_chart(fig_kw, use_container_width=True)
                        except Exception as e:
                            st.error(f"Erreur lors du test de Kruskal-Wallis : {e}")

            elif test_choisi == 'Corrélation de Pearson':
                st.markdown("#### 📐 Corrélation de Pearson")
                st.markdown("""
                **Hypothèses :**
                - H₀ : ρ = 0 (pas de corrélation linéaire)
                - H₁ : ρ ≠ 0 (corrélation linéaire significative)
                """)
                
                var2_label = st.selectbox("Seconde variable numérique", list(variables_numeriques.keys()), index=1)
                var2 = variables_numeriques[var2_label]
                
                if var2 == var_principale:
                    st.warning("⚠️ Veuillez choisir deux variables différentes.")
                else:
                    data_corr = data_test.dropna(subset=[var_principale, var2])
                    
                    if len(data_corr) < 5:
                        st.warning("⚠️ Pas assez de données pour la corrélation.")
                    else:
                        try:
                            r, p_value = pearsonr(data_corr[var_principale], data_corr[var2])
                            
                            interpretation = "✅ Corrélation significative." if p_value < 0.05 else "❌ Corrélation non significative."
                            classe = "test-signif" if p_value < 0.05 else "test-non-signif"
                            
                            if abs(r) < 0.3:
                                force = "faible"
                            elif abs(r) < 0.7:
                                force = "modérée"
                            else:
                                force = "forte"
                            sens = "positive" if r > 0 else "négative"
                            
                            st.markdown(f"""
                            <div class="test-result-box {classe}">
                                <h4>Résultat de la corrélation de Pearson</h4>
                                <p><strong>Coefficient r :</strong> {r:.4f}</p>
                                <p><strong>p-value :</strong> {p_value:.4f}</p>
                                <p><strong>Interprétation :</strong> {interpretation}</p>
                                <p><strong>Force :</strong> corrélation {force} {sens}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            fig_pearson = px.scatter(data_corr, x=var_principale, y=var2,
                                                    title=f"Corrélation Pearson - {var_label} vs {var2_label}",
                                                    trendline="ols")
                            st.plotly_chart(fig_pearson, use_container_width=True)
                        except Exception as e:
                            st.error(f"Erreur lors de la corrélation de Pearson : {e}")

            elif test_choisi == 'Corrélation de Spearman':
                st.markdown("#### 📐 Corrélation de Spearman")
                st.markdown("""
                **Hypothèses :**
                - H₀ : ρ = 0 (pas de corrélation des rangs)
                - H₁ : ρ ≠ 0 (corrélation des rangs significative)
                """)
                
                var2_label = st.selectbox("Seconde variable numérique", list(variables_numeriques.keys()), index=1)
                var2 = variables_numeriques[var2_label]
                
                if var2 == var_principale:
                    st.warning("⚠️ Veuillez choisir deux variables différentes.")
                else:
                    data_corr = data_test.dropna(subset=[var_principale, var2])
                    
                    if len(data_corr) < 5:
                        st.warning("⚠️ Pas assez de données pour la corrélation.")
                    else:
                        try:
                            rho, p_value = spearmanr(data_corr[var_principale], data_corr[var2])
                            
                            interpretation = "✅ Corrélation significative." if p_value < 0.05 else "❌ Corrélation non significative."
                            classe = "test-signif" if p_value < 0.05 else "test-non-signif"
                            
                            if abs(rho) < 0.3:
                                force = "faible"
                            elif abs(rho) < 0.7:
                                force = "modérée"
                            else:
                                force = "forte"
                            sens = "positive" if rho > 0 else "négative"
                            
                            st.markdown(f"""
                            <div class="test-result-box {classe}">
                                <h4>Résultat de la corrélation de Spearman</h4>
                                <p><strong>Coefficient ρ :</strong> {rho:.4f}</p>
                                <p><strong>p-value :</strong> {p_value:.4f}</p>
                                <p><strong>Interprétation :</strong> {interpretation}</p>
                                <p><strong>Force :</strong> corrélation {force} {sens}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            fig_spearman = px.scatter(data_corr, x=var_principale, y=var2,
                                                     title=f"Corrélation Spearman - {var_label} vs {var2_label}",
                                                     trendline="lowess")
                            st.plotly_chart(fig_spearman, use_container_width=True)
                        except Exception as e:
                            st.error(f"Erreur lors de la corrélation de Spearman : {e}")

            elif test_choisi == 'Test de surdispersion (Poisson / Binomiale Négative)':
                st.markdown("#### 📐 Test de surdispersion")
                st.markdown("""
                Ce test compare le modèle de Poisson au modèle Binomiale Négative.
                **Hypothèses :**
                - H₀ : La variance est égale à la moyenne (Poisson)
                - H₁ : La variance est supérieure à la moyenne (surdispersion → Binomiale Négative)
                """)
                
                valeurs_int = valeurs[valeurs >= 0]
                
                if len(valeurs_int) < 5:
                    st.warning("⚠️ Pas assez de données pour le test.")
                else:
                    moyenne = valeurs_int.mean()
                    variance = valeurs_int.var()
                    ratio = variance / moyenne if moyenne > 0 else np.nan
                    
                    st.markdown(f"""
                    <div style="background-color: #f0f8ff; padding: 1rem; border-radius: 10px;">
                        <p><strong>Moyenne :</strong> {moyenne:.4f}</p>
                        <p><strong>Variance :</strong> {variance:.4f}</p>
                        <p><strong>Ratio Variance / Moyenne :</strong> {ratio:.4f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    try:
                        X_test = sm.add_constant(np.ones(len(valeurs_int)))
                        poisson_model = sm.GLM(valeurs_int, X_test, family=sm.families.Poisson()).fit()
                        
                        pearson_chi2 = poisson_model.pearson_chi2
                        df_resid = poisson_model.df_resid
                        dispersion = pearson_chi2 / df_resid if df_resid > 0 else np.nan
                        
                        p_value_disp = 1 - stats.chi2.cdf(pearson_chi2, df_resid) if df_resid > 0 else np.nan
                        
                        if ratio > 1.2:
                            decision = "❌ Surdispersion détectée : le modèle Binomiale Négative est plus approprié."
                            classe = "test-signif"
                        else:
                            decision = "✅ Pas de surdispersion majeure : le modèle de Poisson pourrait être approprié."
                            classe = "test-non-signif"
                        
                        st.markdown(f"""
                        <div class="test-result-box {classe}">
                            <h4>Résultat du test de surdispersion</h4>
                            <p><strong>Ratio Variance/Moyenne :</strong> {ratio:.4f}</p>
                            <p><strong>Dispersion de Pearson (χ²/df) :</strong> {dispersion:.4f}</p>
                            <p><strong>p-value approximative :</strong> {p_value_disp:.4f}</p>
                            <p><strong>Décision :</strong> {decision}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if 'DRS' in data_test.columns:
                            stats_par_drs = data_test.groupby('DRS')[var_principale].agg(['mean', 'var', 'count']).reset_index()
                            stats_par_drs = stats_par_drs[stats_par_drs['count'] >= 2]
                            
                            if not stats_par_drs.empty:
                                fig_disp = px.scatter(stats_par_drs, x='mean', y='var',
                                                     text='DRS',
                                                     title="Moyenne vs Variance par DRS",
                                                     labels={'mean': 'Moyenne', 'var': 'Variance'})
                                max_val = max(stats_par_drs['mean'].max(), stats_par_drs['var'].max())
                                fig_disp.add_trace(go.Scatter(x=[0, max_val], y=[0, max_val],
                                                             mode='lines', name='Variance = Moyenne',
                                                             line=dict(dash='dash', color='red')))
                                st.plotly_chart(fig_disp, use_container_width=True)
                    except Exception as e:
                        st.error(f"Erreur lors du test de surdispersion : {e}")

        st.markdown("---")
        
        # ==========================================
        # MODULE : MODÉLISATION STATISTIQUE (existant)
        # ==========================================
        st.markdown("""
        <div class="stat-header">
            <h2 style="color: white; margin: 0;">📈 Modélisation Statistique</h2>
            <p style="color: #e0e0e0; margin: 0.3rem 0 0 0;">Modélisation interactive avec comparaison Binomiale Négative / ZIP</p>
        </div>
        """, unsafe_allow_html=True)
        # ==========================================
        # MODULE : ACP - ANALYSE EN COMPOSANTES PRINCIPALES
        # ==========================================
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #8e44ad 0%, #9b59b6 100%);
        padding: 1.2rem; border-radius: 12px; color: white; text-align: center; margin: 1rem 0;">
        <h3 style="color: white; margin: 0;">🧬 ACP - Analyse en Composantes Principales</h3>
         <p style="color: #f0f0f0; margin: 0.3rem 0 0 0;">
        Réduction de dimension et visualisation des corrélations entre variables quantitatives
        </p>
         </div>
        """, unsafe_allow_html=True)

        variables_acp = {
            'Consultations': 'Consultations',
            'Cas suspects': 'Cas_suspects',
            'Tests réalisés': 'Tests_realises',
            'Cas confirmés': 'Cas_confirmes',
            'Taux de positivité (%)': 'Taux_positivite',
            'Traitement approprié': 'Traitement_approprié',
            'Taux de traitement (%)': 'Taux_traitement',
            'GE réalisés': 'GE_realises',
            'GE positifs': 'GE_positifs',
            'Taux positivité GE (%)': 'Taux_positivite_GE',
            'Hospitalisations': 'Hospitalisations',
            'Hospitalisations traitées': 'Hospitalisations_traitees',
            'TDR réalisés': 'TDR_realises',
            'TDR positifs': 'TDR_positifs',
            'Taux positivité TDR (%)': 'Taux_positivite_TDR',
            'Décès': 'Deces'
        }
        cols_acp = st.multiselect(
            "📊 Sélectionnez les variables pour l'ACP (minimum 2)",
            list(variables_acp.keys()),
            default=list(variables_acp.keys())[:5]
        )
        if len(cols_acp) < 2:
            st.info("ℹ️ Sélectionnez au moins 2 variables pour réaliser une ACP.")
        else:
            cols_acp_db = [variables_acp[c] for c in cols_acp]

            df_acp = df.copy()
            for c in cols_acp_db:
                df_acp[c] = pd.to_numeric(df_acp[c], errors='coerce')

            df_acp = df_acp.dropna(subset=cols_acp_db)
            if len(df_acp) < 3:
                st.warning("⚠️ Pas assez de données complètes pour l'ACP (minimum 3 lignes).")
            else:
                # Standardisation
                X = df_acp[cols_acp_db].values
                X_mean = X.mean(axis=0)
                X_std = X.std(axis=0)
                X_std[X_std == 0] = 1
                X_scaled = (X - X_mean) / X_std

                # ACP
                n_comp = min(len(cols_acp_db), 5)
                pca = PCA(n_components=n_comp)
                X_pca = pca.fit_transform(X_scaled)

                # Variance expliquée
                explained_var = pca.explained_variance_ratio_ * 100
                cum_var = np.cumsum(explained_var)

                st.markdown("### 📊 Variance expliquée par les composantes")

                df_var = pd.DataFrame({
                    'Composante': [f"PC{i+1}" for i in range(n_comp)],
                    'Variance expliquée (%)': explained_var,
                    'Variance cumulée (%)': cum_var
                })

                col_v1, col_v2 = st.columns([1, 1])
                with col_v1:
                    st.dataframe(df_var.style.format({
                        'Variance expliquée (%)': '{:.2f}',
                        'Variance cumulée (%)': '{:.2f}'
                    }), use_container_width=True, hide_index=True)

                with col_v2:
                    fig_scree = go.Figure()
                    fig_scree.add_trace(go.Bar(
                        x=df_var['Composante'],
                        y=df_var['Variance expliquée (%)'],
                        name='Variance expliquée',
                        marker_color='#9b59b6',
                        text=df_var['Variance expliquée (%)'].round(1).astype(str) + '%',
                        textposition='outside'
                    ))
                    fig_scree.add_trace(go.Scatter(
                        x=df_var['Composante'],
                        y=df_var['Variance cumulée (%)'],
                        name='Variance cumulée',
                        mode='lines+markers',
                        line=dict(color='#e74c3c', width=3),
                        marker=dict(size=10)
                    ))
                    fig_scree.update_layout(
                        title="Éboulis des valeurs propres",
                        yaxis_title="Pourcentage (%)",
                        height=350,
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig_scree, use_container_width=True)

                # Cercle des corrélations
                st.markdown("### 🎯 Cercle des corrélations (PC1 vs PC2)")

                loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

                fig_circle = go.Figure()

                # Cercle unité
                theta = np.linspace(0, 2 * np.pi, 100)
                fig_circle.add_trace(go.Scatter(
                    x=np.cos(theta), y=np.sin(theta),
                    mode='lines',
                    line=dict(color='black', dash='dash', width=1),
                    name='Cercle unité',
                    showlegend=False
                ))

                # Flèches des variables
                for i, var in enumerate(cols_acp):
                    fig_circle.add_trace(go.Scatter(
                        x=[0, loadings[i, 0]],
                        y=[0, loadings[i, 1]],
                        mode='lines+markers+text',
                        line=dict(width=2, color='#3498db'),
                        marker=dict(size=5),
                        text=[None, var],
                        textposition='top center',
                        name=var,
                        showlegend=False,
                        hovertemplate=f"<b>{var}</b><br>PC1: {loadings[i,0]:.3f}<br>PC2: {loadings[i,1]:.3f}<extra></extra>"
                    ))

                fig_circle.update_layout(
                    title=f"Cercle des corrélations (PC1={explained_var[0]:.1f}% - PC2={explained_var[1] if n_comp>1 else 0:.1f}%)",
                    xaxis=dict(title=f"PC1 ({explained_var[0]:.1f}%)", range=[-1.2, 1.2], zeroline=True),
                    yaxis=dict(title=f"PC2 ({explained_var[1] if n_comp>1 else 0:.1f}%)", range=[-1.2, 1.2], zeroline=True),
                    height=600,
                    showlegend=False
                )
                st.plotly_chart(fig_circle, use_container_width=True)

                # Projection des individus
                st.markdown("### 🗺️ Projection des individus (PC1 vs PC2)")

                df_proj = pd.DataFrame(X_pca[:, :2], columns=['PC1', 'PC2'])
                df_proj['DRS'] = df_acp['DRS'].values if 'DRS' in df_acp.columns else 'Inconnu'
                df_proj['ANNEE'] = df_acp['ANNEE'].values if 'ANNEE' in df_acp.columns else ''
                df_proj['Mois'] = df_acp['Mois'].values if 'Mois' in df_acp.columns else ''

                fig_proj = px.scatter(
                    df_proj, x='PC1', y='PC2',
                    color='DRS',
                    hover_data=['ANNEE', 'Mois'],
                    title=f"Projection des individus (PC1={explained_var[0]:.1f}% - PC2={explained_var[1] if n_comp>1 else 0:.1f}%)"
                )
                fig_proj.update_traces(marker=dict(size=10, opacity=0.7, line=dict(width=1, color='white')))
                fig_proj.update_layout(height=550)
                st.plotly_chart(fig_proj, use_container_width=True)

                # Contributions
                st.markdown("### 📋 Contributions des variables aux deux premiers axes")

                df_loadings = pd.DataFrame(
                    loadings[:, :2],
                    index=cols_acp,
                    columns=['PC1', 'PC2']
                ).reset_index().rename(columns={'index': 'Variable'})

                st.dataframe(
                    df_loadings.style.format({'PC1': '{:.3f}', 'PC2': '{:.3f}'}).background_gradient(
                        cmap='RdBu_r', axis=None
                    ),
                    use_container_width=True,
                    hide_index=True
                )

                # Export ACP
                output_acp = io.BytesIO()
                with pd.ExcelWriter(output_acp, engine='openpyxl') as writer:
                    df_var.to_excel(writer, sheet_name='Variance_expliquee', index=False)
                    df_loadings.to_excel(writer, sheet_name='Contributions', index=False)
                    df_proj.to_excel(writer, sheet_name='Projection_individus', index=False)
                st.download_button(
                    label="📥 Télécharger les résultats ACP (XLSX)",
                    data=output_acp.getvalue(),
                    file_name=f"acp_resultats_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

        # ==========================================
        # MODULE : K-MEANS (K=3)
        # ==========================================
        st.markdown("---")
        st.markdown("""
        <div style="background: linear-gradient(135deg, #e67e22 0%, #f39c12 100%);
                    padding: 1.2rem; border-radius: 12px; color: white; text-align: center; margin: 1rem 0;">
            <h3 style="color: white; margin: 0;">🎯 K-means - Classification non supervisée (K=3)</h3>
            <p style="color: #f0f0f0; margin: 0.3rem 0 0 0;">
                Regroupement des observations en 3 clusters homogènes
            </p>
        </div>
        """, unsafe_allow_html=True)

        variables_km = {
            'Consultations': 'Consultations',
            'Cas suspects': 'Cas_suspects',
            'Tests réalisés': 'Tests_realises',
            'Cas confirmés': 'Cas_confirmes',
            'Taux de positivité (%)': 'Taux_positivite',
            'Traitement approprié': 'Traitement_approprié',
            'Taux de traitement (%)': 'Taux_traitement',
            'GE réalisés': 'GE_realises',
            'GE positifs': 'GE_positifs',
            'Taux positivité GE (%)': 'Taux_positivite_GE',
            'Hospitalisations': 'Hospitalisations',
            'Hospitalisations traitées': 'Hospitalisations_traitees',
            'TDR réalisés': 'TDR_realises',
            'TDR positifs': 'TDR_positifs',
            'Taux positivité TDR (%)': 'Taux_positivite_TDR',
            'Décès': 'Deces'
        }

        cols_km = st.multiselect(
            "📊 Sélectionnez les variables pour K-means (minimum 2)",
            list(variables_km.keys()),
            default=list(variables_km.keys())[:4],
            key='km_vars'
        )

        if len(cols_km) < 2:
            st.info("ℹ️ Sélectionnez au moins 2 variables pour réaliser le K-means.")
        else:
            cols_km_db = [variables_km[c] for c in cols_km]

            df_km = df.copy()
            for c in cols_km_db:
                df_km[c] = pd.to_numeric(df_km[c], errors='coerce')

            df_km = df_km.dropna(subset=cols_km_db)

            if len(df_km) < 3:
                st.warning("⚠️ Pas assez de données complètes pour K-means (minimum 3 lignes).")
            else:
                X_km = df_km[cols_km_db].values
                X_km_mean = X_km.mean(axis=0)
                X_km_std = X_km.std(axis=0)
                X_km_std[X_km_std == 0] = 1
                X_km_scaled = (X_km - X_km_mean) / X_km_std

                kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
                clusters = kmeans.fit_predict(X_km_scaled)

                df_km['Cluster'] = clusters
                df_km['Cluster_Label'] = df_km['Cluster'].apply(lambda x: f"Cluster {x+1}")

                # Silhouette score
                try:
                    from sklearn.metrics import silhouette_score
                    sil_score = silhouette_score(X_km_scaled, clusters) if len(set(clusters)) > 1 else -1
                except Exception:
                    sil_score = -1

                # Statistiques par cluster
                col_k1, col_k2, col_k3, col_k4 = st.columns(4)
                with col_k1:
                    st.metric("🎯 K", 3)
                with col_k2:
                    st.metric("📋 Observations", len(df_km))
                with col_k3:
                    st.metric("📊 Variables", len(cols_km))
                with col_k4:
                    st.metric("📈 Silhouette", f"{sil_score:.3f}" if sil_score >= 0 else "N/A")

                # Aperçu des clusters
                st.markdown("### 📋 Répartition des observations par cluster")

                cluster_counts = df_km['Cluster_Label'].value_counts().sort_index().reset_index()
                cluster_counts.columns = ['Cluster', 'Nombre']

                col_c1, col_c2 = st.columns([1, 1])
                with col_c1:
                    st.dataframe(cluster_counts, use_container_width=True, hide_index=True)
                with col_c2:
                    fig_pie = px.pie(
                        cluster_counts, names='Cluster', values='Nombre',
                        title="Répartition des clusters",
                        color_discrete_sequence=['#e74c3c', '#f39c12', '#27ae60']
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

                # Profils moyens
                st.markdown("### 📊 Profils moyens par cluster")

                profils = df_km.groupby('Cluster_Label')[cols_km_db].mean().round(2).reset_index()
                profils.columns = ['Cluster'] + cols_km

                st.dataframe(
                    profils.style.background_gradient(cmap='YlOrRd', axis=0),
                    use_container_width=True,
                    hide_index=True
                )

                # Visualisation 2D des clusters (PCA)
                if len(cols_km_db) >= 2:
                    pca_km = PCA(n_components=2)
                    X_km_pca = pca_km.fit_transform(X_km_scaled)
                    var_km = pca_km.explained_variance_ratio_ * 100

                    df_km_2d = pd.DataFrame(X_km_pca, columns=['PC1', 'PC2'])
                    df_km_2d['Cluster'] = df_km['Cluster_Label'].values
                    df_km_2d['DRS'] = df_km['DRS'].values if 'DRS' in df_km.columns else 'Inconnu'
                    df_km_2d['ANNEE'] = df_km['ANNEE'].values if 'ANNEE' in df_km.columns else ''
                    df_km_2d['Mois'] = df_km['Mois'].values if 'Mois' in df_km.columns else ''

                    st.markdown("### 🗺️ Visualisation des clusters (ACP 2D)")

                    fig_km = px.scatter(
                        df_km_2d, x='PC1', y='PC2',
                        color='Cluster',
                        symbol='Cluster',
                        hover_data=['DRS', 'ANNEE', 'Mois'],
                        title=f"Clusters K-means projetés sur PC1 ({var_km[0]:.1f}%) et PC2 ({var_km[1]:.1f}%)",
                        color_discrete_sequence=['#e74c3c', '#f39c12', '#27ae60']
                    )
                    fig_km.update_traces(marker=dict(size=12, opacity=0.8, line=dict(width=1, color='white')))
                    fig_km.update_layout(height=600)
                    st.plotly_chart(fig_km, use_container_width=True)

                # Centroïdes
                st.markdown("### 🎯 Centroïdes des clusters (dans l'espace standardisé)")

                centroids = pd.DataFrame(
                    kmeans.cluster_centers_,
                    columns=cols_km
                )
                centroids.insert(0, 'Cluster', [f"Cluster {i+1}" for i in range(3)])

                st.dataframe(
                    centroids.style.format({c: '{:.3f}' for c in cols_km}).background_gradient(
                        cmap='coolwarm', axis=0
                    ),
                    use_container_width=True,
                    hide_index=True
                )

                # Détail des observations par cluster
                st.markdown("### 🔍 Détail des observations par cluster")

                selected_cluster = st.selectbox(
                    "Choisir un cluster à afficher",
                    sorted(df_km['Cluster_Label'].unique()),
                    key='km_cluster_detail'
                )

                df_cluster_detail = df_km[df_km['Cluster_Label'] == selected_cluster]
                st.write(f"**{len(df_cluster_detail)} observation(s)** dans le {selected_cluster}")
                st.dataframe(df_cluster_detail, use_container_width=True)

                # Export K-means
                output_km = io.BytesIO()
                with pd.ExcelWriter(output_km, engine='openpyxl') as writer:
                    profils.to_excel(writer, sheet_name='Profils_moyens', index=False)
                    centroids.to_excel(writer, sheet_name='Centroides', index=False)
                    df_km.to_excel(writer, sheet_name='Observations_clusters', index=False)
                st.download_button(
                    label="📥 Télécharger les résultats K-means (XLSX)",
                    data=output_km.getvalue(),
                    file_name=f"kmeans_resultats_{datetime.now():%Y%m%d_%H%M%S}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        variables_disponibles = {
            'Décès': 'Deces',
            'Cas confirmés': 'Cas_confirmes',
            'Hospitalisations': 'Hospitalisations',
            'Cas suspects': 'Cas_suspects',
            'Consultations': 'Consultations',
            'Tests réalisés': 'Tests_realises',
            'GE positifs': 'GE_positifs',
            'TDR positifs': 'TDR_positifs'
        }
        st.markdown("### 📊 Étape 1 : Choix de la  variables à expliquer (Y)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            variable_dependante_label = st.selectbox( 
                "Choisissez la variable à expliquer",
                list(variables_disponibles.keys()),
                index=0,
                key="model_var_dep"
            )
            variable_dependante = variables_disponibles[variable_dependante_label]
        
        with col2:
            st.markdown(f"""
            <div style="background-color: #e8f4f8; padding: 1rem; border-radius: 10px; height: 100%;">
                <p style="margin: 0; color: #1a5276; font-weight: bold;">❓ Question scientifique</p>
                <p style="margin: 0.5rem 0 0 0; color: #333;">
                    Quels facteurs sont associés au nombre de <strong>{variable_dependante_label.lower()}</strong> liés au paludisme au Sénégal ?
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 📊 Étape 2 : Choix des variables explicatives (X)")
        
        variables_explicatives_possibles = {
            'Cas confirmés': 'Cas_confirmes',
            'Traitement approprié': 'Traitement_approprié',
            'GE positifs': 'GE_positifs',
            'Hospitalisations': 'Hospitalisations',
            'Hospitalisations traitées': 'Hospitalisations_traitees',
            'TDR positifs': 'TDR_positifs',
            'Cas suspects': 'Cas_suspects',
            'Tests réalisés': 'Tests_realises',
            'Consultations': 'Consultations',
            'GE réalisés': 'GE_realises',
            'TDR réalisés': 'TDR_realises',
            'Décès': 'Deces'
        }
        
        variables_explicatives_disponibles = {
            k: v for k, v in variables_explicatives_possibles.items() 
            if v != variable_dependante
        }
        
        variables_par_defaut = []
        if variable_dependante == 'Deces':
            variables_par_defaut = ['Cas confirmés', 'Traitement approprié', 'GE positifs', 
                                    'Hospitalisations', 'Hospitalisations traitées', 'TDR positifs']
        else:
            variables_par_defaut = ['Cas confirmés', 'Hospitalisations', 'TDR positifs'][:3]
        
        variables_par_defaut = [v for v in variables_par_defaut if v in variables_explicatives_disponibles]
        
        variables_explicatives_labels = st.multiselect(
            "Sélectionnez les variables explicatives",
            list(variables_explicatives_disponibles.keys()),
            default=variables_par_defaut,
            key="model_var_expl"
        )
        
        variables_explicatives = [variables_explicatives_disponibles[v] for v in variables_explicatives_labels]
        
        if len(variables_explicatives) == 0:
            st.warning("⚠️ Veuillez sélectionner au moins une variable explicative")
            st.stop()
        
        st.markdown("---")
        
        st.markdown("### 🔍 Étape 3 : Vérification de la dispersion et des zéros")
        
        colonnes_model = [variable_dependante] + variables_explicatives
        model_data_full = df[colonnes_model].copy()
        
        for col in colonnes_model:
            model_data_full[col] = pd.to_numeric(model_data_full[col], errors='coerce')
        
        model_data_full = model_data_full.dropna()
        
        if len(model_data_full) < 10:
            st.error(f"❌ Pas assez d'observations valides ({len(model_data_full)}). Minimum 10 requis.")
        else:
            y_data = model_data_full[variable_dependante]
            moyenne_y = y_data.mean()
            variance_y = y_data.var()
            ratio_dispersion = variance_y / moyenne_y if moyenne_y > 0 else 0
            
            nb_zeros = (y_data == 0).sum()
            pourcentage_zeros = (nb_zeros / len(y_data)) * 100
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(f"Moyenne", f"{moyenne_y:.4f}")
            with col2:
                st.metric(f"Variance", f"{variance_y:.4f}")
            with col3:
                st.metric("Ratio Var/Moy", f"{ratio_dispersion:.4f}")
            with col4:
                st.metric("Zéros (%)", f"{pourcentage_zeros:.1f}%")
            
            st.markdown("#### 📋 Diagnostic des données")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if ratio_dispersion > 1.2:
                    st.markdown(f"""
                    <div class="dispersion-warning">
                        <h4>⚠️ Surdispersion détectée</h4>
                        <p>Ratio Variance/Moyenne = <strong>{ratio_dispersion:.4f} > 1</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="dispersion-ok">
                        <h4>✅ Dispersion équilibrée</h4>
                        <p>Ratio Variance/Moyenne = <strong>{ratio_dispersion:.4f} ≈ 1</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                if pourcentage_zeros > 30:
                    st.markdown(f"""
                    <div class="dispersion-warning">
                        <h4>⚠️ Excès de zéros</h4>
                        <p>Pourcentage de zéros = <strong>{pourcentage_zeros:.1f}% > 30%</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="dispersion-ok">
                        <h4>✅ Zéros normaux</h4>
                        <p>Pourcentage de zéros = <strong>{pourcentage_zeros:.1f}% ≤ 30%</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("### 📊 Étape 4 : Choix du modèle")
            
            st.info("""
            💡 **Choisissez manuellement le modèle à ajuster** :
            - **Binomiale Négative** : Adapté en cas de surdispersion
            - **ZIP (Zero-Inflated Poisson)** : Adapté en cas d'excès de zéros
            """)
            
            modele_choisi = st.radio(
                "Sélectionnez le modèle à ajuster",
                ["Binomiale Négative", "ZIP (Zero-Inflated Poisson)"],
                horizontal=True,
                key="model_choix"
            )
            
            st.markdown("---")
            
            st.markdown(f"### 📊 Distribution de {variable_dependante_label}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_hist = px.histogram(model_data_full, x=variable_dependante, nbins=20,
                                       title=f"Distribution de {variable_dependante_label}",
                                       color_discrete_sequence=['#3498db'])
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                fig_box = px.box(model_data_full, y=variable_dependante,
                                title=f"Boxplot de {variable_dependante_label}",
                                color_discrete_sequence=['#3498db'])
                st.plotly_chart(fig_box, use_container_width=True)
            
            st.markdown("---")
            
            st.markdown(f"### 📈 Étape 5 : Ajustement du modèle - {modele_choisi}")
            
            try:
                X = model_data_full[variables_explicatives]
                X = sm.add_constant(X)
                y = model_data_full[variable_dependante]
                
                if modele_choisi == "Binomiale Négative":
                    model = sm.GLM(y, X, family=sm.families.NegativeBinomial()).fit()
                    
                    st.success(f"✅ Modèle Binomiale Négative ajusté avec succès sur {len(model_data_full)} observations")
                    
                    with st.expander("📋 Voir le résumé complet du modèle", expanded=False):
                        st.text(model.summary().as_text())
                    
                    st.markdown("#### 📊 Coefficients du modèle Binomiale Négative")
                    
                    coef_df = pd.DataFrame({
                        'Variable': model.params.index,
                        'Coefficient': model.params.values.round(4),
                        'Erreur std': model.bse.values.round(4),
                        'z': model.tvalues.values.round(4),
                        'p-value': model.pvalues.values.round(4),
                        'Significatif': ['✅ Oui' if p < 0.05 else '❌ Non' for p in model.pvalues.values]
                    })
                    
                    st.dataframe(coef_df, use_container_width=True)
                    
                    st.markdown("#### 📈 Qualité du modèle")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Déviance", f"{model.deviance:.2f}")
                    with col2:
                        pseudo_r2 = 1 - (model.deviance / model.null_deviance) if model.null_deviance > 0 else 0
                        st.metric("Pseudo R²", f"{pseudo_r2:.4f}")
                    with col3:
                        st.metric("AIC", f"{model.aic:.2f}")
                    
                    if 'modeles_ajustes' not in st.session_state:
                        st.session_state.modeles_ajustes = {}
                    
                    st.session_state.modeles_ajustes['Binomiale Négative'] = {
                        'model': model, 'X': X, 'y': y, 'coef': coef_df,
                        'aic': model.aic, 'bic': model.bic, 'llf': model.llf,
                        'deviance': model.deviance, 'null_deviance': model.null_deviance,
                        'pseudo_r2': pseudo_r2, 'variables': variables_explicatives,
                        'var_dep': variable_dependante
                    }
                    
                else:
                    from statsmodels.discrete.count_model import ZeroInflatedPoisson
                    
                    X_zip = sm.add_constant(model_data_full[variables_explicatives])
                    y_zip = model_data_full[variable_dependante]
                    
                    zip_model = ZeroInflatedPoisson(
                        y_zip, X_zip, exog_infl=X_zip, inflation='logit'
                    ).fit(maxiter=100)
                    
                    st.success(f"✅ Modèle ZIP ajusté avec succès sur {len(model_data_full)} observations")
                    
                    with st.expander("📋 Voir le résumé complet du modèle ZIP", expanded=False):
                        st.text(zip_model.summary().as_text())
                    
                    st.markdown("#### 📊 Coefficients du modèle ZIP")
                    st.markdown("##### 🎯 Partie de comptage (Poisson)")
                    
                    params_poisson = zip_model.params[:len(X_zip.columns)]
                    bse_poisson = zip_model.bse[:len(X_zip.columns)]
                    tvalues_poisson = zip_model.tvalues[:len(X_zip.columns)]
                    pvalues_poisson = zip_model.pvalues[:len(X_zip.columns)]
                    
                    coef_df = pd.DataFrame({
                        'Variable': X_zip.columns,
                        'Coefficient': params_poisson.values.round(4),
                        'Erreur std': bse_poisson.values.round(4),
                        'z': tvalues_poisson.values.round(4),
                        'p-value': pvalues_poisson.values.round(4),
                        'Significatif': ['✅ Oui' if p < 0.05 else '❌ Non' for p in pvalues_poisson.values]
                    })
                    
                    st.dataframe(coef_df, use_container_width=True)
                    
                    st.markdown("##### 🚫 Partie d'inflation de zéro (logistique)")
                    
                    params_infl = zip_model.params[len(X_zip.columns):]
                    bse_infl = zip_model.bse[len(X_zip.columns):]
                    tvalues_infl = zip_model.tvalues[len(X_zip.columns):]
                    pvalues_infl = zip_model.pvalues[len(X_zip.columns):]
                    
                    coef_infl_df = pd.DataFrame({
                        'Variable': X_zip.columns,
                        'Coefficient': params_infl.values.round(4),
                        'Erreur std': bse_infl.values.round(4),
                        'z': tvalues_infl.values.round(4),
                        'p-value': pvalues_infl.values.round(4),
                        'Significatif': ['✅ Oui' if p < 0.05 else '❌ Non' for p in pvalues_infl.values]
                    })
                    
                    st.dataframe(coef_infl_df, use_container_width=True)
                    
                    st.markdown("#### 📈 Qualité du modèle")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Log-vraisemblance", f"{zip_model.llf:.2f}")
                    with col2:
                        pseudo_r2_zip = 1 - (zip_model.llf / zip_model.llnull) if hasattr(zip_model, 'llnull') and zip_model.llnull != 0 else 0
                        st.metric("Pseudo R²", f"{pseudo_r2_zip:.4f}")
                    with col3:
                        st.metric("AIC", f"{zip_model.aic:.2f}")
                    
                    if 'modeles_ajustes' not in st.session_state:
                        st.session_state.modeles_ajustes = {}
                    
                    st.session_state.modeles_ajustes['ZIP'] = {
                        'model': zip_model, 'X': X_zip, 'y': y_zip, 'coef': coef_df,
                        'aic': zip_model.aic, 'bic': zip_model.bic, 'llf': zip_model.llf,
                        'variables': variables_explicatives, 'var_dep': variable_dependante
                    }
                
                if 'modeles_ajustes' in st.session_state and len(st.session_state.modeles_ajustes) == 2:
                    st.markdown("---")
                    st.markdown("### 🔬 Étape 6 : Comparaison des modèles")
                    
                    bn = st.session_state.modeles_ajustes.get('Binomiale Négative', {})
                    zip_m = st.session_state.modeles_ajustes.get('ZIP', {})
                    
                    if bn and zip_m:
                        comparaison_df = pd.DataFrame({
                            'Critère': ['Log-vraisemblance', 'AIC', 'BIC', 'Déviance'],
                            'Binomiale Négative': [
                                f"{bn['llf']:.2f}", f"{bn['aic']:.2f}",
                                f"{bn['bic']:.2f}", f"{bn['deviance']:.2f}"
                            ],
                            'ZIP (Zero-Inflated Poisson)': [
                                f"{zip_m['llf']:.2f}", f"{zip_m['aic']:.2f}",
                                f"{zip_m['bic']:.2f}", "N/A"
                            ]
                        })
                        
                        st.dataframe(comparaison_df, use_container_width=True)
                        
                        aic_bn = bn['aic']
                        aic_zip = zip_m['aic']
                        
                        if aic_zip < aic_bn:
                            modele_prefere = "ZIP (Zero-Inflated Poisson)"
                            justification = "AIC plus faible indique un meilleur ajustement"
                        elif aic_bn < aic_zip:
                            modele_prefere = "Binomiale Négative"
                            justification = "AIC plus faible indique un meilleur ajustement"
                        else:
                            modele_prefere = "Les deux modèles sont équivalents"
                            justification = "AIC identiques"
                        
                        st.markdown(f"""
                        <div class="model-comparison">
                            <h4>🏆 Modèle préféré selon l'AIC</h4>
                            <p><strong>Modèle préféré : {modele_prefere}</strong></p>
                            <p><em>{justification}</em></p>
                            <hr>
                            <p><strong>AIC Binomiale Négative :</strong> {aic_bn:.2f}</p>
                            <p><strong>AIC ZIP :</strong> {aic_zip:.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("### 🎯 Étape 7 : Réponse à la question scientifique")
                
                coef_df_no_const = coef_df[coef_df['Variable'] != 'const']
                signif_vars = coef_df_no_const[coef_df_no_const['p-value'] < 0.05].copy()
                non_signif_vars = coef_df_no_const[coef_df_no_const['p-value'] >= 0.05].copy()
                
                if len(signif_vars) > 0:
                    st.markdown(f"""
                    <div class="conclusion-box">
                        <h3>✅ Réponse : Variables significativement associées</h3>
                        <p>
                            L'analyse avec le modèle <strong>{modele_choisi}</strong> montre que 
                            <strong>{len(signif_vars)} variable(s)</strong> sur 
                            <strong>{len(coef_df_no_const)}</strong> sont statistiquement associées 
                            au nombre de <strong>{variable_dependante_label.lower()}</strong> liés au paludisme au Sénégal.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for _, row in signif_vars.iterrows():
                        var_name = row['Variable']
                        coef = row['Coefficient']
                        p_val = row['p-value']
                        
                        if coef > 0:
                            sens = "⬆️ Relation positive"
                            sens_detail = f"Une augmentation de **{var_name}** est associée à une **augmentation** du nombre de {variable_dependante_label.lower()}."
                        else:
                            sens = "⬇️ Relation négative"
                            sens_detail = f"Une augmentation de **{var_name}** est associée à une **diminution** du nombre de {variable_dependante_label.lower()}."
                        
                        st.markdown(f"""
                        <div class="variable-card variable-signif">
                            <h4>✅ {var_name}</h4>
                            <p><strong>Coefficient :</strong> {coef:.4f}</p>
                            <p><strong>p-value :</strong> {p_val:.4f} (significatif)</p>
                            <p><strong>Interprétation :</strong> {sens}</p>
                            <p>{sens_detail}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="conclusion-box">
                        <h3>📊 Réponse : Aucune association significative</h3>
                        <p>
                            L'analyse ne révèle <strong>aucune variable significativement associée</strong> 
                            au nombre de <strong>{variable_dependante_label.lower()}</strong> au seuil de 5%.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                if len(non_signif_vars) > 0:
                    st.markdown("#### 📌 Variables non significatives (p ≥ 0.05)")
                    
                    for _, row in non_signif_vars.iterrows():
                        var_name = row['Variable']
                        coef = row['Coefficient']
                        p_val = row['p-value']
                        
                        st.markdown(f"""
                        <div class="variable-card variable-non-signif">
                            <h4>❌ {var_name}</h4>
                            <p><strong>Coefficient :</strong> {coef:.4f}</p>
                            <p><strong>p-value :</strong> {p_val:.4f} (non significatif)</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("### 📝 Conclusion statistique")
                
                signif_list = ", ".join(signif_vars['Variable'].tolist()) if len(signif_vars) > 0 else "aucune"
                
                st.markdown(f"""
                <div class="model-box">
                    <h4>🎯 Synthèse de l'analyse</h4>
                    <p><strong>Variable dépendante :</strong> {variable_dependante_label}</p>
                    <p><strong>Modèle utilisé :</strong> {modele_choisi}</p>
                    <p><strong>Nombre d'observations :</strong> {len(model_data_full)}</p>
                    <p><strong>Variables explicatives :</strong> {', '.join(variables_explicatives_labels)}</p>
                    <p><strong>Variables significatives :</strong> {signif_list}</p>
                    <hr>
                    <p style="font-size: 1.05rem;">
                        <strong>Réponse :</strong> Les facteurs significativement associés au nombre de 
                        {variable_dependante_label.lower()} liés au paludisme au Sénégal sont : 
                        <strong>{signif_list if signif_list != 'aucune' else 'aucun facteur identifié'}</strong>.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### 📊 Visualisation des prédictions")
                
                if modele_choisi == "Binomiale Négative":
                    predictions = model.predict(X)
                else:
                    predictions = zip_model.predict(X_zip)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_pred = px.scatter(x=y.values, y=predictions,
                                         labels={'x': 'Valeurs observées', 'y': 'Valeurs prédites'},
                                         title="Valeurs observées vs Valeurs prédites")
                    fig_pred.add_trace(go.Scatter(
                        x=[y.min(), y.max()], y=[y.min(), y.max()],
                        mode='lines', name='Ligne de référence',
                        line=dict(color='red', dash='dash')
                    ))
                    st.plotly_chart(fig_pred, use_container_width=True)
                
                with col2:
                    residuals = y - predictions
                    fig_res = px.scatter(x=predictions, y=residuals,
                                        labels={'x': 'Valeurs prédites', 'y': 'Résidus'},
                                        title="Résidus vs Valeurs prédites")
                    fig_res.add_hline(y=0, line_dash="dash", line_color="red")
                    st.plotly_chart(fig_res, use_container_width=True)
                
                if st.button("🔄 Réinitialiser les modèles ajustés"):
                    if 'modeles_ajustes' in st.session_state:
                        del st.session_state.modeles_ajustes
                    st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erreur lors de l'ajustement du modèle : {e}")
                st.info("""
                💡 **Suggestions** :
                - Vérifiez que les variables sélectionnées sont bien numériques
                - Vérifiez qu'il n'y a pas de valeurs aberrantes extrêmes
                - Essayez avec moins de variables explicatives
                """)

# ===============================
# FIN
# ===============================