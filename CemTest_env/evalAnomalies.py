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

    # ✅ Styliser les anomalies en rouge
    def surligner_anomalies(row):
        if row["anomalie"] == "Anomalie":
            return ["background-color: red; color: white"] * len(row)
        else:
            return [""] * len(row)

    # Créer une colonne d'explication des anomalies
    def expliquer_anomalie(row):
        if row["anomalie"] == "Anomalie":
            return f"Slump: {row['slump']}, Temp: {row['temperature']}°C, Formule: {row['formule']}"
        else:
            return ""

    df_long["explication_anomalie"] = df_long.apply(expliquer_anomalie, axis=1)


    # Afficher un tableau simplifié pour les anomalies uniquement
    st.subheader("🚨 Détail des anomalies détectées")
    df_anomalies = df_long[df_long["anomalie"] == "Anomalie"]
    df_anomalies_affiche = df_anomalies[[
        "numeroNSB", "formule", "age", "resistance", "slump", "temperature", "explication_anomalie"
    ]]
    st.dataframe(df_anomalies_affiche, use_container_width=True)


    # 📊 Graphique de dispersion
    st.subheader("📊 Histogramme des anomalies par âge")

    # S'assurer que 'age' est bien catégorique
    df_long["age"] = df_long["age"].astype(str)

    # Optionnel : trier les âges dans l’ordre croissant
    ages_ordonnes = sorted(df_long["age"].unique(), key=lambda x: int(x))

    fig_hist = px.histogram(
        df_long,
        x="age",
        color="anomalie",
        color_discrete_map={"Anomalie": "red", "Normal": "green"},
        barmode="overlay",
        category_orders={"age": ages_ordonnes},  # 🔍 forcer l’ordre des catégories
        title="Répartition des anomalies selon l'âge"
    )


    fig_hist.update_layout(
        xaxis_title="Âge (jours)",
        yaxis_title="Nombre de mesures",
        legend_title_text="Anomalie"
    )

    st.plotly_chart(fig_hist, use_container_width=True)




    # ✅ Résumé
    anomalies = df_long[df_long["anomalie"] == "Anomalie"]
    st.error(f"{len(anomalies)} anomalies détectées sur {len(df_long)} mesures.")
