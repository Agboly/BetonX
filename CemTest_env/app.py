import streamlit as st
import pandas as pd
import sqlite3
from dbVisualize import afficher_tables_sqlite
from exploreData import afficher_resume_statistiques
from imputeData import corriger_valeurs_manquantes

st.set_page_config(page_title="Essai Béton", layout="wide")

page = st.sidebar.selectbox("Navigation", ["Accueil", "Visualisation", "Exploration", "Correction"])

if page == "Accueil":
    st.title("🧱 Bienvenue sur l'application Essai Béton")
    st.markdown("""
    ## Objectif 🎯
    Cette application permet :
    - de récupérer les données d'essais béton
    - de les stocker dans une base SQLite
    - de visualiser et télécharger les données

    ➡️ Utilisez le menu à gauche pour accéder aux différentes fonctionnalités.
    """)

elif page == "Visualisation":
    afficher_tables_sqlite()

elif page == "Exploration":
    st.title("Exploration simple - Histogramme")

    db_path = "dataBeton.db"
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM NSB_Liste_273983CC", conn)
    conn.close()

    afficher_resume_statistiques(df)


elif page == "Correction":
    st.title("Correction des valeurs manquantes")
    db_path = "dataBeton.db"
    from imputeData import corriger_valeurs_manquantes
    corriger_valeurs_manquantes(db_path, "NSB_Liste_273983CC")

