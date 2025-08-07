import streamlit as st
import pandas as pd
import joblib
import os
import sqlite3
import numpy as np
import matplotlib.pyplot as plt

from exploreData import charger_donnees_sqlite, nettoyer_dataframe, afficher_resume
from evalAnomalies import detecter_anomalies_app
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

# Chemins
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "dataBeton.db")
MODEL_PATH = os.path.join(BASE_DIR, "model", "modele_multi_resistance.pkl")

@st.cache_data(show_spinner=False)
def charger_modele(path=MODEL_PATH):
    if not os.path.exists(path):
        st.error(f"Modèle introuvable : {path}. Veuillez d'abord entraîner le modèle avec 'trainModel.py'.")
        return None
    return joblib.load(path)

def get_resistances_mesurees(numeroNSB, conn):
    query = """
    SELECT Age, Resistance FROM (
        SELECT '1' AS Age, jour_1 AS Resistance FROM NSB_Liste_273983CC WHERE numeroNSB = ?
        UNION ALL
        SELECT '3' AS Age, jour_3 AS Resistance FROM NSB_Liste_273983CC WHERE numeroNSB = ?
        UNION ALL
        SELECT '7' AS Age, jour_7 AS Resistance FROM NSB_Liste_273983CC WHERE numeroNSB = ?
        UNION ALL
        SELECT '28' AS Age, jour_28 AS Resistance FROM NSB_Liste_273983CC WHERE numeroNSB = ?
        UNION ALL
        SELECT '56' AS Age, jour_56 AS Resistance FROM NSB_Liste_273983CC WHERE numeroNSB = ?
    )
    ORDER BY CAST(Age AS INTEGER)
    """
    params = (numeroNSB,) * 5
    df_mesure = pd.read_sql_query(query, conn, params=params)
    df_mesure["Age"] = df_mesure["Age"].astype(int)
    return df_mesure

def prepare_predictions_dataframe(preds):
    ages = [1, 3, 7, 28, 56]
    df_pred = pd.DataFrame({
        "Age": ages,
        "Resistance_predite": preds
    })
    return df_pred

def enregistrer_prediction(numeroNSB, preds, conn):
    ages = [1, 3, 7, 28, 56]
    for age, res_pred in zip(ages, preds):
        colonne = f"pred_jour_{age}"
        sql_update = f"""
        UPDATE NSB_Liste_273983CC
        SET {colonne} = ?
        WHERE numeroNSB = ?
        """
        conn.execute(sql_update, (float(res_pred), numeroNSB))
    conn.commit()

def prediction_avec_incertitude_multioutput(model, X_new):
    # Pour chaque sortie (5 sorties), calculer moyenne et std sur les arbres internes
    mean_preds = []
    std_preds = []
    for est in model.estimators_:
        all_preds = np.array([tree.predict(X_new) for tree in est.estimators_])
        mean_preds.append(np.mean(all_preds, axis=0)[0])
        std_preds.append(np.std(all_preds, axis=0)[0])
    return mean_preds, std_preds

# 5. Prédiction résistances
with tab5:
    st.header("🧠 Prédiction des résistances du béton")
    try:
        modele = charger_modele()
        if modele is None:
            st.warning("Le modèle n'est pas chargé, impossible de faire des prédictions.")
        else:
            conn = sqlite3.connect(DB_PATH)
            numeros = pd.read_sql_query(f"SELECT DISTINCT numeroNSB FROM {table} WHERE slump IS NOT NULL AND temperature IS NOT NULL AND volume IS NOT NULL", conn)
            if numeros.empty:
                st.warning("Aucun numéro NSB avec slump, température et volume disponibles.")
            else:
                numero_selectionne = st.selectbox("Sélectionnez un Numéro NSB", numeros["numeroNSB"].tolist())

                if numero_selectionne:
                    # Récupérer slump, volume, temperature les plus récents
                    df_param = pd.read_sql_query(f"""
                        SELECT slump, volume, temperature FROM {table}
                        WHERE numeroNSB = ?
                        ORDER BY rowid DESC LIMIT 1
                    """, conn, params=(numero_selectionne,))

                    if df_param.empty:
                        st.warning("Aucune donnée de paramètres disponibles pour ce numéro NSB.")
                    else:
                        slump_val = float(str(df_param["slump"].values[0]).replace(",", "."))
                        volume_val = float(str(df_param["volume"].values[0]).replace(",", "."))
                        temperature_val = float(str(df_param["temperature"].values[0]).replace(",", "."))

                        slump = st.number_input("Slump", value=slump_val, step=0.1)
                        volume = st.number_input("Volume", value=volume_val, step=0.1)
                        temperature = st.number_input("Température", value=temperature_val, step=0.1)

                        if st.button("Prédire"):
                            X_new = pd.DataFrame([[slump, volume, temperature]], columns=["slump", "volume", "temperature"])

                            # Prédiction + incertitude
                            try:
                                preds_mean, preds_std = prediction_avec_incertitude_multioutput(modele, X_new)
                            except Exception:
                                # fallback si modèle incompatible
                                preds_mean = modele.predict(X_new)[0]
                                preds_std = [0]*5

                            st.success("Résistances prédites :")
                            ages = [1, 3, 7, 28, 56]
                            for age, mean_pred, std_pred in zip(ages, preds_mean, preds_std):
                                st.write(f"Jour {age} : {mean_pred:.2f} MPa ± {std_pred:.2f}")

                            # Affichage des résistances mesurées
                            df_mesure = get_resistances_mesurees(numero_selectionne, conn)
                            if not df_mesure.empty:
                                df_pred = prepare_predictions_dataframe(preds_mean)

                                # Tableau comparatif
                                df_compare = pd.merge(df_mesure, df_pred, on="Age", how="outer")
                                st.subheader("Résistances mesurées vs prédites")
                                st.dataframe(df_compare)

                                # Graphique matplotlib
                                fig, ax = plt.subplots()
                                ax.plot(df_compare["Age"], df_compare["Resistance"], marker='o', label="Mesuré")
                                ax.plot(df_compare["Age"], df_compare["Resistance_predite"], marker='x', label="Prédit")
                                ax.set_xlabel("Âge (jours)")
                                ax.set_ylabel("Résistance (MPa)")
                                ax.set_title(f"Comparaison résistances pour {numero_selectionne}")
                                ax.legend()
                                ax.grid(True)
                                st.pyplot(fig)
                            else:
                                st.info("Pas de résistances mesurées disponibles pour ce Numéro NSB.")

                            # Enregistrer les prédictions dans la base
                            enregistrer_prediction(numero_selectionne, preds_mean, conn)

            conn.close()
    except Exception as e:
        st.error(f"Erreur lors de la prédiction : {e}")
