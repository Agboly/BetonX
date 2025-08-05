# evalAnomalies.py
import streamlit as st
from sklearn.ensemble import IsolationForest
import pandas as pd

def detecter_anomalies(df):
    st.write("🔍 Analyse automatique avec Isolation Forest")

    # Colonnes numériques pour la détection
    features = ["jour_1", "jour_3", "jour_7", "jour_28", "jour_56", "slump", "temperature", "volume"]
    df_features = df[features].dropna()

    if df_features.empty:
        st.warning("Pas assez de données complètes pour la détection.")
        return

    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(df_features)
    df_features["anomalie"] = model.predict(df_features)
    df_features["anomalie"] = df_features["anomalie"].map({1: "Normal", -1: "Anomalie"})

    st.subheader("🚨 Résultats de la détection")
    st.dataframe(df_features, use_container_width=True)

    anomalies = df_features[df_features["anomalie"] == "Anomalie"]
    st.error(f"{len(anomalies)} anomalies détectées sur {len(df_features)} lignes.")
