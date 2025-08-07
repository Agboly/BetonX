# app.py

import streamlit as st
from exploreData import charger_donnees_sqlite, nettoyer_dataframe, afficher_resume
from evalAnomalies import detecter_anomalies_app  # 🆕 Détection automatique des anomalies
from imputeData import corriger_valeurs_manquantes
from imputeData import corriger_valeurs_anormales

import plotly.express as px



st.set_page_config(page_title="Analyse Béton", layout="wide")
st.title("🧱 BetonX : Application intelligente d’analyse des résistances du béton")

# Onglets
tab1, tab2, tab3, tab4 = st.tabs(["📅 Chargement & Nettoyage", "📊 Exploration", "🚨 Anomalies", "🛠 Correction manuelle", ])

# Nom de la table
table = "NSB_Liste_273983CC"

# 1. Chargement & Nettoyage
with tab1:
    st.header("📅 Chargement & Nettoyage des données")
    df = charger_donnees_sqlite(table_name=table)
    df_nettoye = nettoyer_dataframe(df)
    st.success("Données chargées et nettoyées depuis les formulaires de capture des valeurs d'essais beton sur le chantier.")
    st.dataframe(df_nettoye, use_container_width=True)

# 2. Exploration
with tab2:
    st.header("📊 Résumé Statistique")
    try:
        afficher_resume(df_nettoye)
    except Exception as e:
        st.error(f"Erreur lors de l'affichage du résumé : {e}")

# 3. Anomalies
with tab3:
    st.header("🚨 Détection automatique des anomalies")
    try:
        detecter_anomalies_app(df_nettoye)
    except Exception as e:
        st.error(f"Erreur lors de la détection d'anomalies : {e}")

# 4. Correction manuelle
with tab4:
    st.header("🛠 Interface de correction des valeurs manquantes")
    try:
        corriger_valeurs_manquantes(df_nettoye, table_name=table)
    except Exception as e:
        st.error(f"Erreur lors de la correction : {e}")
    
        corriger_valeurs_anormales()

