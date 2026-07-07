# ===============================
# PLATEFORME SRSD FATICK - VERSION COMPLETE AVEC TOURISME
# ===============================

import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime
from sqlalchemy import create_engine, text

# -------------------------------
# CONFIGURATION
# -------------------------------
st.set_page_config(page_title="Plateforme SRSD FATICK", page_icon="📊", layout="wide")

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
    div[data-testid="stForm"] { border: none; padding: 0; }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# TITRE PRINCIPAL (utilisé sur toutes les pages SAUF Accueil)
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

def get_all_ninea_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM collecte_ninea ORDER BY id", conn)
    conn.close()
    return df

def get_ninea_by_secteur(secteur):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM collecte_ninea WHERE secteur = ? ORDER BY id", conn, params=(secteur,))
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

def update_ninea(data):
    """Met à jour un enregistrement NINEA existant"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE collecte_ninea SET
            nom_complet = ?, cni = ?, sexe = ?, activite_principale = ?,
            regime = ?, forme_juridique = ?, date_depot = ?,
            commune = ?, departement = ?, secteur = ?
        WHERE id = ?
    ''', data)
    conn.commit()
    conn.close()

def delete_ninea_by_id(id_record):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM collecte_ninea WHERE id = ?", (id_record,))
    conn.commit()
    conn.close()

def replace_all_ninea(df):
    delete_all_ninea()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    inserted = 0
    errors = 0
    for _, row in df.iterrows():
        try:
            cursor.execute('''
                INSERT INTO collecte_ninea 
                (nom_complet, cni, sexe, activite_principale, regime, forme_juridique, date_depot, commune, departement, secteur, synchro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            ''', (
                row['nom_complet'], row['cni'], row['sexe'], row['activite_principale'],
                row['regime'], row['forme_juridique'], row['date_depot'], row['commune'], row['departement'],
                row.get('secteur', 'NINEA (Entreprises)')
            ))
            inserted += 1
        except Exception:
            errors += 1
    conn.commit()
    conn.close()
    return inserted, errors

def add_missing_ninea(df):
    conn = sqlite3.connect(DB_PATH)
    existing_cni = set(pd.read_sql_query("SELECT cni FROM collecte_ninea", conn)['cni'].values)
    cursor = conn.cursor()
    inserted = 0
    skipped = 0
    for _, row in df.iterrows():
        if row['cni'] not in existing_cni:
            try:
                cursor.execute('''
                    INSERT INTO collecte_ninea 
                    (nom_complet, cni, sexe, activite_principale, regime, forme_juridique, date_depot, commune, departement, secteur, synchro)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                ''', (
                    row['nom_complet'], row['cni'], row['sexe'], row['activite_principale'],
                    row['regime'], row['forme_juridique'], row['date_depot'], row['commune'], row['departement'],
                    row.get('secteur', 'NINEA (Entreprises)')
                ))
                inserted += 1
                existing_cni.add(row['cni'])
            except Exception:
                skipped += 1
        else:
            skipped += 1
    conn.commit()
    conn.close()
    return inserted, skipped

# -------------------------------
# BASE DE DONNÉES SQLITE POUR TRAVAIL
# -------------------------------
DB_TRAVAIL_PATH = 'collecte_travail.db'

def init_travail_db():
    conn = sqlite3.connect(DB_TRAVAIL_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collecte_travail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            annee INTEGER NOT NULL,
            departement TEXT NOT NULL,
            manoeuvres_hommes INTEGER DEFAULT 0,
            manoeuvres_femmes INTEGER DEFAULT 0,
            employes_hommes INTEGER DEFAULT 0,
            employes_femmes INTEGER DEFAULT 0,
            etablissements_ouverts INTEGER DEFAULT 0,
            etablissements_fermes INTEGER DEFAULT 0,
            ei INTEGER DEFAULT 0,
            sa INTEGER DEFAULT 0,
            sarl INTEGER DEFAULT 0,
            suarl INTEGER DEFAULT 0,
            gie INTEGER DEFAULT 0,
            ong INTEGER DEFAULT 0,
            autres_statuts INTEGER DEFAULT 0,
            emplois_generes INTEGER DEFAULT 0,
            emplois_perdus INTEGER DEFAULT 0,
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
            conflit_indiv_conciliation INTEGER DEFAULT 0,
            conflit_indiv_partielle INTEGER DEFAULT 0,
            conflit_indiv_non INTEGER DEFAULT 0,
            conflit_collectif_conciliation INTEGER DEFAULT 0,
            conflit_collectif_partielle INTEGER DEFAULT 0,
            conflit_collectif_non INTEGER DEFAULT 0,
            synchro INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_all_travail_data():
    conn = sqlite3.connect(DB_TRAVAIL_PATH)
    df = pd.read_sql_query("SELECT * FROM collecte_travail ORDER BY id DESC", conn)
    conn.close()
    return df

def insert_travail(data):
    conn = sqlite3.connect(DB_TRAVAIL_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO collecte_travail (
            annee, departement,
            manoeuvres_hommes, manoeuvres_femmes,
            employes_hommes, employes_femmes,
            etablissements_ouverts, etablissements_fermes,
            ei, sa, sarl, suarl, gie, ong, autres_statuts,
            emplois_generes, emplois_perdus,
            cdi_hommes, cdi_femmes,
            cdd_hommes, cdd_femmes,
            saisonnier_hommes, saisonnier_femmes,
            apprentissage_hommes, apprentissage_femmes,
            temporaire_hommes, temporaire_femmes,
            stage_hommes, stage_femmes,
            conflit_indiv_conciliation, conflit_indiv_partielle, conflit_indiv_non,
            conflit_collectif_conciliation, conflit_collectif_partielle, conflit_collectif_non,
            synchro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    ''', data)
    conn.commit()
    conn.close()

def delete_all_travail():
    conn = sqlite3.connect(DB_TRAVAIL_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM collecte_travail")
    conn.commit()
    conn.close()

def update_travail(data):
    conn = sqlite3.connect(DB_TRAVAIL_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE collecte_travail SET
            annee = ?, departement = ?,
            manoeuvres_hommes = ?, manoeuvres_femmes = ?,
            employes_hommes = ?, employes_femmes = ?,
            etablissements_ouverts = ?, etablissements_fermes = ?,
            ei = ?, sa = ?, sarl = ?, suarl = ?,
            gie = ?, ong = ?, autres_statuts = ?,
            emplois_generes = ?, emplois_perdus = ?,
            cdi_hommes = ?, cdi_femmes = ?,
            cdd_hommes = ?, cdd_femmes = ?,
            saisonnier_hommes = ?, saisonnier_femmes = ?,
            apprentissage_hommes = ?, apprentissage_femmes = ?,
            temporaire_hommes = ?, temporaire_femmes = ?,
            stage_hommes = ?, stage_femmes = ?,
            conflit_indiv_conciliation = ?, conflit_indiv_partielle = ?, conflit_indiv_non = ?,
            conflit_collectif_conciliation = ?, conflit_collectif_partielle = ?, conflit_collectif_non = ?
        WHERE id = ?
    ''', data)
    conn.commit()
    conn.close()

def delete_travail_by_id(id_record):
    conn = sqlite3.connect(DB_TRAVAIL_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM collecte_travail WHERE id = ?", (id_record,))
    conn.commit()
    conn.close()

def replace_all_travail(df):
    delete_all_travail()
    conn = sqlite3.connect(DB_TRAVAIL_PATH)
    cursor = conn.cursor()
    inserted = 0
    errors = 0
    for _, row in df.iterrows():
        try:
            cursor.execute('''
                INSERT INTO collecte_travail (
                    annee, departement,
                    manoeuvres_hommes, manoeuvres_femmes,
                    employes_hommes, employes_femmes,
                    etablissements_ouverts, etablissements_fermes,
                    ei, sa, sarl, suarl, gie, ong, autres_statuts,
                    emplois_generes, emplois_perdus,
                    cdi_hommes, cdi_femmes,
                    cdd_hommes, cdd_femmes,
                    saisonnier_hommes, saisonnier_femmes,
                    apprentissage_hommes, apprentissage_femmes,
                    temporaire_hommes, temporaire_femmes,
                    stage_hommes, stage_femmes,
                    conflit_indiv_conciliation, conflit_indiv_partielle, conflit_indiv_non,
                    conflit_collectif_conciliation, conflit_collectif_partielle, conflit_collectif_non,
                    synchro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            ''', (
                row['annee'], row['departement'],
                row.get('manoeuvres_hommes', 0), row.get('manoeuvres_femmes', 0),
                row.get('employes_hommes', 0), row.get('employes_femmes', 0),
                row.get('etablissements_ouverts', 0), row.get('etablissements_fermes', 0),
                row.get('ei', 0), row.get('sa', 0), row.get('sarl', 0), row.get('suarl', 0),
                row.get('gie', 0), row.get('ong', 0), row.get('autres_statuts', 0),
                row.get('emplois_generes', 0), row.get('emplois_perdus', 0),
                row.get('cdi_hommes', 0), row.get('cdi_femmes', 0),
                row.get('cdd_hommes', 0), row.get('cdd_femmes', 0),
                row.get('saisonnier_hommes', 0), row.get('saisonnier_femmes', 0),
                row.get('apprentissage_hommes', 0), row.get('apprentissage_femmes', 0),
                row.get('temporaire_hommes', 0), row.get('temporaire_femmes', 0),
                row.get('stage_hommes', 0), row.get('stage_femmes', 0),
                row.get('conflit_indiv_conciliation', 0), row.get('conflit_indiv_partielle', 0), row.get('conflit_indiv_non', 0),
                row.get('conflit_collectif_conciliation', 0), row.get('conflit_collectif_partielle', 0), row.get('conflit_collectif_non', 0)
            ))
            inserted += 1
        except Exception:
            errors += 1
    conn.commit()
    conn.close()
    return inserted, errors

def add_missing_travail(df):
    conn = sqlite3.connect(DB_TRAVAIL_PATH)
    cursor = conn.cursor()
    inserted = 0
    skipped = 0
    for _, row in df.iterrows():
        existing = pd.read_sql_query(
            "SELECT id FROM collecte_travail WHERE annee = ? AND departement = ?",
            conn, params=(row['annee'], row['departement'])
        )
        if existing.empty:
            try:
                cursor.execute('''
                    INSERT INTO collecte_travail (
                        annee, departement,
                        manoeuvres_hommes, manoeuvres_femmes,
                        employes_hommes, employes_femmes,
                        etablissements_ouverts, etablissements_fermes,
                        ei, sa, sarl, suarl, gie, ong, autres_statuts,
                        emplois_generes, emplois_perdus,
                        cdi_hommes, cdi_femmes,
                        cdd_hommes, cdd_femmes,
                        saisonnier_hommes, saisonnier_femmes,
                        apprentissage_hommes, apprentissage_femmes,
                        temporaire_hommes, temporaire_femmes,
                        stage_hommes, stage_femmes,
                        conflit_indiv_conciliation, conflit_indiv_partielle, conflit_indiv_non,
                        conflit_collectif_conciliation, conflit_collectif_partielle, conflit_collectif_non,
                        synchro
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                ''', (
                    row['annee'], row['departement'],
                    row.get('manoeuvres_hommes', 0), row.get('manoeuvres_femmes', 0),
                    row.get('employes_hommes', 0), row.get('employes_femmes', 0),
                    row.get('etablissements_ouverts', 0), row.get('etablissements_fermes', 0),
                    row.get('ei', 0), row.get('sa', 0), row.get('sarl', 0), row.get('suarl', 0),
                    row.get('gie', 0), row.get('ong', 0), row.get('autres_statuts', 0),
                    row.get('emplois_generes', 0), row.get('emplois_perdus', 0),
                    row.get('cdi_hommes', 0), row.get('cdi_femmes', 0),
                    row.get('cdd_hommes', 0), row.get('cdd_femmes', 0),
                    row.get('saisonnier_hommes', 0), row.get('saisonnier_femmes', 0),
                    row.get('apprentissage_hommes', 0), row.get('apprentissage_femmes', 0),
                    row.get('temporaire_hommes', 0), row.get('temporaire_femmes', 0),
                    row.get('stage_hommes', 0), row.get('stage_femmes', 0),
                    row.get('conflit_indiv_conciliation', 0), row.get('conflit_indiv_partielle', 0), row.get('conflit_indiv_non', 0),
                    row.get('conflit_collectif_conciliation', 0), row.get('conflit_collectif_partielle', 0), row.get('conflit_collectif_non', 0)
                ))
                inserted += 1
            except Exception:
                skipped += 1
        else:
            skipped += 1
    conn.commit()
    conn.close()
    return inserted, skipped

def mark_travail_synchronized(ids):
    if not ids:
        return
    conn = sqlite3.connect(DB_TRAVAIL_PATH)
    cursor = conn.cursor()
    placeholders = ','.join('?' for _ in ids)
    cursor.execute(f"UPDATE collecte_travail SET synchro = 1 WHERE id IN ({placeholders})", ids)
    conn.commit()
    conn.close()

def get_unsynchronized_travail():
    conn = sqlite3.connect(DB_TRAVAIL_PATH)
    df = pd.read_sql_query("SELECT * FROM collecte_travail WHERE synchro = 0", conn)
    conn.close()
    return df

# -------------------------------
# BASE DE DONNÉES SQLITE POUR ARTISANAT
# -------------------------------
DB_ARTISANAT_PATH = 'collecte_artisanat.db'

def init_artisanat_db():
    conn = sqlite3.connect(DB_ARTISANAT_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collecte_artisanat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            annee INTEGER NOT NULL,
            departement TEXT NOT NULL,
            prod_ei INTEGER DEFAULT 0,
            prod_gie INTEGER DEFAULT 0,
            service_ei INTEGER DEFAULT 0,
            service_gie INTEGER DEFAULT 0,
            art_ei INTEGER DEFAULT 0,
            art_gie INTEGER DEFAULT 0,
            synchro INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_all_artisanat_data():
    conn = sqlite3.connect(DB_ARTISANAT_PATH)
    df = pd.read_sql_query("SELECT * FROM collecte_artisanat ORDER BY id DESC", conn)
    conn.close()
    return df

def insert_artisanat(data):
    conn = sqlite3.connect(DB_ARTISANAT_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO collecte_artisanat (
            annee, departement,
            prod_ei, prod_gie,
            service_ei, service_gie,
            art_ei, art_gie,
            synchro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    ''', data)
    conn.commit()
    conn.close()

def delete_all_artisanat():
    conn = sqlite3.connect(DB_ARTISANAT_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM collecte_artisanat")
    conn.commit()
    conn.close()

def update_artisanat(data):
    conn = sqlite3.connect(DB_ARTISANAT_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE collecte_artisanat SET
            annee = ?, departement = ?,
            prod_ei = ?, prod_gie = ?,
            service_ei = ?, service_gie = ?,
            art_ei = ?, art_gie = ?
        WHERE id = ?
    ''', data)
    conn.commit()
    conn.close()

def delete_artisanat_by_id(id_record):
    conn = sqlite3.connect(DB_ARTISANAT_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM collecte_artisanat WHERE id = ?", (id_record,))
    conn.commit()
    conn.close()

def replace_all_artisanat(df):
    delete_all_artisanat()
    conn = sqlite3.connect(DB_ARTISANAT_PATH)
    cursor = conn.cursor()
    inserted = 0
    errors = 0
    for _, row in df.iterrows():
        try:
            cursor.execute('''
                INSERT INTO collecte_artisanat (
                    annee, departement,
                    prod_ei, prod_gie,
                    service_ei, service_gie,
                    art_ei, art_gie,
                    synchro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            ''', (
                row['annee'], row['departement'],
                row.get('prod_ei', 0), row.get('prod_gie', 0),
                row.get('service_ei', 0), row.get('service_gie', 0),
                row.get('art_ei', 0), row.get('art_gie', 0)
            ))
            inserted += 1
        except Exception:
            errors += 1
    conn.commit()
    conn.close()
    return inserted, errors

def add_missing_artisanat(df):
    conn = sqlite3.connect(DB_ARTISANAT_PATH)
    cursor = conn.cursor()
    inserted = 0
    skipped = 0
    for _, row in df.iterrows():
        existing = pd.read_sql_query(
            "SELECT id FROM collecte_artisanat WHERE annee = ? AND departement = ?",
            conn, params=(row['annee'], row['departement'])
        )
        if existing.empty:
            try:
                cursor.execute('''
                    INSERT INTO collecte_artisanat (
                        annee, departement,
                        prod_ei, prod_gie,
                        service_ei, service_gie,
                        art_ei, art_gie,
                        synchro
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                ''', (
                    row['annee'], row['departement'],
                    row.get('prod_ei', 0), row.get('prod_gie', 0),
                    row.get('service_ei', 0), row.get('service_gie', 0),
                    row.get('art_ei', 0), row.get('art_gie', 0)
                ))
                inserted += 1
            except Exception:
                skipped += 1
        else:
            skipped += 1
    conn.commit()
    conn.close()
    return inserted, skipped

def mark_artisanat_synchronized(ids):
    if not ids:
        return
    conn = sqlite3.connect(DB_ARTISANAT_PATH)
    cursor = conn.cursor()
    placeholders = ','.join('?' for _ in ids)
    cursor.execute(f"UPDATE collecte_artisanat SET synchro = 1 WHERE id IN ({placeholders})", ids)
    conn.commit()
    conn.close()

def get_unsynchronized_artisanat():
    conn = sqlite3.connect(DB_ARTISANAT_PATH)
    df = pd.read_sql_query("SELECT * FROM collecte_artisanat WHERE synchro = 0", conn)
    conn.close()
    return df

# -------------------------------
# BASE DE DONNÉES SQLITE POUR TOURISME
# -------------------------------
DB_TOURISME_PATH = 'collecte_tourisme.db'

def init_tourisme_db():
    conn = sqlite3.connect(DB_TOURISME_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS collecte_tourisme (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            annee INTEGER NOT NULL,
            departement TEXT NOT NULL,
            
            -- Bloc A - Infrastructures (Tableau 19.1)
            hotel_receptifs INTEGER DEFAULT 0,
            hotel_chambres INTEGER DEFAULT 0,
            hotel_lits INTEGER DEFAULT 0,
            auberge_receptifs INTEGER DEFAULT 0,
            auberge_chambres INTEGER DEFAULT 0,
            auberge_lits INTEGER DEFAULT 0,
            campement_touristique_receptifs INTEGER DEFAULT 0,
            campement_touristique_chambres INTEGER DEFAULT 0,
            campement_touristique_lits INTEGER DEFAULT 0,
            campement_chasse_receptifs INTEGER DEFAULT 0,
            campement_chasse_chambres INTEGER DEFAULT 0,
            campement_chasse_lits INTEGER DEFAULT 0,
            relais_receptifs INTEGER DEFAULT 0,
            relais_chambres INTEGER DEFAULT 0,
            relais_lits INTEGER DEFAULT 0,
            gite_receptifs INTEGER DEFAULT 0,
            gite_chambres INTEGER DEFAULT 0,
            gite_lits INTEGER DEFAULT 0,
            lodge_receptifs INTEGER DEFAULT 0,
            lodge_chambres INTEGER DEFAULT 0,
            lodge_lits INTEGER DEFAULT 0,
            centre_accueil_receptifs INTEGER DEFAULT 0,
            centre_accueil_chambres INTEGER DEFAULT 0,
            centre_accueil_lits INTEGER DEFAULT 0,
            
            -- Bloc B - Arrivées par provenance (Tableau 19.2)
            france INTEGER DEFAULT 0,
            autres_pays_europeens INTEGER DEFAULT 0,
            usa INTEGER DEFAULT 0,
            autres_pays_americains INTEGER DEFAULT 0,
            senegal INTEGER DEFAULT 0,
            autres_pays_africains INTEGER DEFAULT 0,
            asie INTEGER DEFAULT 0,
            oceanie INTEGER DEFAULT 0,
            
            -- Bloc C - Occupation (Tableau 19.3)
            hotel_nuitees INTEGER DEFAULT 0,
            hotel_taux_occupation REAL DEFAULT 0,
            auberge_nuitees INTEGER DEFAULT 0,
            auberge_taux_occupation REAL DEFAULT 0,
            campement_touristique_nuitees INTEGER DEFAULT 0,
            campement_touristique_taux_occupation REAL DEFAULT 0,
            campement_chasse_nuitees INTEGER DEFAULT 0,
            campement_chasse_taux_occupation REAL DEFAULT 0,
            relais_nuitees INTEGER DEFAULT 0,
            relais_taux_occupation REAL DEFAULT 0,
            gite_nuitees INTEGER DEFAULT 0,
            gite_taux_occupation REAL DEFAULT 0,
            lodge_nuitees INTEGER DEFAULT 0,
            lodge_taux_occupation REAL DEFAULT 0,
            centre_accueil_nuitees INTEGER DEFAULT 0,
            centre_accueil_taux_occupation REAL DEFAULT 0,
            
            synchro INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def get_all_tourisme_data():
    conn = sqlite3.connect(DB_TOURISME_PATH)
    df = pd.read_sql_query("SELECT * FROM collecte_tourisme ORDER BY id DESC", conn)
    conn.close()
    return df

def insert_tourisme(data):
    conn = sqlite3.connect(DB_TOURISME_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO collecte_tourisme (
            annee, departement,
            hotel_receptifs, hotel_chambres, hotel_lits,
            auberge_receptifs, auberge_chambres, auberge_lits,
            campement_touristique_receptifs, campement_touristique_chambres, campement_touristique_lits,
            campement_chasse_receptifs, campement_chasse_chambres, campement_chasse_lits,
            relais_receptifs, relais_chambres, relais_lits,
            gite_receptifs, gite_chambres, gite_lits,
            lodge_receptifs, lodge_chambres, lodge_lits,
            centre_accueil_receptifs, centre_accueil_chambres, centre_accueil_lits,
            france, autres_pays_europeens, usa, autres_pays_americains, senegal, autres_pays_africains, asie, oceanie,
            hotel_nuitees, hotel_taux_occupation,
            auberge_nuitees, auberge_taux_occupation,
            campement_touristique_nuitees, campement_touristique_taux_occupation,
            campement_chasse_nuitees, campement_chasse_taux_occupation,
            relais_nuitees, relais_taux_occupation,
            gite_nuitees, gite_taux_occupation,
            lodge_nuitees, lodge_taux_occupation,
            centre_accueil_nuitees, centre_accueil_taux_occupation,
            synchro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    ''', data)
    conn.commit()
    conn.close()

def delete_all_tourisme():
    conn = sqlite3.connect(DB_TOURISME_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM collecte_tourisme")
    conn.commit()
    conn.close()

def update_tourisme(data):
    conn = sqlite3.connect(DB_TOURISME_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE collecte_tourisme SET
            annee = ?, departement = ?,
            hotel_receptifs = ?, hotel_chambres = ?, hotel_lits = ?,
            auberge_receptifs = ?, auberge_chambres = ?, auberge_lits = ?,
            campement_touristique_receptifs = ?, campement_touristique_chambres = ?, campement_touristique_lits = ?,
            campement_chasse_receptifs = ?, campement_chasse_chambres = ?, campement_chasse_lits = ?,
            relais_receptifs = ?, relais_chambres = ?, relais_lits = ?,
            gite_receptifs = ?, gite_chambres = ?, gite_lits = ?,
            lodge_receptifs = ?, lodge_chambres = ?, lodge_lits = ?,
            centre_accueil_receptifs = ?, centre_accueil_chambres = ?, centre_accueil_lits = ?,
            france = ?, autres_pays_europeens = ?, usa = ?, autres_pays_americains = ?, senegal = ?, autres_pays_africains = ?, asie = ?, oceanie = ?,
            hotel_nuitees = ?, hotel_taux_occupation = ?,
            auberge_nuitees = ?, auberge_taux_occupation = ?,
            campement_touristique_nuitees = ?, campement_touristique_taux_occupation = ?,
            campement_chasse_nuitees = ?, campement_chasse_taux_occupation = ?,
            relais_nuitees = ?, relais_taux_occupation = ?,
            gite_nuitees = ?, gite_taux_occupation = ?,
            lodge_nuitees = ?, lodge_taux_occupation = ?,
            centre_accueil_nuitees = ?, centre_accueil_taux_occupation = ?
        WHERE id = ?
    ''', data)
    conn.commit()
    conn.close()

def delete_tourisme_by_id(id_record):
    conn = sqlite3.connect(DB_TOURISME_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM collecte_tourisme WHERE id = ?", (id_record,))
    conn.commit()
    conn.close()

def replace_all_tourisme(df):
    delete_all_tourisme()
    conn = sqlite3.connect(DB_TOURISME_PATH)
    cursor = conn.cursor()
    inserted = 0
    errors = 0
    for _, row in df.iterrows():
        try:
            cursor.execute('''
                INSERT INTO collecte_tourisme (
                    annee, departement,
                    hotel_receptifs, hotel_chambres, hotel_lits,
                    auberge_receptifs, auberge_chambres, auberge_lits,
                    campement_touristique_receptifs, campement_touristique_chambres, campement_touristique_lits,
                    campement_chasse_receptifs, campement_chasse_chambres, campement_chasse_lits,
                    relais_receptifs, relais_chambres, relais_lits,
                    gite_receptifs, gite_chambres, gite_lits,
                    lodge_receptifs, lodge_chambres, lodge_lits,
                    centre_accueil_receptifs, centre_accueil_chambres, centre_accueil_lits,
                    france, autres_pays_europeens, usa, autres_pays_americains, senegal, autres_pays_africains, asie, oceanie,
                    hotel_nuitees, hotel_taux_occupation,
                    auberge_nuitees, auberge_taux_occupation,
                    campement_touristique_nuitees, campement_touristique_taux_occupation,
                    campement_chasse_nuitees, campement_chasse_taux_occupation,
                    relais_nuitees, relais_taux_occupation,
                    gite_nuitees, gite_taux_occupation,
                    lodge_nuitees, lodge_taux_occupation,
                    centre_accueil_nuitees, centre_accueil_taux_occupation,
                    synchro
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            ''', (
                row['annee'], row['departement'],
                row.get('hotel_receptifs', 0), row.get('hotel_chambres', 0), row.get('hotel_lits', 0),
                row.get('auberge_receptifs', 0), row.get('auberge_chambres', 0), row.get('auberge_lits', 0),
                row.get('campement_touristique_receptifs', 0), row.get('campement_touristique_chambres', 0), row.get('campement_touristique_lits', 0),
                row.get('campement_chasse_receptifs', 0), row.get('campement_chasse_chambres', 0), row.get('campement_chasse_lits', 0),
                row.get('relais_receptifs', 0), row.get('relais_chambres', 0), row.get('relais_lits', 0),
                row.get('gite_receptifs', 0), row.get('gite_chambres', 0), row.get('gite_lits', 0),
                row.get('lodge_receptifs', 0), row.get('lodge_chambres', 0), row.get('lodge_lits', 0),
                row.get('centre_accueil_receptifs', 0), row.get('centre_accueil_chambres', 0), row.get('centre_accueil_lits', 0),
                row.get('france', 0), row.get('autres_pays_europeens', 0), row.get('usa', 0), row.get('autres_pays_americains', 0),
                row.get('senegal', 0), row.get('autres_pays_africains', 0), row.get('asie', 0), row.get('oceanie', 0),
                row.get('hotel_nuitees', 0), row.get('hotel_taux_occupation', 0),
                row.get('auberge_nuitees', 0), row.get('auberge_taux_occupation', 0),
                row.get('campement_touristique_nuitees', 0), row.get('campement_touristique_taux_occupation', 0),
                row.get('campement_chasse_nuitees', 0), row.get('campement_chasse_taux_occupation', 0),
                row.get('relais_nuitees', 0), row.get('relais_taux_occupation', 0),
                row.get('gite_nuitees', 0), row.get('gite_taux_occupation', 0),
                row.get('lodge_nuitees', 0), row.get('lodge_taux_occupation', 0),
                row.get('centre_accueil_nuitees', 0), row.get('centre_accueil_taux_occupation', 0)
            ))
            inserted += 1
        except Exception:
            errors += 1
    conn.commit()
    conn.close()
    return inserted, errors

def add_missing_tourisme(df):
    conn = sqlite3.connect(DB_TOURISME_PATH)
    cursor = conn.cursor()
    inserted = 0
    skipped = 0
    for _, row in df.iterrows():
        existing = pd.read_sql_query(
            "SELECT id FROM collecte_tourisme WHERE annee = ? AND departement = ?",
            conn, params=(row['annee'], row['departement'])
        )
        if existing.empty:
            try:
                cursor.execute('''
                    INSERT INTO collecte_tourisme (
                        annee, departement,
                        hotel_receptifs, hotel_chambres, hotel_lits,
                        auberge_receptifs, auberge_chambres, auberge_lits,
                        campement_touristique_receptifs, campement_touristique_chambres, campement_touristique_lits,
                        campement_chasse_receptifs, campement_chasse_chambres, campement_chasse_lits,
                        relais_receptifs, relais_chambres, relais_lits,
                        gite_receptifs, gite_chambres, gite_lits,
                        lodge_receptifs, lodge_chambres, lodge_lits,
                        centre_accueil_receptifs, centre_accueil_chambres, centre_accueil_lits,
                        france, autres_pays_europeens, usa, autres_pays_americains, senegal, autres_pays_africains, asie, oceanie,
                        hotel_nuitees, hotel_taux_occupation,
                        auberge_nuitees, auberge_taux_occupation,
                        campement_touristique_nuitees, campement_touristique_taux_occupation,
                        campement_chasse_nuitees, campement_chasse_taux_occupation,
                        relais_nuitees, relais_taux_occupation,
                        gite_nuitees, gite_taux_occupation,
                        lodge_nuitees, lodge_taux_occupation,
                        centre_accueil_nuitees, centre_accueil_taux_occupation,
                        synchro
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
                ''', (
                    row['annee'], row['departement'],
                    row.get('hotel_receptifs', 0), row.get('hotel_chambres', 0), row.get('hotel_lits', 0),
                    row.get('auberge_receptifs', 0), row.get('auberge_chambres', 0), row.get('auberge_lits', 0),
                    row.get('campement_touristique_receptifs', 0), row.get('campement_touristique_chambres', 0), row.get('campement_touristique_lits', 0),
                    row.get('campement_chasse_receptifs', 0), row.get('campement_chasse_chambres', 0), row.get('campement_chasse_lits', 0),
                    row.get('relais_receptifs', 0), row.get('relais_chambres', 0), row.get('relais_lits', 0),
                    row.get('gite_receptifs', 0), row.get('gite_chambres', 0), row.get('gite_lits', 0),
                    row.get('lodge_receptifs', 0), row.get('lodge_chambres', 0), row.get('lodge_lits', 0),
                    row.get('centre_accueil_receptifs', 0), row.get('centre_accueil_chambres', 0), row.get('centre_accueil_lits', 0),
                    row.get('france', 0), row.get('autres_pays_europeens', 0), row.get('usa', 0), row.get('autres_pays_americains', 0),
                    row.get('senegal', 0), row.get('autres_pays_africains', 0), row.get('asie', 0), row.get('oceanie', 0),
                    row.get('hotel_nuitees', 0), row.get('hotel_taux_occupation', 0),
                    row.get('auberge_nuitees', 0), row.get('auberge_taux_occupation', 0),
                    row.get('campement_touristique_nuitees', 0), row.get('campement_touristique_taux_occupation', 0),
                    row.get('campement_chasse_nuitees', 0), row.get('campement_chasse_taux_occupation', 0),
                    row.get('relais_nuitees', 0), row.get('relais_taux_occupation', 0),
                    row.get('gite_nuitees', 0), row.get('gite_taux_occupation', 0),
                    row.get('lodge_nuitees', 0), row.get('lodge_taux_occupation', 0),
                    row.get('centre_accueil_nuitees', 0), row.get('centre_accueil_taux_occupation', 0)
                ))
                inserted += 1
            except Exception:
                skipped += 1
        else:
            skipped += 1
    conn.commit()
    conn.close()
    return inserted, skipped

def mark_tourisme_synchronized(ids):
    if not ids:
        return
    conn = sqlite3.connect(DB_TOURISME_PATH)
    cursor = conn.cursor()
    placeholders = ','.join('?' for _ in ids)
    cursor.execute(f"UPDATE collecte_tourisme SET synchro = 1 WHERE id IN ({placeholders})", ids)
    conn.commit()
    conn.close()

def get_unsynchronized_tourisme():
    conn = sqlite3.connect(DB_TOURISME_PATH)
    df = pd.read_sql_query("SELECT * FROM collecte_tourisme WHERE synchro = 0", conn)
    conn.close()
    return df

# Initialisation des bases
init_ninea_db()
init_travail_db()
init_artisanat_db()
init_tourisme_db()

# -------------------------------
# CONNEXION POSTGRESQL (synchronisation)
# -------------------------------
@st.cache_resource
def get_postgres_engine():
    return create_engine("postgresql+psycopg2://postgres:ansdfatick@localhost:5432/ANSD_FATICK")

def init_postgres_travail_table():
    try:
        engine = get_postgres_engine()
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS travail (
                    id SERIAL PRIMARY KEY,
                    annee INTEGER NOT NULL,
                    departement TEXT NOT NULL,
                    manoeuvres_hommes INTEGER DEFAULT 0,
                    manoeuvres_femmes INTEGER DEFAULT 0,
                    employes_hommes INTEGER DEFAULT 0,
                    employes_femmes INTEGER DEFAULT 0,
                    etablissements_ouverts INTEGER DEFAULT 0,
                    etablissements_fermes INTEGER DEFAULT 0,
                    ei INTEGER DEFAULT 0,
                    sa INTEGER DEFAULT 0,
                    sarl INTEGER DEFAULT 0,
                    suarl INTEGER DEFAULT 0,
                    gie INTEGER DEFAULT 0,
                    ong INTEGER DEFAULT 0,
                    autres_statuts INTEGER DEFAULT 0,
                    emplois_generes INTEGER DEFAULT 0,
                    emplois_perdus INTEGER DEFAULT 0,
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
                    conflit_indiv_conciliation INTEGER DEFAULT 0,
                    conflit_indiv_partielle INTEGER DEFAULT 0,
                    conflit_indiv_non INTEGER DEFAULT 0,
                    conflit_collectif_conciliation INTEGER DEFAULT 0,
                    conflit_collectif_partielle INTEGER DEFAULT 0,
                    conflit_collectif_non INTEGER DEFAULT 0,
                    date_synchronisation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
        return True
    except Exception as e:
        st.warning(f"⚠️ PostgreSQL indisponible pour travail : {e}")
        return False

def init_postgres_artisanat_table():
    try:
        engine = get_postgres_engine()
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS artisanat (
                    id SERIAL PRIMARY KEY,
                    annee INTEGER NOT NULL,
                    departement TEXT NOT NULL,
                    prod_ei INTEGER DEFAULT 0,
                    prod_gie INTEGER DEFAULT 0,
                    service_ei INTEGER DEFAULT 0,
                    service_gie INTEGER DEFAULT 0,
                    art_ei INTEGER DEFAULT 0,
                    art_gie INTEGER DEFAULT 0,
                    date_synchronisation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
        return True
    except Exception as e:
        st.warning(f"⚠️ PostgreSQL indisponible pour artisanat : {e}")
        return False

def init_postgres_tourisme_table():
    try:
        engine = get_postgres_engine()
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS tourisme (
                    id SERIAL PRIMARY KEY,
                    annee INTEGER NOT NULL,
                    departement TEXT NOT NULL,
                    hotel_receptifs INTEGER DEFAULT 0,
                    hotel_chambres INTEGER DEFAULT 0,
                    hotel_lits INTEGER DEFAULT 0,
                    auberge_receptifs INTEGER DEFAULT 0,
                    auberge_chambres INTEGER DEFAULT 0,
                    auberge_lits INTEGER DEFAULT 0,
                    campement_touristique_receptifs INTEGER DEFAULT 0,
                    campement_touristique_chambres INTEGER DEFAULT 0,
                    campement_touristique_lits INTEGER DEFAULT 0,
                    campement_chasse_receptifs INTEGER DEFAULT 0,
                    campement_chasse_chambres INTEGER DEFAULT 0,
                    campement_chasse_lits INTEGER DEFAULT 0,
                    relais_receptifs INTEGER DEFAULT 0,
                    relais_chambres INTEGER DEFAULT 0,
                    relais_lits INTEGER DEFAULT 0,
                    gite_receptifs INTEGER DEFAULT 0,
                    gite_chambres INTEGER DEFAULT 0,
                    gite_lits INTEGER DEFAULT 0,
                    lodge_receptifs INTEGER DEFAULT 0,
                    lodge_chambres INTEGER DEFAULT 0,
                    lodge_lits INTEGER DEFAULT 0,
                    centre_accueil_receptifs INTEGER DEFAULT 0,
                    centre_accueil_chambres INTEGER DEFAULT 0,
                    centre_accueil_lits INTEGER DEFAULT 0,
                    france INTEGER DEFAULT 0,
                    autres_pays_europeens INTEGER DEFAULT 0,
                    usa INTEGER DEFAULT 0,
                    autres_pays_americains INTEGER DEFAULT 0,
                    senegal INTEGER DEFAULT 0,
                    autres_pays_africains INTEGER DEFAULT 0,
                    asie INTEGER DEFAULT 0,
                    oceanie INTEGER DEFAULT 0,
                    hotel_nuitees INTEGER DEFAULT 0,
                    hotel_taux_occupation REAL DEFAULT 0,
                    auberge_nuitees INTEGER DEFAULT 0,
                    auberge_taux_occupation REAL DEFAULT 0,
                    campement_touristique_nuitees INTEGER DEFAULT 0,
                    campement_touristique_taux_occupation REAL DEFAULT 0,
                    campement_chasse_nuitees INTEGER DEFAULT 0,
                    campement_chasse_taux_occupation REAL DEFAULT 0,
                    relais_nuitees INTEGER DEFAULT 0,
                    relais_taux_occupation REAL DEFAULT 0,
                    gite_nuitees INTEGER DEFAULT 0,
                    gite_taux_occupation REAL DEFAULT 0,
                    lodge_nuitees INTEGER DEFAULT 0,
                    lodge_taux_occupation REAL DEFAULT 0,
                    centre_accueil_nuitees INTEGER DEFAULT 0,
                    centre_accueil_taux_occupation REAL DEFAULT 0,
                    date_synchronisation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
        return True
    except Exception as e:
        st.warning(f"⚠️ PostgreSQL indisponible pour tourisme : {e}")
        return False

def synchroniser_travail_vers_postgresql():
    try:
        df_non_sync = get_unsynchronized_travail()
    except Exception as e:
        return 0, 0, 0, f"Erreur lecture SQLite travail : {e}"
    
    if df_non_sync.empty:
        return 0, 0, 0, None
    
    try:
        engine = get_postgres_engine()
    except Exception as e:
        return 0, 0, 0, f"Erreur connexion PostgreSQL : {e}"
    
    inserted = 0
    skipped = 0
    errors = 0
    synced_ids = []
    
    for _, row in df_non_sync.iterrows():
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT COUNT(*) FROM travail WHERE annee = :annee AND departement = :departement"),
                    {"annee": row['annee'], "departement": row['departement']}
                )
                exists = result.scalar()
            
            if exists == 0:
                with engine.connect() as conn:
                    conn.execute(
                        text("""
                            INSERT INTO travail (
                                annee, departement,
                                manoeuvres_hommes, manoeuvres_femmes,
                                employes_hommes, employes_femmes,
                                etablissements_ouverts, etablissements_fermes,
                                ei, sa, sarl, suarl, gie, ong, autres_statuts,
                                emplois_generes, emplois_perdus,
                                cdi_hommes, cdi_femmes,
                                cdd_hommes, cdd_femmes,
                                saisonnier_hommes, saisonnier_femmes,
                                apprentissage_hommes, apprentissage_femmes,
                                temporaire_hommes, temporaire_femmes,
                                stage_hommes, stage_femmes,
                                conflit_indiv_conciliation, conflit_indiv_partielle, conflit_indiv_non,
                                conflit_collectif_conciliation, conflit_collectif_partielle, conflit_collectif_non
                            ) VALUES (
                                :annee, :departement,
                                :manoeuvres_hommes, :manoeuvres_femmes,
                                :employes_hommes, :employes_femmes,
                                :etablissements_ouverts, :etablissements_fermes,
                                :ei, :sa, :sarl, :suarl, :gie, :ong, :autres_statuts,
                                :emplois_generes, :emplois_perdus,
                                :cdi_hommes, :cdi_femmes,
                                :cdd_hommes, :cdd_femmes,
                                :saisonnier_hommes, :saisonnier_femmes,
                                :apprentissage_hommes, :apprentissage_femmes,
                                :temporaire_hommes, :temporaire_femmes,
                                :stage_hommes, :stage_femmes,
                                :conflit_indiv_conciliation, :conflit_indiv_partielle, :conflit_indiv_non,
                                :conflit_collectif_conciliation, :conflit_collectif_partielle, :conflit_collectif_non
                            )
                        """),
                        {
                            "annee": row['annee'], "departement": row['departement'],
                            "manoeuvres_hommes": row['manoeuvres_hommes'], "manoeuvres_femmes": row['manoeuvres_femmes'],
                            "employes_hommes": row['employes_hommes'], "employes_femmes": row['employes_femmes'],
                            "etablissements_ouverts": row['etablissements_ouverts'], "etablissements_fermes": row['etablissements_fermes'],
                            "ei": row['ei'], "sa": row['sa'], "sarl": row['sarl'], "suarl": row['suarl'],
                            "gie": row['gie'], "ong": row['ong'], "autres_statuts": row['autres_statuts'],
                            "emplois_generes": row['emplois_generes'], "emplois_perdus": row['emplois_perdus'],
                            "cdi_hommes": row['cdi_hommes'], "cdi_femmes": row['cdi_femmes'],
                            "cdd_hommes": row['cdd_hommes'], "cdd_femmes": row['cdd_femmes'],
                            "saisonnier_hommes": row['saisonnier_hommes'], "saisonnier_femmes": row['saisonnier_femmes'],
                            "apprentissage_hommes": row['apprentissage_hommes'], "apprentissage_femmes": row['apprentissage_femmes'],
                            "temporaire_hommes": row['temporaire_hommes'], "temporaire_femmes": row['temporaire_femmes'],
                            "stage_hommes": row['stage_hommes'], "stage_femmes": row['stage_femmes'],
                            "conflit_indiv_conciliation": row['conflit_indiv_conciliation'],
                            "conflit_indiv_partielle": row['conflit_indiv_partielle'],
                            "conflit_indiv_non": row['conflit_indiv_non'],
                            "conflit_collectif_conciliation": row['conflit_collectif_conciliation'],
                            "conflit_collectif_partielle": row['conflit_collectif_partielle'],
                            "conflit_collectif_non": row['conflit_collectif_non']
                        }
                    )
                    conn.commit()
                inserted += 1
                synced_ids.append(row['id'])
            else:
                skipped += 1
                synced_ids.append(row['id'])
        except Exception as e:
            errors += 1
    
    if synced_ids:
        mark_travail_synchronized(synced_ids)
    
    return inserted, skipped, errors, None

def synchroniser_artisanat_vers_postgresql():
    try:
        df_non_sync = get_unsynchronized_artisanat()
    except Exception as e:
        return 0, 0, 0, f"Erreur lecture SQLite artisanat : {e}"
    
    if df_non_sync.empty:
        return 0, 0, 0, None
    
    try:
        engine = get_postgres_engine()
    except Exception as e:
        return 0, 0, 0, f"Erreur connexion PostgreSQL : {e}"
    
    inserted = 0
    skipped = 0
    errors = 0
    synced_ids = []
    
    for _, row in df_non_sync.iterrows():
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT COUNT(*) FROM artisanat WHERE annee = :annee AND departement = :departement"),
                    {"annee": row['annee'], "departement": row['departement']}
                )
                exists = result.scalar()
            
            if exists == 0:
                with engine.connect() as conn:
                    conn.execute(
                        text("""
                            INSERT INTO artisanat (
                                annee, departement,
                                prod_ei, prod_gie,
                                service_ei, service_gie,
                                art_ei, art_gie
                            ) VALUES (
                                :annee, :departement,
                                :prod_ei, :prod_gie,
                                :service_ei, :service_gie,
                                :art_ei, :art_gie
                            )
                        """),
                        {
                            "annee": row['annee'], "departement": row['departement'],
                            "prod_ei": row['prod_ei'], "prod_gie": row['prod_gie'],
                            "service_ei": row['service_ei'], "service_gie": row['service_gie'],
                            "art_ei": row['art_ei'], "art_gie": row['art_gie']
                        }
                    )
                    conn.commit()
                inserted += 1
                synced_ids.append(row['id'])
            else:
                skipped += 1
                synced_ids.append(row['id'])
        except Exception as e:
            errors += 1
    
    if synced_ids:
        mark_artisanat_synchronized(synced_ids)
    
    return inserted, skipped, errors, None

def synchroniser_tourisme_vers_postgresql():
    try:
        df_non_sync = get_unsynchronized_tourisme()
    except Exception as e:
        return 0, 0, 0, f"Erreur lecture SQLite tourisme : {e}"
    
    if df_non_sync.empty:
        return 0, 0, 0, None
    
    try:
        engine = get_postgres_engine()
    except Exception as e:
        return 0, 0, 0, f"Erreur connexion PostgreSQL : {e}"
    
    inserted = 0
    skipped = 0
    errors = 0
    synced_ids = []
    
    for _, row in df_non_sync.iterrows():
        try:
            with engine.connect() as conn:
                result = conn.execute(
                    text("SELECT COUNT(*) FROM tourisme WHERE annee = :annee AND departement = :departement"),
                    {"annee": row['annee'], "departement": row['departement']}
                )
                exists = result.scalar()
            
            if exists == 0:
                with engine.connect() as conn:
                    conn.execute(
                        text("""
                            INSERT INTO tourisme (
                                annee, departement,
                                hotel_receptifs, hotel_chambres, hotel_lits,
                                auberge_receptifs, auberge_chambres, auberge_lits,
                                campement_touristique_receptifs, campement_touristique_chambres, campement_touristique_lits,
                                campement_chasse_receptifs, campement_chasse_chambres, campement_chasse_lits,
                                relais_receptifs, relais_chambres, relais_lits,
                                gite_receptifs, gite_chambres, gite_lits,
                                lodge_receptifs, lodge_chambres, lodge_lits,
                                centre_accueil_receptifs, centre_accueil_chambres, centre_accueil_lits,
                                france, autres_pays_europeens, usa, autres_pays_americains, senegal, autres_pays_africains, asie, oceanie,
                                hotel_nuitees, hotel_taux_occupation,
                                auberge_nuitees, auberge_taux_occupation,
                                campement_touristique_nuitees, campement_touristique_taux_occupation,
                                campement_chasse_nuitees, campement_chasse_taux_occupation,
                                relais_nuitees, relais_taux_occupation,
                                gite_nuitees, gite_taux_occupation,
                                lodge_nuitees, lodge_taux_occupation,
                                centre_accueil_nuitees, centre_accueil_taux_occupation
                            ) VALUES (
                                :annee, :departement,
                                :hotel_receptifs, :hotel_chambres, :hotel_lits,
                                :auberge_receptifs, :auberge_chambres, :auberge_lits,
                                :campement_touristique_receptifs, :campement_touristique_chambres, :campement_touristique_lits,
                                :campement_chasse_receptifs, :campement_chasse_chambres, :campement_chasse_lits,
                                :relais_receptifs, :relais_chambres, :relais_lits,
                                :gite_receptifs, :gite_chambres, :gite_lits,
                                :lodge_receptifs, :lodge_chambres, :lodge_lits,
                                :centre_accueil_receptifs, :centre_accueil_chambres, :centre_accueil_lits,
                                :france, :autres_pays_europeens, :usa, :autres_pays_americains, :senegal, :autres_pays_africains, :asie, :oceanie,
                                :hotel_nuitees, :hotel_taux_occupation,
                                :auberge_nuitees, :auberge_taux_occupation,
                                :campement_touristique_nuitees, :campement_touristique_taux_occupation,
                                :campement_chasse_nuitees, :campement_chasse_taux_occupation,
                                :relais_nuitees, :relais_taux_occupation,
                                :gite_nuitees, :gite_taux_occupation,
                                :lodge_nuitees, :lodge_taux_occupation,
                                :centre_accueil_nuitees, :centre_accueil_taux_occupation
                            )
                        """),
                        {
                            "annee": row['annee'], "departement": row['departement'],
                            "hotel_receptifs": row['hotel_receptifs'], "hotel_chambres": row['hotel_chambres'], "hotel_lits": row['hotel_lits'],
                            "auberge_receptifs": row['auberge_receptifs'], "auberge_chambres": row['auberge_chambres'], "auberge_lits": row['auberge_lits'],
                            "campement_touristique_receptifs": row['campement_touristique_receptifs'], "campement_touristique_chambres": row['campement_touristique_chambres'], "campement_touristique_lits": row['campement_touristique_lits'],
                            "campement_chasse_receptifs": row['campement_chasse_receptifs'], "campement_chasse_chambres": row['campement_chasse_chambres'], "campement_chasse_lits": row['campement_chasse_lits'],
                            "relais_receptifs": row['relais_receptifs'], "relais_chambres": row['relais_chambres'], "relais_lits": row['relais_lits'],
                            "gite_receptifs": row['gite_receptifs'], "gite_chambres": row['gite_chambres'], "gite_lits": row['gite_lits'],
                            "lodge_receptifs": row['lodge_receptifs'], "lodge_chambres": row['lodge_chambres'], "lodge_lits": row['lodge_lits'],
                            "centre_accueil_receptifs": row['centre_accueil_receptifs'], "centre_accueil_chambres": row['centre_accueil_chambres'], "centre_accueil_lits": row['centre_accueil_lits'],
                            "france": row['france'], "autres_pays_europeens": row['autres_pays_europeens'], "usa": row['usa'],
                            "autres_pays_americains": row['autres_pays_americains'], "senegal": row['senegal'],
                            "autres_pays_africains": row['autres_pays_africains'], "asie": row['asie'], "oceanie": row['oceanie'],
                            "hotel_nuitees": row['hotel_nuitees'], "hotel_taux_occupation": row['hotel_taux_occupation'],
                            "auberge_nuitees": row['auberge_nuitees'], "auberge_taux_occupation": row['auberge_taux_occupation'],
                            "campement_touristique_nuitees": row['campement_touristique_nuitees'], "campement_touristique_taux_occupation": row['campement_touristique_taux_occupation'],
                            "campement_chasse_nuitees": row['campement_chasse_nuitees'], "campement_chasse_taux_occupation": row['campement_chasse_taux_occupation'],
                            "relais_nuitees": row['relais_nuitees'], "relais_taux_occupation": row['relais_taux_occupation'],
                            "gite_nuitees": row['gite_nuitees'], "gite_taux_occupation": row['gite_taux_occupation'],
                            "lodge_nuitees": row['lodge_nuitees'], "lodge_taux_occupation": row['lodge_taux_occupation'],
                            "centre_accueil_nuitees": row['centre_accueil_nuitees'], "centre_accueil_taux_occupation": row['centre_accueil_taux_occupation']
                        }
                    )
                    conn.commit()
                inserted += 1
                synced_ids.append(row['id'])
            else:
                skipped += 1
                synced_ids.append(row['id'])
        except Exception as e:
            errors += 1
    
    if synced_ids:
        mark_tourisme_synchronized(synced_ids)
    
    return inserted, skipped, errors, None

# -------------------------------
# LISTES
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
    "Travail", "Artisanat"
]

# -------------------------------
# FONCTIONS D'ANALYSE
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
# SESSION STATE
# -------------------------------
if 'confirm_delete_ninea' not in st.session_state:
    st.session_state.confirm_delete_ninea = False
if 'confirm_delete_travail' not in st.session_state:
    st.session_state.confirm_delete_travail = False
if 'confirm_delete_artisanat' not in st.session_state:
    st.session_state.confirm_delete_artisanat = False
if 'confirm_delete_tourisme' not in st.session_state:
    st.session_state.confirm_delete_tourisme = False
if 'secteur_courant' not in st.session_state:
    st.session_state.secteur_courant = "NINEA (Entreprises)"
if 'annee_courante' not in st.session_state:
    st.session_state.annee_courante = "Tous"
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'edit_id' not in st.session_state:
    st.session_state.edit_id = None
if 'edit_secteur' not in st.session_state:
    st.session_state.edit_secteur = None

init_postgres_travail_table()
init_postgres_artisanat_table()
init_postgres_tourisme_table()

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

df_ninea = get_all_ninea_data()

# ===============================
# PAGE ACCUEIL
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
        ("🌤️", "Météo"), ("🏗️", "BTP/Construction"), ("📊", "NINEA (ENTREPRISES)"),
        ("👷", "Travail"), ("🎨", "Artisanat")
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
        df = get_all_travail_data()
        if df.empty:
            st.info(f"Aucune donnée pour le secteur **{secteur}**.")
        else:
            st.metric(f"Nombre d'enregistrements - {secteur}", len(df))
            st.dataframe(df.drop(columns=['synchro'], errors='ignore'), use_container_width=True)
    elif secteur == "Artisanat":
        df = get_all_artisanat_data()
        if df.empty:
            st.info(f"Aucune donnée pour le secteur **{secteur}**.")
        else:
            st.metric(f"Nombre d'enregistrements - {secteur}", len(df))
            st.dataframe(df.drop(columns=['synchro'], errors='ignore'), use_container_width=True)
    elif secteur == "Tourisme":
        df = get_all_tourisme_data()
        if df.empty:
            st.info(f"Aucune donnée pour le secteur **{secteur}**.")
        else:
            st.metric(f"Nombre d'enregistrements - {secteur}", len(df))
            df_afficher = df.drop(columns=['synchro'], errors='ignore')
            st.dataframe(df_afficher, use_container_width=True)
    else:
        df = get_ninea_by_secteur(secteur)
        if df.empty:
            st.info(f"Aucune donnée pour le secteur **{secteur}**.")
        else:
            st.metric(f"Nombre d'enregistrements - {secteur}", len(df))
            df_afficher = df.drop(columns=['secteur', 'synchro'], errors='ignore')
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
        if annee == "Tous":
            df = get_all_travail_data()
        else:
            conn = sqlite3.connect(DB_TRAVAIL_PATH)
            df = pd.read_sql_query("SELECT * FROM collecte_travail WHERE annee = ? ORDER BY id DESC", conn, params=(annee,))
            conn.close()
    elif st.session_state.secteur_courant == "Artisanat":
        if annee == "Tous":
            df = get_all_artisanat_data()
        else:
            conn = sqlite3.connect(DB_ARTISANAT_PATH)
            df = pd.read_sql_query("SELECT * FROM collecte_artisanat WHERE annee = ? ORDER BY id DESC", conn, params=(annee,))
            conn.close()
    elif st.session_state.secteur_courant == "Tourisme":
        if annee == "Tous":
            df = get_all_tourisme_data()
        else:
            conn = sqlite3.connect(DB_TOURISME_PATH)
            df = pd.read_sql_query("SELECT * FROM collecte_tourisme WHERE annee = ? ORDER BY id DESC", conn, params=(annee,))
            conn.close()
    else:
        df = get_ninea_by_secteur(st.session_state.secteur_courant)
        if annee != "Tous":
            df = df[df['date_depot'].str[:4] == str(annee)]
    
    if df.empty:
        st.info(f"Aucune donnée pour cette combinaison.")
    else:
        st.metric(f"Nombre d'enregistrements", len(df))
        df_afficher = df.drop(columns=['synchro'], errors='ignore')
        st.dataframe(df_afficher, use_container_width=True)

# ===============================
# PAGE VISUALISATION (avec affichage des vrais nombres)
# ===============================
elif page == "📈 Visualisation":
    show_main_title()
    st.title("📈 Visualisation et recherche")
    
    secteur = st.session_state.secteur_courant
    annee = st.session_state.annee_courante
    
    # Charger les données selon le secteur
    if secteur == "Travail":
        if annee == "Tous":
            df = get_all_travail_data()
        else:
            conn = sqlite3.connect(DB_TRAVAIL_PATH)
            df = pd.read_sql_query("SELECT * FROM collecte_travail WHERE annee = ? ORDER BY id DESC", conn, params=(annee,))
            conn.close()
    elif secteur == "Artisanat":
        if annee == "Tous":
            df = get_all_artisanat_data()
        else:
            conn = sqlite3.connect(DB_ARTISANAT_PATH)
            df = pd.read_sql_query("SELECT * FROM collecte_artisanat WHERE annee = ? ORDER BY id DESC", conn, params=(annee,))
            conn.close()
    elif secteur == "Tourisme":
        if annee == "Tous":
            df = get_all_tourisme_data()
        else:
            conn = sqlite3.connect(DB_TOURISME_PATH)
            df = pd.read_sql_query("SELECT * FROM collecte_tourisme WHERE annee = ? ORDER BY id DESC", conn, params=(annee,))
            conn.close()
    else:
        df = get_ninea_by_secteur(secteur)
        if annee != "Tous":
            df = df[df['date_depot'].str[:4] == str(annee)]
    
    if df.empty:
        st.warning(f"Aucune donnée pour le secteur **{secteur}** et l'année **{annee}**.")
    else:
        # MÊME LISTE COMPLÈTE POUR TOUS LES SECTEURS
        display_type = st.selectbox(
            "Choisissez le type d'affichage",
            ["Recherche", "Colonne bande", "Colonne empilée", "Bar", "Bar empilé", "Ligne", "Secteur (camembert)", 
             "Radar", "Zone", "Zone empilée", "Tarte", "Jaguar", "Année après année (ligne)", 
             "Année après année (colonne)", "Valeur unique", "Dispersion", "Carte"]
        )
        
        if display_type == "Recherche":
            st.subheader("Recherche textuelle")
            colonnes_recherche = [col for col in df.columns if col not in ['id', 'synchro']]
            colonne_choisie = st.selectbox("Colonne à filtrer", colonnes_recherche)
            texte_recherche = st.text_input("Texte à rechercher (contient)", "")
            if texte_recherche:
                df_filtre = df[df[colonne_choisie].astype(str).str.contains(texte_recherche, case=False, na=False)]
            else:
                df_filtre = df
            st.dataframe(df_filtre, use_container_width=True)
            st.caption(f"{len(df_filtre)} ligne(s) trouvée(s)")
        
        elif display_type == "Carte":
            st.subheader("🗺️ Carte géographique")
            
            if secteur == "NINEA (Entreprises)":
                if 'departement' in df.columns:
                    carte_data = df.groupby('departement').size().reset_index(name='Nombre')
                    fig = px.bar(carte_data, x='departement', y='Nombre', title="Répartition par département", color='departement')
                    fig.update_layout(yaxis_tickformat=',.0f')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    coords = {'Fatick': (14.2, -16.2), 'Foundiougne': (14.1, -16.5), 'Gossas': (14.5, -16.1)}
                    map_df = df.groupby('departement').size().reset_index(name='Nombre')
                    map_df['lat'] = map_df['departement'].map(lambda x: coords.get(x, (14.2, -16.2))[0])
                    map_df['lon'] = map_df['departement'].map(lambda x: coords.get(x, (14.2, -16.2))[1])
                    fig_map = px.scatter_geo(map_df, lat='lat', lon='lon', size='Nombre', text='departement',
                                             projection='natural earth', title="Carte des départements")
                    st.plotly_chart(fig_map, use_container_width=True)
                else:
                    st.info("Colonne 'departement' non disponible.")
            
            elif secteur == "Artisanat":
                if 'departement' in df.columns:
                    total_par_dep = df.groupby('departement')[['prod_ei', 'prod_gie', 'service_ei', 'service_gie', 'art_ei', 'art_gie']].sum().reset_index()
                    st.dataframe(total_par_dep, use_container_width=True)
                    
                    fig = px.bar(total_par_dep, x='departement', y='prod_ei', title="Entreprises individuelles (Production) par département", color='departement')
                    fig.update_layout(yaxis_tickformat=',.0f')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Colonne 'departement' non disponible.")
            
            elif secteur == "Travail":
                if 'departement' in df.columns:
                    total_par_dep = df.groupby('departement')[['etablissements_ouverts', 'etablissements_fermes', 'emplois_generes', 'emplois_perdus']].sum().reset_index()
                    st.dataframe(total_par_dep, use_container_width=True)
                    
                    fig = px.bar(total_par_dep, x='departement', y='etablissements_ouverts', title="Établissements ouverts par département", color='departement')
                    fig.update_layout(yaxis_tickformat=',.0f')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Colonne 'departement' non disponible.")
            
            elif secteur == "Tourisme":
                if 'departement' in df.columns:
                    total_par_dep = df.groupby('departement')[['hotel_receptifs', 'hotel_chambres', 'hotel_lits', 
                                                                'auberge_receptifs', 'auberge_chambres', 'auberge_lits',
                                                                'campement_touristique_receptifs', 'campement_touristique_chambres', 'campement_touristique_lits']].sum().reset_index()
                    st.dataframe(total_par_dep, use_container_width=True)
                    
                    fig = px.bar(total_par_dep, x='departement', y='hotel_lits', title="Nombre de lits (Hôtels) par département", color='departement')
                    fig.update_layout(yaxis_tickformat=',.0f')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Colonne 'departement' non disponible.")
        
        elif display_type == "Tableau croisé":
            if secteur == "Travail":
                numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
                if 'id' in numeric_cols:
                    numeric_cols.remove('id')
                if 'synchro' in numeric_cols:
                    numeric_cols.remove('synchro')
                if numeric_cols:
                    selected_metric = st.selectbox("Choisir l'indicateur", numeric_cols)
                    pivot = df.pivot_table(index='departement', columns='annee', values=selected_metric, aggfunc='sum', fill_value=0)
                    st.dataframe(pivot, use_container_width=True)
                else:
                    st.info("Aucune colonne numérique disponible pour le tableau croisé.")
            else:
                st.info("Tableau croisé disponible uniquement pour le secteur Travail.")
        
        elif display_type == "Valeur unique":
            total = len(df)
            st.metric("Valeur unique", total, delta=None)
        
        else:
            # Déterminer les colonnes disponibles selon le secteur
            if secteur == "Artisanat":
                colonnes_cat = ['departement', 'annee']
                x_axis = st.selectbox("Axe X (catégorie)", colonnes_cat)
                
                if display_type in ["Colonne bande", "Colonne empilée", "Bar", "Bar empilé", "Ligne", "Zone", "Zone empilée", "Jaguar", "Dispersion"]:
                    numeric_cols = ['prod_ei', 'prod_gie', 'service_ei', 'service_gie', 'art_ei', 'art_gie']
                    y_axis = st.selectbox("Axe Y (valeur numérique)", numeric_cols)
                    df_group = df.groupby(x_axis)[y_axis].sum().reset_index()
                    y_value = y_axis
                else:
                    df_group = df.groupby(x_axis).size().reset_index(name='Nombre')
                    y_value = 'Nombre'
            
            elif secteur == "Travail":
                colonnes_cat = ['departement', 'annee']
                x_axis = st.selectbox("Axe X (catégorie)", colonnes_cat)
                
                if display_type in ["Colonne bande", "Colonne empilée", "Bar", "Bar empilé", "Ligne", "Zone", "Zone empilée", "Jaguar", "Dispersion"]:
                    numeric_cols = [col for col in df.columns if col not in ['id', 'synchro', 'departement', 'annee']]
                    y_axis = st.selectbox("Axe Y (valeur numérique)", numeric_cols)
                    df_group = df.groupby(x_axis)[y_axis].sum().reset_index()
                    y_value = y_axis
                else:
                    df_group = df.groupby(x_axis).size().reset_index(name='Nombre')
                    y_value = 'Nombre'
            
            elif secteur == "Tourisme":
                colonnes_cat = ['departement', 'annee']
                x_axis = st.selectbox("Axe X (catégorie)", colonnes_cat)
                
                numeric_cols = ['hotel_receptifs', 'hotel_chambres', 'hotel_lits', 
                                'auberge_receptifs', 'auberge_chambres', 'auberge_lits',
                                'campement_touristique_receptifs', 'campement_touristique_chambres', 'campement_touristique_lits',
                                'campement_chasse_receptifs', 'campement_chasse_chambres', 'campement_chasse_lits',
                                'relais_receptifs', 'relais_chambres', 'relais_lits',
                                'gite_receptifs', 'gite_chambres', 'gite_lits',
                                'lodge_receptifs', 'lodge_chambres', 'lodge_lits',
                                'centre_accueil_receptifs', 'centre_accueil_chambres', 'centre_accueil_lits',
                                'france', 'autres_pays_europeens', 'usa', 'autres_pays_americains', 
                                'senegal', 'autres_pays_africains', 'asie', 'oceanie',
                                'hotel_nuitees', 'auberge_nuitees', 'campement_touristique_nuitees',
                                'campement_chasse_nuitees', 'relais_nuitees', 'gite_nuitees', 
                                'lodge_nuitees', 'centre_accueil_nuitees']
                
                if display_type in ["Colonne bande", "Colonne empilée", "Bar", "Bar empilé", "Ligne", "Zone", "Zone empilée", "Jaguar", "Dispersion"]:
                    y_axis = st.selectbox("Axe Y (valeur numérique)", numeric_cols)
                    df_group = df.groupby(x_axis)[y_axis].sum().reset_index()
                    y_value = y_axis
                else:
                    df_group = df.groupby(x_axis).size().reset_index(name='Nombre')
                    y_value = 'Nombre'
            
            else:  # NINEA
                colonnes_cat = ['commune', 'departement', 'sexe', 'regime', 'forme_juridique', 'activite_principale']
                if 'date_depot' in df.columns:
                    df['mois'] = pd.to_datetime(df['date_depot'], errors='coerce').dt.month
                    colonnes_cat.append('mois')
                x_axis = st.selectbox("Axe X (catégorie)", colonnes_cat)
                df_group = df.groupby(x_axis).size().reset_index(name='Nombre')
                y_value = 'Nombre'
            
            type_affichage = display_type.replace(" bande", "")
            
            try:
                # ========== ANNÉE APRÈS ANNÉE (LIGNE) - CORRECTION SPÉCIFIQUE ==========
                if type_affichage == "Année après année (ligne)":
                    # Vérifier si une colonne année existe
                    if 'annee' in df.columns:
                        # Créer un groupement par année et par catégorie (x_axis)
                        # Pour Artisanat et Travail, on utilise x_axis comme catégorie
                        if secteur == "Artisanat":
                            # Pour Artisanat, on regroupe par année et par département ou autre catégorie
                            if x_axis in df.columns:
                                annee_group = df.groupby(['annee', x_axis])[y_value if y_value != 'Nombre' else 'prod_ei'].sum().reset_index()
                                fig = px.line(annee_group, x='annee', y=y_value if y_value != 'Nombre' else 'prod_ei', 
                                              color=x_axis, markers=True, title=f"Année après année - {x_axis}")
                            else:
                                annee_group = df.groupby('annee')[y_value if y_value != 'Nombre' else 'prod_ei'].sum().reset_index()
                                fig = px.line(annee_group, x='annee', y=y_value if y_value != 'Nombre' else 'prod_ei', 
                                              markers=True, title="Année après année (total)")
                        elif secteur == "Travail":
                            if x_axis in df.columns and x_axis != 'annee':
                                annee_group = df.groupby(['annee', x_axis])[y_axis].sum().reset_index()
                                fig = px.line(annee_group, x='annee', y=y_axis, color=x_axis, markers=True, 
                                              title=f"Année après année - {x_axis}")
                            else:
                                annee_group = df.groupby('annee')[y_axis].sum().reset_index()
                                fig = px.line(annee_group, x='annee', y=y_axis, markers=True, title="Année après année (total)")
                        elif secteur == "Tourisme":
                            if x_axis in df.columns and x_axis != 'annee':
                                annee_group = df.groupby(['annee', x_axis])[y_axis].sum().reset_index()
                                fig = px.line(annee_group, x='annee', y=y_axis, color=x_axis, markers=True, 
                                              title=f"Année après année - {x_axis}")
                            else:
                                annee_group = df.groupby('annee')[y_axis].sum().reset_index()
                                fig = px.line(annee_group, x='annee', y=y_axis, markers=True, title="Année après année (total)")
                        else:  # NINEA
                            # Pour NINEA, on extrait l'année de date_depot
                            if 'date_depot' in df.columns:
                                df['annee'] = pd.to_datetime(df['date_depot'], errors='coerce').dt.year
                                if x_axis != 'annee' and x_axis in df.columns:
                                    annee_group = df.groupby(['annee', x_axis]).size().reset_index(name='Nombre')
                                    fig = px.line(annee_group, x='annee', y='Nombre', color=x_axis, markers=True, 
                                                  title=f"Année après année - {x_axis}")
                                else:
                                    annee_group = df.groupby('annee').size().reset_index(name='Nombre')
                                    fig = px.line(annee_group, x='annee', y='Nombre', markers=True, title="Année après année (total)")
                            else:
                                fig = px.line(df_group, x=x_axis, y=y_value, markers=True, title=f"Année après année - {x_axis}")
                        fig.update_layout(yaxis_tickformat=',.0f')
                    else:
                        st.info("Aucune colonne 'annee' trouvée. Ce graphique nécessite des données avec années.")
                        fig = None
                
                # ========== ANNÉE APRÈS ANNÉE (COLONNE) - CORRECTION SPÉCIFIQUE ==========
                elif type_affichage == "Année après année (colonne)":
                    if 'annee' in df.columns:
                        if secteur == "Artisanat":
                            if x_axis in df.columns and x_axis != 'annee':
                                annee_group = df.groupby(['annee', x_axis])[y_value if y_value != 'Nombre' else 'prod_ei'].sum().reset_index()
                                fig = px.bar(annee_group, x='annee', y=y_value if y_value != 'Nombre' else 'prod_ei', 
                                             color=x_axis, title=f"Année après année - {x_axis}", text=y_value if y_value != 'Nombre' else 'prod_ei')
                            else:
                                annee_group = df.groupby('annee')[y_value if y_value != 'Nombre' else 'prod_ei'].sum().reset_index()
                                fig = px.bar(annee_group, x='annee', y=y_value if y_value != 'Nombre' else 'prod_ei', 
                                             title="Année après année (total)")
                        elif secteur == "Travail":
                            if x_axis in df.columns and x_axis != 'annee':
                                annee_group = df.groupby(['annee', x_axis])[y_axis].sum().reset_index()
                                fig = px.bar(annee_group, x='annee', y=y_axis, color=x_axis, title=f"Année après année - {x_axis}")
                            else:
                                annee_group = df.groupby('annee')[y_axis].sum().reset_index()
                                fig = px.bar(annee_group, x='annee', y=y_axis, title="Année après année (total)")
                        elif secteur == "Tourisme":
                            if x_axis in df.columns and x_axis != 'annee':
                                annee_group = df.groupby(['annee', x_axis])[y_axis].sum().reset_index()
                                fig = px.bar(annee_group, x='annee', y=y_axis, color=x_axis, title=f"Année après année - {x_axis}")
                            else:
                                annee_group = df.groupby('annee')[y_axis].sum().reset_index()
                                fig = px.bar(annee_group, x='annee', y=y_axis, title="Année après année (total)")
                        else:
                            if 'date_depot' in df.columns:
                                df['annee'] = pd.to_datetime(df['date_depot'], errors='coerce').dt.year
                                if x_axis != 'annee' and x_axis in df.columns:
                                    annee_group = df.groupby(['annee', x_axis]).size().reset_index(name='Nombre')
                                    fig = px.bar(annee_group, x='annee', y='Nombre', color=x_axis, title=f"Année après année - {x_axis}")
                                else:
                                    annee_group = df.groupby('annee').size().reset_index(name='Nombre')
                                    fig = px.bar(annee_group, x='annee', y='Nombre', title="Année après année (total)")
                            else:
                                fig = px.bar(df_group, x=x_axis, y=y_value, title=f"Année après année - {x_axis}")
                        fig.update_layout(yaxis_tickformat=',.0f')
                    else:
                        st.info("Aucune colonne 'annee' trouvée. Ce graphique nécessite des données avec années.")
                        fig = None
                
                # ========== AUTRES GRAPHIQUES ==========
                elif type_affichage == "Colonne":
                    fig = px.bar(df_group, x=x_axis, y=y_value, title=f"Répartition par {x_axis}", text=y_value if y_value != 'Nombre' else None)
                    if y_value != 'Nombre':
                        fig.update_traces(textposition='outside')
                    fig.update_layout(yaxis_tickformat=',.0f')
                elif type_affichage == "Colonne empilée":
                    if secteur == "NINEA (Entreprises)" and 'sexe' in df.columns:
                        df_group2 = df.groupby([x_axis, 'sexe']).size().reset_index(name='Nombre')
                        fig = px.bar(df_group2, x=x_axis, y='Nombre', color='sexe', title=f"Répartition par {x_axis} et sexe", text='Nombre')
                        fig.update_traces(textposition='outside')
                        fig.update_layout(yaxis_tickformat=',.0f')
                    elif secteur != "NINEA (Entreprises)" and 'departement' in df.columns and x_axis != 'departement':
                        df_group2 = df.groupby([x_axis, 'departement'])[y_value].sum().reset_index()
                        fig = px.bar(df_group2, x=x_axis, y=y_value, color='departement', title=f"Répartition par {x_axis} et département", text=y_value)
                        fig.update_traces(textposition='outside')
                        fig.update_layout(yaxis_tickformat=',.0f')
                    else:
                        fig = px.bar(df_group, x=x_axis, y=y_value, text=y_value if y_value != 'Nombre' else None)
                        if y_value != 'Nombre':
                            fig.update_traces(textposition='outside')
                        fig.update_layout(yaxis_tickformat=',.0f')
                elif type_affichage == "Bar":
                    fig = px.bar(df_group, y=x_axis, x=y_value, orientation='h', title=f"Répartition par {x_axis}", text=y_value if y_value != 'Nombre' else None)
                    if y_value != 'Nombre':
                        fig.update_traces(textposition='outside')
                    fig.update_layout(xaxis_tickformat=',.0f')
                elif type_affichage == "Bar empilé":
                    if secteur == "NINEA (Entreprises)" and 'sexe' in df.columns:
                        df_group2 = df.groupby([x_axis, 'sexe']).size().reset_index(name='Nombre')
                        fig = px.bar(df_group2, y=x_axis, x='Nombre', color='sexe', orientation='h', title=f"Répartition par {x_axis} et sexe", text='Nombre')
                        fig.update_traces(textposition='outside')
                        fig.update_layout(xaxis_tickformat=',.0f')
                    elif secteur != "NINEA (Entreprises)" and 'departement' in df.columns and x_axis != 'departement':
                        df_group2 = df.groupby([x_axis, 'departement'])[y_value].sum().reset_index()
                        fig = px.bar(df_group2, y=x_axis, x=y_value, color='departement', orientation='h', title=f"Répartition par {x_axis} et département", text=y_value)
                        fig.update_traces(textposition='outside')
                        fig.update_layout(xaxis_tickformat=',.0f')
                    else:
                        fig = px.bar(df_group, y=x_axis, x=y_value, orientation='h', text=y_value if y_value != 'Nombre' else None)
                        if y_value != 'Nombre':
                            fig.update_traces(textposition='outside')
                        fig.update_layout(xaxis_tickformat=',.0f')
                elif type_affichage == "Ligne":
                    fig = px.line(df_group, x=x_axis, y=y_value, markers=True, title=f"Évolution de {x_axis}", text=y_value if y_value != 'Nombre' else None)
                    fig.update_layout(yaxis_tickformat=',.0f')
                elif type_affichage == "Secteur (camembert)":
                    fig = px.pie(df_group, names=x_axis, values=y_value, title=f"Part de {x_axis}")
                elif type_affichage == "Radar":
                    df_radar = df_group.head(10)
                    fig = px.line_polar(df_radar, r=y_value, theta=x_axis, line_close=True, title=f"Radar - {x_axis}")
                elif type_affichage == "Zone":
                    fig = px.area(df_group, x=x_axis, y=y_value, title=f"Zone - {x_axis}")
                    fig.update_layout(yaxis_tickformat=',.0f')
                elif type_affichage == "Zone empilée":
                    if secteur == "NINEA (Entreprises)" and 'sexe' in df.columns:
                        df_group2 = df.groupby([x_axis, 'sexe']).size().reset_index(name='Nombre')
                        fig = px.area(df_group2, x=x_axis, y='Nombre', color='sexe', title=f"Zone empilée par {x_axis} et sexe")
                        fig.update_layout(yaxis_tickformat=',.0f')
                    elif secteur != "NINEA (Entreprises)" and 'departement' in df.columns and x_axis != 'departement':
                        df_group2 = df.groupby([x_axis, 'departement'])[y_value].sum().reset_index()
                        fig = px.area(df_group2, x=x_axis, y=y_value, color='departement', title=f"Zone empilée par {x_axis} et département")
                        fig.update_layout(yaxis_tickformat=',.0f')
                    else:
                        fig = px.area(df_group, x=x_axis, y=y_value, title=f"Zone empilée - {x_axis}")
                        fig.update_layout(yaxis_tickformat=',.0f')
                elif type_affichage == "Tarte":
                    fig = px.pie(df_group, names=x_axis, values=y_value, title=f"Tarte - {x_axis}")
                elif type_affichage == "Jaguar":
                    total = df_group[y_value].sum() if y_value != 'Nombre' else len(df)
                    fig = px.bar(df_group, x=x_axis, y=y_value, title=f"Jaguar - {x_axis} (Total: {total})", text=y_value if y_value != 'Nombre' else None)
                    if y_value != 'Nombre':
                        fig.update_traces(textposition='outside')
                    fig.update_layout(yaxis_tickformat=',.0f')
                elif type_affichage == "Dispersion":
                    if len(df_group) > 1:
                        fig = px.scatter(df_group, x=x_axis, y=y_value, size=y_value, title=f"Dispersion de {x_axis}")
                        fig.update_layout(yaxis_tickformat=',.0f')
                    else:
                        fig = None
                else:
                    fig = None
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True, key=f"viz_{display_type}_{x_axis}")
                elif display_type not in ["Valeur unique", "Tableau croisé"]:
                    st.info("Type de graphique non disponible avec ces données.")
            
            except Exception as e:
                st.info(f"Graphique non disponible pour cette sélection. Essayez un autre axe X.")

# ===============================
# PAGE BASE D'EXPLORATION (avec édition/suppression)
# ===============================
elif page == "🗄️ Base d'exploration":
    show_main_title()
    
    secteur_choisi = st.selectbox("📌 Choisir le secteur de collecte", secteurs_liste)
    
    # ==========================================
    # FORMULAIRE POUR SECTEUR TRAVAIL
    # ==========================================
    if secteur_choisi == "Travail":
        st.markdown("### 📝 Formulaire de collecte - Secteur Travail")
        
        with st.form(key="formulaire_travail", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                annee = st.selectbox("Année *", [2023, 2024, 2025, 2026])
            with col2:
                departement = st.selectbox("Département / Région *", ["Fatick", "Foundiougne", "Gossas", "Région"])
            
            st.markdown("#### Demandeurs d'emploi")
            col_a1, col_a2 = st.columns(2)
            with col_a1:
                manoeuvres_h = st.number_input("Manœuvres - Hommes", min_value=0, step=1, key="manoeuvres_h", value=0)
                employes_h = st.number_input("Employés - Hommes", min_value=0, step=1, key="employes_h", value=0)
            with col_a2:
                manoeuvres_f = st.number_input("Manœuvres - Femmes", min_value=0, step=1, key="manoeuvres_f", value=0)
                employes_f = st.number_input("Employés - Femmes", min_value=0, step=1, key="employes_f", value=0)
            
            st.markdown("#### Établissements")
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                etab_ouverts = st.number_input("Établissements ouverts", min_value=0, step=1, key="etab_ouverts", value=0)
            with col_b2:
                etab_fermes = st.number_input("Établissements fermés", min_value=0, step=1, key="etab_fermes", value=0)
            
            st.markdown("#### Statut juridique (établissements ouverts)")
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                ei = st.number_input("EI", min_value=0, step=1, key="ei", value=0)
                sarl = st.number_input("SARL", min_value=0, step=1, key="sarl", value=0)
                gie = st.number_input("GIE", min_value=0, step=1, key="gie", value=0)
            with col_c2:
                sa = st.number_input("SA", min_value=0, step=1, key="sa", value=0)
                suarl = st.number_input("SUARL", min_value=0, step=1, key="suarl", value=0)
                ong = st.number_input("ONG", min_value=0, step=1, key="ong", value=0)
            with col_c3:
                autres_statuts = st.number_input("Autres statuts", min_value=0, step=1, key="autres_statuts", value=0)
            
            st.markdown("#### Emplois")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                emplois_gen = st.number_input("Emplois générés", min_value=0, step=1, key="emplois_gen", value=0)
            with col_d2:
                emplois_per = st.number_input("Emplois perdus", min_value=0, step=1, key="emplois_per", value=0)
            
            st.markdown("#### Contrats de travail")
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                st.markdown("**Hommes**")
                cdi_h = st.number_input("CDI - Hommes", min_value=0, step=1, key="cdi_h", value=0)
                cdd_h = st.number_input("CDD - Hommes", min_value=0, step=1, key="cdd_h", value=0)
                saisonnier_h = st.number_input("Saisonnier - Hommes", min_value=0, step=1, key="saisonnier_h", value=0)
                apprentissage_h = st.number_input("Apprentissage - Hommes", min_value=0, step=1, key="apprentissage_h", value=0)
                temporaire_h = st.number_input("Temporaire - Hommes", min_value=0, step=1, key="temp_h", value=0)
                stage_h = st.number_input("Stage - Hommes", min_value=0, step=1, key="stage_h", value=0)
            with col_e2:
                st.markdown("**Femmes**")
                cdi_f = st.number_input("CDI - Femmes", min_value=0, step=1, key="cdi_f", value=0)
                cdd_f = st.number_input("CDD - Femmes", min_value=0, step=1, key="cdd_f", value=0)
                saisonnier_f = st.number_input("Saisonnier - Femmes", min_value=0, step=1, key="saisonnier_f", value=0)
                apprentissage_f = st.number_input("Apprentissage - Femmes", min_value=0, step=1, key="apprentissage_f", value=0)
                temporaire_f = st.number_input("Temporaire - Femmes", min_value=0, step=1, key="temp_f", value=0)
                stage_f = st.number_input("Stage - Femmes", min_value=0, step=1, key="stage_f", value=0)
            
            st.markdown("#### Conflits de travail")
            st.markdown("**Conflits individuels**")
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1:
                indiv_conciliation = st.number_input("Conciliation", min_value=0, step=1, key="indiv_conciliation", value=0)
            with col_f2:
                indiv_partielle = st.number_input("Conciliation partielle", min_value=0, step=1, key="indiv_partielle", value=0)
            with col_f3:
                indiv_non = st.number_input("Non conciliation", min_value=0, step=1, key="indiv_non", value=0)
            
            st.markdown("**Conflits collectifs**")
            col_g1, col_g2, col_g3 = st.columns(3)
            with col_g1:
                coll_conciliation = st.number_input("Conciliation", min_value=0, step=1, key="coll_conciliation", value=0)
            with col_g2:
                coll_partielle = st.number_input("Conciliation partielle", min_value=0, step=1, key="coll_partielle", value=0)
            with col_g3:
                coll_non = st.number_input("Non conciliation", min_value=0, step=1, key="coll_non", value=0)
            
            st.markdown("*** champs obligatoires**")
            submitted = st.form_submit_button("✅ Enregistrer la collecte")
            
            if submitted:
                data = (
                    annee, departement,
                    manoeuvres_h, manoeuvres_f,
                    employes_h, employes_f,
                    etab_ouverts, etab_fermes,
                    ei, sa, sarl, suarl,
                    gie, ong, autres_statuts,
                    emplois_gen, emplois_per,
                    cdi_h, cdi_f,
                    cdd_h, cdd_f,
                    saisonnier_h, saisonnier_f,
                    apprentissage_h, apprentissage_f,
                    temporaire_h, temporaire_f,
                    stage_h, stage_f,
                    indiv_conciliation, indiv_partielle, indiv_non,
                    coll_conciliation, coll_partielle, coll_non
                )
                insert_travail(data)
                st.markdown('<div class="success-message">✅ Données enregistrées avec succès dans le secteur Travail</div>', unsafe_allow_html=True)
                st.balloons()
                st.rerun()
    
    # ==========================================
    # FORMULAIRE POUR SECTEUR ARTISANAT
    # ==========================================
    elif secteur_choisi == "Artisanat":
        st.markdown("### 📝 Formulaire de collecte - Secteur Artisanat")
        
        with st.form(key="formulaire_artisanat", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                annee = st.selectbox("Année *", [2023, 2024, 2025, 2026])
            with col2:
                departement = st.selectbox("Département *", ["Fatick", "Foundiougne", "Gossas", "Région"])
            
            st.markdown("#### Effectifs par section")
            
            col_prod1, col_prod2 = st.columns(2)
            with col_prod1:
                st.markdown("**Production**")
                prod_ei = st.number_input("Entreprises individuelles", min_value=0, step=1, key="prod_ei", value=0)
            with col_prod2:
                st.markdown("**Production**")
                prod_gie = st.number_input("GIE", min_value=0, step=1, key="prod_gie", value=0)
            
            col_serv1, col_serv2 = st.columns(2)
            with col_serv1:
                st.markdown("**Service**")
                service_ei = st.number_input("Entreprises individuelles", min_value=0, step=1, key="service_ei", value=0)
            with col_serv2:
                st.markdown("**Service**")
                service_gie = st.number_input("GIE", min_value=0, step=1, key="service_gie", value=0)
            
            col_art1, col_art2 = st.columns(2)
            with col_art1:
                st.markdown("**Art**")
                art_ei = st.number_input("Entreprises individuelles", min_value=0, step=1, key="art_ei", value=0)
            with col_art2:
                st.markdown("**Art**")
                art_gie = st.number_input("GIE", min_value=0, step=1, key="art_gie", value=0)
            
            st.markdown("*** champs obligatoires**")
            submitted = st.form_submit_button("✅ Enregistrer la collecte")
            
            if submitted:
                data = (
                    annee, departement,
                    prod_ei, prod_gie,
                    service_ei, service_gie,
                    art_ei, art_gie
                )
                insert_artisanat(data)
                st.markdown('<div class="success-message">✅ Données enregistrées avec succès dans le secteur Artisanat</div>', unsafe_allow_html=True)
                st.balloons()
                st.rerun()
    
    # ==========================================
    # FORMULAIRE POUR SECTEUR TOURISME
    # ==========================================
    elif secteur_choisi == "Tourisme":
        st.markdown("### 📝 Formulaire de collecte - Secteur Tourisme")
        
        with st.form(key="formulaire_tourisme", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                annee = st.selectbox("Année *", [2024, 2025, 2026])
            with col2:
                departement = st.selectbox("Département *", ["Fatick", "Foundiougne", "Gossas", "Région"])
            
            st.markdown("#### Bloc A - Infrastructures d'hébergement")
            
            # Hôtel
            st.markdown("**Hôtel**")
            col_h1, col_h2, col_h3 = st.columns(3)
            with col_h1:
                hotel_receptifs = st.number_input("Réceptifs", min_value=0, step=1, key="hotel_receptifs", value=0)
            with col_h2:
                hotel_chambres = st.number_input("Chambres", min_value=0, step=1, key="hotel_chambres", value=0)
            with col_h3:
                hotel_lits = st.number_input("Lits", min_value=0, step=1, key="hotel_lits", value=0)
            
            # Auberge
            st.markdown("**Auberge**")
            col_a1, col_a2, col_a3 = st.columns(3)
            with col_a1:
                auberge_receptifs = st.number_input("Réceptifs", min_value=0, step=1, key="auberge_receptifs", value=0)
            with col_a2:
                auberge_chambres = st.number_input("Chambres", min_value=0, step=1, key="auberge_chambres", value=0)
            with col_a3:
                auberge_lits = st.number_input("Lits", min_value=0, step=1, key="auberge_lits", value=0)
            
            # Campement touristique
            st.markdown("**Campement touristique**")
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                campement_touristique_receptifs = st.number_input("Réceptifs", min_value=0, step=1, key="campement_touristique_receptifs", value=0)
            with col_c2:
                campement_touristique_chambres = st.number_input("Chambres", min_value=0, step=1, key="campement_touristique_chambres", value=0)
            with col_c3:
                campement_touristique_lits = st.number_input("Lits", min_value=0, step=1, key="campement_touristique_lits", value=0)
            
            # Campement de chasse
            st.markdown("**Campement de chasse**")
            col_cc1, col_cc2, col_cc3 = st.columns(3)
            with col_cc1:
                campement_chasse_receptifs = st.number_input("Réceptifs", min_value=0, step=1, key="campement_chasse_receptifs", value=0)
            with col_cc2:
                campement_chasse_chambres = st.number_input("Chambres", min_value=0, step=1, key="campement_chasse_chambres", value=0)
            with col_cc3:
                campement_chasse_lits = st.number_input("Lits", min_value=0, step=1, key="campement_chasse_lits", value=0)
            
            # Relais
            st.markdown("**Relais**")
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                relais_receptifs = st.number_input("Réceptifs", min_value=0, step=1, key="relais_receptifs", value=0)
            with col_r2:
                relais_chambres = st.number_input("Chambres", min_value=0, step=1, key="relais_chambres", value=0)
            with col_r3:
                relais_lits = st.number_input("Lits", min_value=0, step=1, key="relais_lits", value=0)
            
            # Gîte
            st.markdown("**Gîte**")
            col_g1, col_g2, col_g3 = st.columns(3)
            with col_g1:
                gite_receptifs = st.number_input("Réceptifs", min_value=0, step=1, key="gite_receptifs", value=0)
            with col_g2:
                gite_chambres = st.number_input("Chambres", min_value=0, step=1, key="gite_chambres", value=0)
            with col_g3:
                gite_lits = st.number_input("Lits", min_value=0, step=1, key="gite_lits", value=0)
            
            # Lodge
            st.markdown("**Lodge**")
            col_l1, col_l2, col_l3 = st.columns(3)
            with col_l1:
                lodge_receptifs = st.number_input("Réceptifs", min_value=0, step=1, key="lodge_receptifs", value=0)
            with col_l2:
                lodge_chambres = st.number_input("Chambres", min_value=0, step=1, key="lodge_chambres", value=0)
            with col_l3:
                lodge_lits = st.number_input("Lits", min_value=0, step=1, key="lodge_lits", value=0)
            
            # Centre d'accueil
            st.markdown("**Centre d'accueil**")
            col_ca1, col_ca2, col_ca3 = st.columns(3)
            with col_ca1:
                centre_accueil_receptifs = st.number_input("Réceptifs", min_value=0, step=1, key="centre_accueil_receptifs", value=0)
            with col_ca2:
                centre_accueil_chambres = st.number_input("Chambres", min_value=0, step=1, key="centre_accueil_chambres", value=0)
            with col_ca3:
                centre_accueil_lits = st.number_input("Lits", min_value=0, step=1, key="centre_accueil_lits", value=0)
            
            st.markdown("#### Bloc B - Arrivées de touristes par provenance")
            
            col_prov1, col_prov2 = st.columns(2)
            with col_prov1:
                france = st.number_input("France", min_value=0, step=1, key="france", value=0)
                autres_pays_europeens = st.number_input("Autres pays européens", min_value=0, step=1, key="autres_pays_europeens", value=0)
                usa = st.number_input("USA", min_value=0, step=1, key="usa", value=0)
                autres_pays_americains = st.number_input("Autres pays américains", min_value=0, step=1, key="autres_pays_americains", value=0)
            with col_prov2:
                senegal = st.number_input("Sénégal", min_value=0, step=1, key="senegal", value=0)
                autres_pays_africains = st.number_input("Autres pays africains", min_value=0, step=1, key="autres_pays_africains", value=0)
                asie = st.number_input("Asie", min_value=0, step=1, key="asie", value=0)
                oceanie = st.number_input("Océanie", min_value=0, step=1, key="oceanie", value=0)
            
            st.markdown("#### Bloc C - Occupation des réceptifs")
            
            # Hôtel occupation
            st.markdown("**Hôtel**")
            col_ho1, col_ho2, col_ho3 = st.columns(3)
            with col_ho1:
                hotel_nuitees = st.number_input("Nuitées", min_value=0, step=1, key="hotel_nuitees", value=0)
            with col_ho2:
                hotel_taux_occupation = st.number_input("Taux d'occupation (%)", min_value=0.0, step=0.01, format="%.2f", key="hotel_taux_occupation", value=0.0)
            
            # Auberge occupation
            st.markdown("**Auberge**")
            col_ao1, col_ao2 = st.columns(2)
            with col_ao1:
                auberge_nuitees = st.number_input("Nuitées", min_value=0, step=1, key="auberge_nuitees", value=0)
            with col_ao2:
                auberge_taux_occupation = st.number_input("Taux d'occupation (%)", min_value=0.0, step=0.01, format="%.2f", key="auberge_taux_occupation", value=0.0)
            
            # Campement touristique occupation
            st.markdown("**Campement touristique**")
            col_ct1, col_ct2 = st.columns(2)
            with col_ct1:
                campement_touristique_nuitees = st.number_input("Nuitées", min_value=0, step=1, key="campement_touristique_nuitees", value=0)
            with col_ct2:
                campement_touristique_taux_occupation = st.number_input("Taux d'occupation (%)", min_value=0.0, step=0.01, format="%.2f", key="campement_touristique_taux_occupation", value=0.0)
            
            # Campement de chasse occupation
            st.markdown("**Campement de chasse**")
            col_cc1, col_cc2 = st.columns(2)
            with col_cc1:
                campement_chasse_nuitees = st.number_input("Nuitées", min_value=0, step=1, key="campement_chasse_nuitees", value=0)
            with col_cc2:
                campement_chasse_taux_occupation = st.number_input("Taux d'occupation (%)", min_value=0.0, step=0.01, format="%.2f", key="campement_chasse_taux_occupation", value=0.0)
            
            # Relais occupation
            st.markdown("**Relais**")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                relais_nuitees = st.number_input("Nuitées", min_value=0, step=1, key="relais_nuitees", value=0)
            with col_r2:
                relais_taux_occupation = st.number_input("Taux d'occupation (%)", min_value=0.0, step=0.01, format="%.2f", key="relais_taux_occupation", value=0.0)
            
            # Gîte occupation
            st.markdown("**Gîte**")
            col_gi1, col_gi2 = st.columns(2)
            with col_gi1:
                gite_nuitees = st.number_input("Nuitées", min_value=0, step=1, key="gite_nuitees", value=0)
            with col_gi2:
                gite_taux_occupation = st.number_input("Taux d'occupation (%)", min_value=0.0, step=0.01, format="%.2f", key="gite_taux_occupation", value=0.0)
            
            # Lodge occupation
            st.markdown("**Lodge**")
            col_l1, col_l2 = st.columns(2)
            with col_l1:
                lodge_nuitees = st.number_input("Nuitées", min_value=0, step=1, key="lodge_nuitees", value=0)
            with col_l2:
                lodge_taux_occupation = st.number_input("Taux d'occupation (%)", min_value=0.0, step=0.01, format="%.2f", key="lodge_taux_occupation", value=0.0)
            
            # Centre d'accueil occupation
            st.markdown("**Centre d'accueil**")
            col_ca1, col_ca2 = st.columns(2)
            with col_ca1:
                centre_accueil_nuitees = st.number_input("Nuitées", min_value=0, step=1, key="centre_accueil_nuitees", value=0)
            with col_ca2:
                centre_accueil_taux_occupation = st.number_input("Taux d'occupation (%)", min_value=0.0, step=0.01, format="%.2f", key="centre_accueil_taux_occupation", value=0.0)
            
            st.markdown("*** champs obligatoires**")
            submitted = st.form_submit_button("✅ Enregistrer la collecte")
            
            if submitted:
                data = (
                    annee, departement,
                    hotel_receptifs, hotel_chambres, hotel_lits,
                    auberge_receptifs, auberge_chambres, auberge_lits,
                    campement_touristique_receptifs, campement_touristique_chambres, campement_touristique_lits,
                    campement_chasse_receptifs, campement_chasse_chambres, campement_chasse_lits,
                    relais_receptifs, relais_chambres, relais_lits,
                    gite_receptifs, gite_chambres, gite_lits,
                    lodge_receptifs, lodge_chambres, lodge_lits,
                    centre_accueil_receptifs, centre_accueil_chambres, centre_accueil_lits,
                    france, autres_pays_europeens, usa, autres_pays_americains, senegal, autres_pays_africains, asie, oceanie,
                    hotel_nuitees, hotel_taux_occupation,
                    auberge_nuitees, auberge_taux_occupation,
                    campement_touristique_nuitees, campement_touristique_taux_occupation,
                    campement_chasse_nuitees, campement_chasse_taux_occupation,
                    relais_nuitees, relais_taux_occupation,
                    gite_nuitees, gite_taux_occupation,
                    lodge_nuitees, lodge_taux_occupation,
                    centre_accueil_nuitees, centre_accueil_taux_occupation
                )
                insert_tourisme(data)
                st.markdown('<div class="success-message">✅ Données enregistrées avec succès dans le secteur Tourisme</div>', unsafe_allow_html=True)
                st.balloons()
                st.rerun()
    
    # ==========================================
    # FORMULAIRE POUR NINEA
    # ==========================================
    elif secteur_choisi == "NINEA (Entreprises)":
        st.markdown(f"### 📝 Formulaire de collecte - {secteur_choisi}")
        
        with st.form(key="formulaire_ninea", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                nom_complet = st.text_input("Nom complet *", placeholder="Ex: GIE ANDOUN SERVICES")
                cni = st.text_input("Numéro CNI *", placeholder="Ex: 146220010114")
            with col2:
                sexe = st.radio("Sexe *", ["Masculin", "Féminin"], horizontal=True)
                activite_principale = st.text_input("Activité principale *", placeholder="Ex: AGRICULTURE, COMMERCE...")
            
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
            
            departement = st.selectbox("Département *", ["Fatick", "Foundiougne", "Gossas"])
            
            st.markdown("*** champs obligatoires**")
            submitted = st.form_submit_button("✅ Enregistrer la collecte")
            
            if submitted:
                if not nom_complet or not cni or not activite_principale:
                    st.error("❌ Veuillez remplir tous les champs obligatoires")
                else:
                    data = (nom_complet, cni, sexe, activite_principale, regime,
                            forme_juridique, date_depot.strftime("%Y-%m-%d"), commune, departement, secteur_choisi)
                    success = insert_ninea(data)
                    if success:
                        st.markdown(f'<div class="success-message">✅ Données enregistrées dans le secteur **{secteur_choisi}**</div>', unsafe_allow_html=True)
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Ce CNI existe déjà")
    
    # ==========================================
    # AUTRES SECTEURS
    # ==========================================
    elif secteur_choisi not in ["Travail", "Artisanat", "Tourisme", "NINEA (Entreprises)"]:
        st.markdown(f"### 📝 Formulaire de collecte - {secteur_choisi}")
        st.info(f"Formulaire pour le secteur **{secteur_choisi}** en cours de développement.")
    
    # ==========================================
    # AFFICHAGE DES DONNÉES DÉJÀ COLLECTÉES + ÉDITION
    # ==========================================
    st.markdown("---")
    st.markdown("### 📊 Données déjà collectées")
    
    # Chargement des données selon le secteur
    if secteur_choisi == "Travail":
        df_collecte = get_all_travail_data()
    elif secteur_choisi == "Artisanat":
        df_collecte = get_all_artisanat_data()
    elif secteur_choisi == "Tourisme":
        df_collecte = get_all_tourisme_data()
    else:
        df_collecte = get_ninea_by_secteur(secteur_choisi)
        if 'secteur' in df_collecte.columns:
            df_collecte = df_collecte[df_collecte['secteur'] == secteur_choisi]
    
    if df_collecte.empty:
        st.info("Aucune donnée collectée pour ce secteur.")
    else:
        nb_total = len(df_collecte)
        nb_synchro = df_collecte['synchro'].sum() if 'synchro' in df_collecte.columns else 0
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        col_stats1.metric("📋 Total enregistrements", nb_total)
        col_stats2.metric("✅ Synchronisés", nb_synchro)
        col_stats3.metric("⏳ En attente", nb_total - nb_synchro)
        
        df_afficher = df_collecte.drop(columns=['synchro'], errors='ignore')
        st.dataframe(df_afficher, use_container_width=True)
    
    # ==========================================
    # SECTION ÉDITION / SUPPRESSION
    # ==========================================
    st.markdown("---")
    st.markdown("### ✏️ Modifier ou supprimer un enregistrement")
    
    if not df_collecte.empty:
        col_edit1, col_edit2 = st.columns(2)
        
        with col_edit1:
            id_a_modifier = st.number_input("ID de l'enregistrement à modifier", min_value=1, step=1, key="edit_id_input")
            if st.button("🔍 Charger les données", key="load_edit"):
                record = df_collecte[df_collecte['id'] == id_a_modifier]
                if not record.empty:
                    st.session_state.edit_mode = True
                    st.session_state.edit_id = id_a_modifier
                    st.session_state.edit_secteur = secteur_choisi
                    st.rerun()
        
        with col_edit2:
            id_a_supprimer = st.number_input("ID de l'enregistrement à supprimer", min_value=1, step=1, key="delete_id_input")
            if st.button("🗑️ Supprimer cet enregistrement", key="delete_record"):
                if secteur_choisi == "Travail":
                    delete_travail_by_id(id_a_supprimer)
                elif secteur_choisi == "Artisanat":
                    delete_artisanat_by_id(id_a_supprimer)
                elif secteur_choisi == "Tourisme":
                    delete_tourisme_by_id(id_a_supprimer)
                else:
                    delete_ninea_by_id(id_a_supprimer)
                st.success(f"✅ Enregistrement {id_a_supprimer} supprimé avec succès.")
                st.rerun()
        
        # Formulaire d'édition
        if st.session_state.edit_mode and st.session_state.edit_secteur == secteur_choisi:
            st.markdown("#### Modifier l'enregistrement")
            record = df_collecte[df_collecte['id'] == st.session_state.edit_id].iloc[0]
            
            if secteur_choisi == "Artisanat":
                with st.form(key="edit_form_artisanat"):
                    new_annee = st.selectbox("Année", [2023, 2024, 2025, 2026], index=[2023, 2024, 2025, 2026].index(record['annee']) if record['annee'] in [2023, 2024, 2025, 2026] else 0)
                    new_departement = st.selectbox("Département", ["Fatick", "Foundiougne", "Gossas", "Région"], index=["Fatick", "Foundiougne", "Gossas", "Région"].index(record['departement']) if record['departement'] in ["Fatick", "Foundiougne", "Gossas", "Région"] else 0)
                    new_prod_ei = st.number_input("Production - EI", value=record['prod_ei'], step=1)
                    new_prod_gie = st.number_input("Production - GIE", value=record['prod_gie'], step=1)
                    new_service_ei = st.number_input("Service - EI", value=record['service_ei'], step=1)
                    new_service_gie = st.number_input("Service - GIE", value=record['service_gie'], step=1)
                    new_art_ei = st.number_input("Art - EI", value=record['art_ei'], step=1)
                    new_art_gie = st.number_input("Art - GIE", value=record['art_gie'], step=1)
                    
                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        if st.form_submit_button("✅ Enregistrer les modifications"):
                            data = (new_annee, new_departement, new_prod_ei, new_prod_gie,
                                    new_service_ei, new_service_gie, new_art_ei, new_art_gie, st.session_state.edit_id)
                            update_artisanat(data)
                            st.session_state.edit_mode = False
                            st.session_state.edit_id = None
                            st.success("✅ Enregistrement modifié avec succès.")
                            st.rerun()
                    with col_cancel:
                        if st.form_submit_button("❌ Annuler"):
                            st.session_state.edit_mode = False
                            st.session_state.edit_id = None
                            st.rerun()
            
            elif secteur_choisi == "Travail":
                with st.form(key="edit_form_travail"):
                    new_annee = st.selectbox("Année", [2023, 2024, 2025, 2026], index=[2023, 2024, 2025, 2026].index(record['annee']) if record['annee'] in [2023, 2024, 2025, 2026] else 0)
                    new_departement = st.selectbox("Département", ["Fatick", "Foundiougne", "Gossas", "Région"], index=["Fatick", "Foundiougne", "Gossas", "Région"].index(record['departement']) if record['departement'] in ["Fatick", "Foundiougne", "Gossas", "Région"] else 0)
                    
                    st.markdown("**Demandeurs d'emploi**")
                    col1, col2 = st.columns(2)
                    with col1:
                        new_manoeuvres_h = st.number_input("Manœuvres - Hommes", value=record['manoeuvres_hommes'], step=1)
                        new_employes_h = st.number_input("Employés - Hommes", value=record['employes_hommes'], step=1)
                    with col2:
                        new_manoeuvres_f = st.number_input("Manœuvres - Femmes", value=record['manoeuvres_femmes'], step=1)
                        new_employes_f = st.number_input("Employés - Femmes", value=record['employes_femmes'], step=1)
                    
                    st.markdown("**Établissements**")
                    col1, col2 = st.columns(2)
                    with col1:
                        new_etab_ouverts = st.number_input("Établissements ouverts", value=record['etablissements_ouverts'], step=1)
                    with col2:
                        new_etab_fermes = st.number_input("Établissements fermés", value=record['etablissements_fermes'], step=1)
                    
                    st.markdown("**Statut juridique**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        new_ei = st.number_input("EI", value=record['ei'], step=1)
                        new_sarl = st.number_input("SARL", value=record['sarl'], step=1)
                        new_gie = st.number_input("GIE", value=record['gie'], step=1)
                    with col2:
                        new_sa = st.number_input("SA", value=record['sa'], step=1)
                        new_suarl = st.number_input("SUARL", value=record['suarl'], step=1)
                        new_ong = st.number_input("ONG", value=record['ong'], step=1)
                    with col3:
                        new_autres_statuts = st.number_input("Autres", value=record['autres_statuts'], step=1)
                    
                    st.markdown("**Emplois**")
                    col1, col2 = st.columns(2)
                    with col1:
                        new_emplois_gen = st.number_input("Emplois générés", value=record['emplois_generes'], step=1)
                    with col2:
                        new_emplois_per = st.number_input("Emplois perdus", value=record['emplois_perdus'], step=1)
                    
                    st.markdown("**Contrats de travail**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Hommes**")
                        new_cdi_h = st.number_input("CDI - Hommes", value=record['cdi_hommes'], step=1)
                        new_cdd_h = st.number_input("CDD - Hommes", value=record['cdd_hommes'], step=1)
                        new_saisonnier_h = st.number_input("Saisonnier - Hommes", value=record['saisonnier_hommes'], step=1)
                        new_apprentissage_h = st.number_input("Apprentissage - Hommes", value=record['apprentissage_hommes'], step=1)
                        new_temporaire_h = st.number_input("Temporaire - Hommes", value=record['temporaire_hommes'], step=1)
                        new_stage_h = st.number_input("Stage - Hommes", value=record['stage_hommes'], step=1)
                    with col2:
                        st.markdown("**Femmes**")
                        new_cdi_f = st.number_input("CDI - Femmes", value=record['cdi_femmes'], step=1)
                        new_cdd_f = st.number_input("CDD - Femmes", value=record['cdd_femmes'], step=1)
                        new_saisonnier_f = st.number_input("Saisonnier - Femmes", value=record['saisonnier_femmes'], step=1)
                        new_apprentissage_f = st.number_input("Apprentissage - Femmes", value=record['apprentissage_femmes'], step=1)
                        new_temporaire_f = st.number_input("Temporaire - Femmes", value=record['temporaire_femmes'], step=1)
                        new_stage_f = st.number_input("Stage - Femmes", value=record['stage_femmes'], step=1)
                    
                    st.markdown("**Conflits de travail**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Individuels**")
                        new_indiv_conciliation = st.number_input("Conciliation", value=record['conflit_indiv_conciliation'], step=1)
                        new_indiv_partielle = st.number_input("Conciliation partielle", value=record['conflit_indiv_partielle'], step=1)
                        new_indiv_non = st.number_input("Non conciliation", value=record['conflit_indiv_non'], step=1)
                    with col2:
                        st.markdown("**Collectifs**")
                        new_coll_conciliation = st.number_input("Conciliation", value=record['conflit_collectif_conciliation'], step=1)
                        new_coll_partielle = st.number_input("Conciliation partielle", value=record['conflit_collectif_partielle'], step=1)
                        new_coll_non = st.number_input("Non conciliation", value=record['conflit_collectif_non'], step=1)
                    
                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        if st.form_submit_button("✅ Enregistrer les modifications"):
                            data = (
                                new_annee, new_departement,
                                new_manoeuvres_h, new_manoeuvres_f,
                                new_employes_h, new_employes_f,
                                new_etab_ouverts, new_etab_fermes,
                                new_ei, new_sa, new_sarl, new_suarl,
                                new_gie, new_ong, new_autres_statuts,
                                new_emplois_gen, new_emplois_per,
                                new_cdi_h, new_cdi_f,
                                new_cdd_h, new_cdd_f,
                                new_saisonnier_h, new_saisonnier_f,
                                new_apprentissage_h, new_apprentissage_f,
                                new_temporaire_h, new_temporaire_f,
                                new_stage_h, new_stage_f,
                                new_indiv_conciliation, new_indiv_partielle, new_indiv_non,
                                new_coll_conciliation, new_coll_partielle, new_coll_non,
                                st.session_state.edit_id
                            )
                            update_travail(data)
                            st.session_state.edit_mode = False
                            st.session_state.edit_id = None
                            st.success("✅ Enregistrement modifié avec succès.")
                            st.rerun()
                    with col_cancel:
                        if st.form_submit_button("❌ Annuler"):
                            st.session_state.edit_mode = False
                            st.session_state.edit_id = None
                            st.rerun()
            
            elif secteur_choisi == "Tourisme":
                with st.form(key="edit_form_tourisme"):
                    new_annee = st.selectbox("Année", [2024, 2025, 2026], index=[2024, 2025, 2026].index(record['annee']) if record['annee'] in [2024, 2025, 2026] else 0)
                    new_departement = st.selectbox("Département", ["Fatick", "Foundiougne", "Gossas", "Région"], index=["Fatick", "Foundiougne", "Gossas", "Région"].index(record['departement']) if record['departement'] in ["Fatick", "Foundiougne", "Gossas", "Région"] else 0)
                    
                    # Bloc A
                    st.markdown("**Infrastructures**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        new_hotel_receptifs = st.number_input("Hôtel - Réceptifs", value=record['hotel_receptifs'], step=1)
                    with col2:
                        new_hotel_chambres = st.number_input("Hôtel - Chambres", value=record['hotel_chambres'], step=1)
                    with col3:
                        new_hotel_lits = st.number_input("Hôtel - Lits", value=record['hotel_lits'], step=1)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        new_auberge_receptifs = st.number_input("Auberge - Réceptifs", value=record['auberge_receptifs'], step=1)
                    with col2:
                        new_auberge_chambres = st.number_input("Auberge - Chambres", value=record['auberge_chambres'], step=1)
                    with col3:
                        new_auberge_lits = st.number_input("Auberge - Lits", value=record['auberge_lits'], step=1)
                    
                    # Bloc B - simplifié
                    st.markdown("**Arrivées par provenance**")
                    col1, col2 = st.columns(2)
                    with col1:
                        new_france = st.number_input("France", value=record['france'], step=1)
                        new_autres_pays_europeens = st.number_input("Autres pays européens", value=record['autres_pays_europeens'], step=1)
                        new_usa = st.number_input("USA", value=record['usa'], step=1)
                    with col2:
                        new_senegal = st.number_input("Sénégal", value=record['senegal'], step=1)
                        new_autres_pays_africains = st.number_input("Autres pays africains", value=record['autres_pays_africains'], step=1)
                    
                    # Bloc C - simplifié
                    st.markdown("**Occupation**")
                    col1, col2 = st.columns(2)
                    with col1:
                        new_hotel_nuitees = st.number_input("Hôtel - Nuitées", value=record['hotel_nuitees'], step=1)
                        new_hotel_taux = st.number_input("Hôtel - Taux occupation (%)", value=record['hotel_taux_occupation'], step=0.01, format="%.2f")
                    with col2:
                        new_auberge_nuitees = st.number_input("Auberge - Nuitées", value=record['auberge_nuitees'], step=1)
                        new_auberge_taux = st.number_input("Auberge - Taux occupation (%)", value=record['auberge_taux_occupation'], step=0.01, format="%.2f")
                    
                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        if st.form_submit_button("✅ Enregistrer les modifications"):
                            data = (
                                new_annee, new_departement,
                                new_hotel_receptifs, new_hotel_chambres, new_hotel_lits,
                                new_auberge_receptifs, new_auberge_chambres, new_auberge_lits,
                                record['campement_touristique_receptifs'], record['campement_touristique_chambres'], record['campement_touristique_lits'],
                                record['campement_chasse_receptifs'], record['campement_chasse_chambres'], record['campement_chasse_lits'],
                                record['relais_receptifs'], record['relais_chambres'], record['relais_lits'],
                                record['gite_receptifs'], record['gite_chambres'], record['gite_lits'],
                                record['lodge_receptifs'], record['lodge_chambres'], record['lodge_lits'],
                                record['centre_accueil_receptifs'], record['centre_accueil_chambres'], record['centre_accueil_lits'],
                                new_france, new_autres_pays_europeens, new_usa, record['autres_pays_americains'], 
                                new_senegal, new_autres_pays_africains, record['asie'], record['oceanie'],
                                new_hotel_nuitees, new_hotel_taux,
                                new_auberge_nuitees, new_auberge_taux,
                                record['campement_touristique_nuitees'], record['campement_touristique_taux_occupation'],
                                record['campement_chasse_nuitees'], record['campement_chasse_taux_occupation'],
                                record['relais_nuitees'], record['relais_taux_occupation'],
                                record['gite_nuitees'], record['gite_taux_occupation'],
                                record['lodge_nuitees'], record['lodge_taux_occupation'],
                                record['centre_accueil_nuitees'], record['centre_accueil_taux_occupation'],
                                st.session_state.edit_id
                            )
                            update_tourisme(data)
                            st.session_state.edit_mode = False
                            st.session_state.edit_id = None
                            st.success("✅ Enregistrement modifié avec succès.")
                            st.rerun()
                    with col_cancel:
                        if st.form_submit_button("❌ Annuler"):
                            st.session_state.edit_mode = False
                            st.session_state.edit_id = None
                            st.rerun()
            
            else:  # NINEA
                with st.form(key="edit_form_ninea"):
                    new_nom_complet = st.text_input("Nom complet", value=record['nom_complet'])
                    new_cni = st.text_input("CNI", value=record['cni'])
                    new_sexe = st.selectbox("Sexe", ["Masculin", "Féminin"], index=0 if record['sexe'] == "Masculin" else 1)
                    new_activite = st.text_input("Activité principale", value=record['activite_principale'])
                    new_regime = st.selectbox("Régime", ["Personne physique", "Personne morale"], index=0 if record['regime'] == "Personne physique" else 1)
                    new_forme = st.selectbox("Forme juridique", [
                        "ENTREPRISE INDIVIDUELLE", "GIE", "SARL", "SAS", "SNC",
                        "COOPERATIVE", "ASSOCIATION", "ONG", "ENTREPRISE PUBLIQUE"
                    ], index=0)
                    new_date = st.date_input("Date de dépôt", value=pd.to_datetime(record['date_depot']).date())
                    new_commune = st.selectbox("Commune", communes, index=communes.index(record['commune']) if record['commune'] in communes else 0)
                    new_departement = st.selectbox("Département", ["Fatick", "Foundiougne", "Gossas"], index=["Fatick", "Foundiougne", "Gossas"].index(record['departement']) if record['departement'] in ["Fatick", "Foundiougne", "Gossas"] else 0)
                    
                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        if st.form_submit_button("✅ Enregistrer les modifications"):
                            data = (new_nom_complet, new_cni, new_sexe, new_activite, new_regime,
                                    new_forme, new_date.strftime("%Y-%m-%d"), new_commune, new_departement,
                                    secteur_choisi, st.session_state.edit_id)
                            update_ninea(data)
                            st.session_state.edit_mode = False
                            st.session_state.edit_id = None
                            st.success("✅ Enregistrement modifié avec succès.")
                            st.rerun()
                    with col_cancel:
                        if st.form_submit_button("❌ Annuler"):
                            st.session_state.edit_mode = False
                            st.session_state.edit_id = None
                            st.rerun()
    
    # ==========================================
    # QUATRE BOUTONS EN BAS (EXPORT, IMPORT, VIDER, SYNCHRONISER)
    # ==========================================
    st.markdown("---")
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    
    with col_btn1:
        if not df_collecte.empty:
            csv_data = df_collecte.drop(columns=['synchro'], errors='ignore').to_csv(index=False)
            st.download_button("📥 Exporter CSV", csv_data, f"export_{secteur_choisi}_{datetime.now():%Y%m%d_%H%M%S}.csv", "text/csv")
        else:
            st.button("📥 Exporter CSV", disabled=True)
    
    with col_btn2:
        uploaded_file = st.file_uploader("📂 Importer CSV", type=["csv"], key="import_csv")
        if uploaded_file is not None:
            try:
                df_import = pd.read_csv(uploaded_file)
                if secteur_choisi == "Travail":
                    required_cols = ['annee', 'departement']
                    if all(col in df_import.columns for col in required_cols):
                        mode = st.radio("Mode d'import", ["Remplacer", "Ajouter (sans doublons)"], horizontal=True, key="mode_import_travail")
                        if st.button("Lancer l'import", key="btn_import_travail"):
                            if mode == "Remplacer":
                                ins, err = replace_all_travail(df_import)
                                st.success(f"✅ {ins} lignes insérées, {err} erreurs.")
                            else:
                                ins, skip = add_missing_travail(df_import)
                                st.success(f"✅ {ins} ajoutées, {skip} doublons ignorés.")
                            st.rerun()
                    else:
                        st.error("Colonnes requises manquantes.")
                elif secteur_choisi == "Artisanat":
                    required_cols = ['annee', 'departement']
                    if all(col in df_import.columns for col in required_cols):
                        mode = st.radio("Mode d'import", ["Remplacer", "Ajouter (sans doublons)"], horizontal=True, key="mode_import_artisanat")
                        if st.button("Lancer l'import", key="btn_import_artisanat"):
                            if mode == "Remplacer":
                                ins, err = replace_all_artisanat(df_import)
                                st.success(f"✅ {ins} lignes insérées, {err} erreurs.")
                            else:
                                ins, skip = add_missing_artisanat(df_import)
                                st.success(f"✅ {ins} ajoutées, {skip} doublons ignorés.")
                            st.rerun()
                    else:
                        st.error("Colonnes requises manquantes.")
                elif secteur_choisi == "Tourisme":
                    required_cols = ['annee', 'departement']
                    if all(col in df_import.columns for col in required_cols):
                        mode = st.radio("Mode d'import", ["Remplacer", "Ajouter (sans doublons)"], horizontal=True, key="mode_import_tourisme")
                        if st.button("Lancer l'import", key="btn_import_tourisme"):
                            if mode == "Remplacer":
                                ins, err = replace_all_tourisme(df_import)
                                st.success(f"✅ {ins} lignes insérées, {err} erreurs.")
                            else:
                                ins, skip = add_missing_tourisme(df_import)
                                st.success(f"✅ {ins} ajoutées, {skip} doublons ignorés.")
                            st.rerun()
                    else:
                        st.error("Colonnes requises manquantes.")
                else:
                    required_cols = ['nom_complet', 'cni', 'sexe', 'activite_principale', 'regime',
                                     'forme_juridique', 'date_depot', 'commune', 'departement']
                    if all(col in df_import.columns for col in required_cols):
                        if 'secteur' not in df_import.columns:
                            df_import['secteur'] = secteur_choisi
                        mode = st.radio("Mode d'import", ["Remplacer", "Ajouter (sans doublons)"], horizontal=True, key="mode_import_ninea")
                        if st.button("Lancer l'import", key="btn_import_ninea"):
                            if mode == "Remplacer":
                                ins, err = replace_all_ninea(df_import)
                                st.success(f"✅ {ins} lignes insérées, {err} erreurs.")
                            else:
                                ins, skip = add_missing_ninea(df_import)
                                st.success(f"✅ {ins} ajoutées, {skip} doublons ignorés.")
                            st.rerun()
                    else:
                        st.error("Colonnes requises manquantes.")
            except Exception as e:
                st.error(f"Erreur : {e}")
    
    with col_btn3:
        if secteur_choisi == "Travail":
            if st.button("🗑️ Vider toutes les données", key="btn_vider_travail"):
                st.session_state.confirm_delete_travail = True
        elif secteur_choisi == "Artisanat":
            if st.button("🗑️ Vider toutes les données", key="btn_vider_artisanat"):
                st.session_state.confirm_delete_artisanat = True
        elif secteur_choisi == "Tourisme":
            if st.button("🗑️ Vider toutes les données", key="btn_vider_tourisme"):
                st.session_state.confirm_delete_tourisme = True
        else:
            if st.button("🗑️ Vider toutes les données", key="btn_vider_ninea"):
                st.session_state.confirm_delete_ninea = True
    
    with col_btn4:
        if secteur_choisi == "Travail":
            if st.button("🔄 Synchroniser", key="btn_sync_travail"):
                with st.spinner("Synchronisation en cours..."):
                    ins, skip, err, msg = synchroniser_travail_vers_postgresql()
                    if msg:
                        st.error(msg)
                    else:
                        st.success(f"✅ {ins} ajoutées, {skip} existantes, {err} erreurs.")
                        st.rerun()
        elif secteur_choisi == "Artisanat":
            if st.button("🔄 Synchroniser", key="btn_sync_artisanat"):
                with st.spinner("Synchronisation en cours..."):
                    ins, skip, err, msg = synchroniser_artisanat_vers_postgresql()
                    if msg:
                        st.error(msg)
                    else:
                        st.success(f"✅ {ins} ajoutées, {skip} existantes, {err} erreurs.")
                        st.rerun()
        elif secteur_choisi == "Tourisme":
            if st.button("🔄 Synchroniser", key="btn_sync_tourisme"):
                with st.spinner("Synchronisation en cours..."):
                    ins, skip, err, msg = synchroniser_tourisme_vers_postgresql()
                    if msg:
                        st.error(msg)
                    else:
                        st.success(f"✅ {ins} ajoutées, {skip} existantes, {err} erreurs.")
                        st.rerun()
        else:
            if st.button("🔄 Synchroniser", key="btn_sync_ninea"):
                with st.spinner("Synchronisation en cours..."):
                    st.info("Synchronisation des secteurs NINEA en cours de développement...")
    
    # Confirmations de vidage
    if st.session_state.confirm_delete_travail:
        st.markdown('<div class="warning-message">⚠️ Supprimer TOUTES les données du secteur Travail ?</div>', unsafe_allow_html=True)
        col_yes, col_no = st.columns(2)
        if col_yes.button("✅ Oui, tout supprimer", key="confirm_travail_yes"):
            delete_all_travail()
            st.session_state.confirm_delete_travail = False
            st.success("Base Travail vidée.")
            st.rerun()
        if col_no.button("❌ Annuler", key="confirm_travail_no"):
            st.session_state.confirm_delete_travail = False
            st.rerun()
    
    if st.session_state.confirm_delete_artisanat:
        st.markdown('<div class="warning-message">⚠️ Supprimer TOUTES les données du secteur Artisanat ?</div>', unsafe_allow_html=True)
        col_yes, col_no = st.columns(2)
        if col_yes.button("✅ Oui, tout supprimer", key="confirm_artisanat_yes"):
            delete_all_artisanat()
            st.session_state.confirm_delete_artisanat = False
            st.success("Base Artisanat vidée.")
            st.rerun()
        if col_no.button("❌ Annuler", key="confirm_artisanat_no"):
            st.session_state.confirm_delete_artisanat = False
            st.rerun()
    
    if st.session_state.confirm_delete_tourisme:
        st.markdown('<div class="warning-message">⚠️ Supprimer TOUTES les données du secteur Tourisme ?</div>', unsafe_allow_html=True)
        col_yes, col_no = st.columns(2)
        if col_yes.button("✅ Oui, tout supprimer", key="confirm_tourisme_yes"):
            delete_all_tourisme()
            st.session_state.confirm_delete_tourisme = False
            st.success("Base Tourisme vidée.")
            st.rerun()
        if col_no.button("❌ Annuler", key="confirm_tourisme_no"):
            st.session_state.confirm_delete_tourisme = False
            st.rerun()
    
    if st.session_state.confirm_delete_ninea:
        st.markdown('<div class="warning-message">⚠️ Supprimer TOUTES les données du secteur ?</div>', unsafe_allow_html=True)
        col_yes, col_no = st.columns(2)
        if col_yes.button("✅ Oui, tout supprimer", key="confirm_ninea_yes"):
            delete_all_ninea()
            st.session_state.confirm_delete_ninea = False
            st.success("Base vidée.")
            st.rerun()
        if col_no.button("❌ Annuler", key="confirm_ninea_no"):
            st.session_state.confirm_delete_ninea = False
            st.rerun()

# ===============================
# FIN
# ===============================