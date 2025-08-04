# app.py

#Chargement des données depuis SQLite

# Nettoyage automatique des valeurs (virgules → points)

# Résumé statistique affiché

# Interface de correction interactive pour les valeurs manquantes (par numeroNSB)

# Écriture directe dans la base avec rechargement instantané


import streamlit as st
from exploreData import charger_donnees_sqlite, nettoyer_dataframe, afficher_resume
from imputeData import corriger_valeurs_manquantes

st.set_page_config(page_title="Analyse Béton", layout="wide")

st.title("🧱 Application d’analyse des résistances du béton")

# 1. Chargement
table = "NSB_Liste_273983CC"
df = charger_donnees_sqlite(table_name=table)

# 2. Nettoyage
df_nettoye = nettoyer_dataframe(df)

# 3. Exploration
afficher_resume(df_nettoye)

# 4. Correction manuelle
corriger_valeurs_manquantes(df_nettoye, table_name=table)
