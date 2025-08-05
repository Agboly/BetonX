import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder

def detecter_anomalies(df):
    st.write("🔍 Détection automatique des anomalies")

    colonnes_resistance = ["jour_1", "jour_3", "jour_7", "jour_28", "jour_56"]
    st.write("Colonnes du dataframe :", df.columns.tolist())

    # Format long
    try:
        df_long = df.melt(
            id_vars=["numeroNSB", "formule", "slump", "temperature", "volume"],
            value_vars=colonnes_resistance,
            var_name="age_jour",
            value_name="resistance"
        )
    except Exception as e:
        st.error(f"Erreur lors du melt : {e}")
        return

    df_long = df_long.dropna(subset=["resistance", "formule", "slump", "temperature"])

    st.write("Lignes après dropna :", len(df_long))
    if df_long.empty:
        st.warning("Pas assez de données après nettoyage.")
        return

    df_long["age"] = df_long["age_jour"].str.extract("jour_(\d+)").astype(int)
    df_long["formule_enc"] = LabelEncoder().fit_transform(df_long["formule"])

    features = ["resistance", "age", "formule_enc", "slump", "temperature"]
    df_features = df_long[features]
    st.write("Données utilisées pour le modèle :", df_features.head())

    try:
        model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        model.fit(df_features)
    except Exception as e:
        st.error(f"Erreur dans l'entraînement du modèle : {e}")
        return

    df_long["anomalie"] = model.predict(df_features)
    df_long["anomalie"] = df_long["anomalie"].map({1: "Normal", -1: "Anomalie"})

    st.subheader("🚨 Résultats de la détection")
    st.dataframe(df_long, use_container_width=True)

    fig = px.scatter(
        df_long, x="age", y="resistance",
        color="anomalie", symbol="formule",
        title="Visualisation des anomalies détectées",
        hover_data=["numeroNSB", "formule", "slump", "temperature"]
    )
    st.plotly_chart(fig, use_container_width=True)

    anomalies = df_long[df_long["anomalie"] == "Anomalie"]
    st.error(f"{len(anomalies)} anomalies détectées sur {len(df_long)} mesures.")
