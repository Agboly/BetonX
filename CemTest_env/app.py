import streamlit as st
import pandas as pd
import joblib
import os
from exploreData import charger_donnees_sqlite, nettoyer_dataframe, afficher_resume
from evalAnomalies import detecter_anomalies_app  # 🆕 Détection automatique des anomalies
from imputeData import corriger_valeurs_manquantes, corriger_valeurs_anormales

st.set_page_config(page_title="Analyse Béton", layout="wide")
st.title("🧱 BetonX : Application intelligente d’analyse des résistances du béton")

# Onglets
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 Chargement & Nettoyage",
    "📊 Exploration",
    "🚨 Anomalies",
    "🛠 Correction manuelle",
    "🧠 Prédiction résistances"
])

# Nom de la table SQLite
table = "NSB_Liste_273983CC"

# 1. Chargement & Nettoyage
with tab1:
    st.header("📅 Chargement & Nettoyage des données")
    df = charger_donnees_sqlite(table_name=table)
    df_nettoye = nettoyer_dataframe(df)
    st.success("Données chargées et nettoyées depuis les formulaires de capture des valeurs d'essais béton sur le chantier.")
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
    st.header("🛠 Interface de correction des valeurs manquantes et anormales")
    try:
        corriger_valeurs_manquantes(df_nettoye, table_name=table)
    except Exception as e:
        st.error(f"Erreur lors de la correction des valeurs manquantes : {e}")

    try:
        corriger_valeurs_anormales()
    except Exception as e:
        st.error(f"Erreur lors de la correction des valeurs anormales : {e}")

import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "modele_multi_resistance.pkl")

@st.cache_data(show_spinner=False)
def charger_modele(path=MODEL_PATH):
    if not os.path.exists(path):
        st.error(f"Modèle introuvable : {path}. Veuillez d'abord entraîner le modèle avec 'trainModel.py'.")
        return None
    return joblib.load(path)


# 5. Prédiction résistances
with tab5:
    st.header("🧠 Prédiction des résistances du béton")
    try:
        modele = charger_modele()
        if modele is not None:
            slump = st.number_input("Slump", value=10.0, step=0.1)
            volume = st.number_input("Volume", value=100.0, step=0.1)
            temperature = st.number_input("Température", value=20.0, step=0.1)

            if st.button("Prédire"):
                X_new = pd.DataFrame([[slump, volume, temperature]], columns=["slump", "volume", "temperature"])
                preds = modele.predict(X_new)[0]
                st.success("Résistances prédites :")
                st.write(f"Jour 1  : {preds[0]:.2f} MPa")
                st.write(f"Jour 3  : {preds[1]:.2f} MPa")
                st.write(f"Jour 7  : {preds[2]:.2f} MPa")
                st.write(f"Jour 28 : {preds[3]:.2f} MPa")
                st.write(f"Jour 56 : {preds[4]:.2f} MPa")
        else:
            st.warning("Le modèle n'est pas chargé, impossible de faire des prédictions.")
    except Exception as e:
        st.error(f"Erreur lors de la prédiction : {e}")
