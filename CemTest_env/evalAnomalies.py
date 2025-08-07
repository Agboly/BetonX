import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import IsolationForest
from correctionAnomalies import corriger_valeurs_anormales

def detecter_anomalies_app(df):
    st.title("🔎 Détection d'anomalies")
    st.write("Cette section permet de détecter automatiquement les valeurs anormales dans toutes les colonnes numériques (résistances, slump, température).")

    colonnes_analyse = ["jour_1", "jour_3", "jour_7", "jour_28", "jour_56", "slump", "temperature"]
    colonnes_presentes = [col for col in colonnes_analyse if col in df.columns]

    identifiant_colonne = "numeroNSB" if "numeroNSB" in df.columns else "NumeroBL"

    if not colonnes_presentes:
        st.warning("Aucune des colonnes cibles n’est présente dans les données.")
        return

    anomalies_globales = []

    for col in colonnes_presentes:
        data_col = df[[identifiant_colonne] + colonnes_presentes].dropna(subset=[col])

        if data_col.empty or len(data_col) < 10:
            st.info(f"Pas assez de données pour analyser la colonne '{col}'.")
            continue

        model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
        model.fit(data_col[[col]])

        pred = model.predict(data_col[[col]])
        data_col["anomalie"] = pred
        data_col["anomalie"] = data_col["anomalie"].map({1: "Normal", -1: "Anomalie"})

        anomalies = data_col[data_col["anomalie"] == "Anomalie"].copy()
        anomalies["colonne_concernee"] = col

        anomalies_globales.append(anomalies)

    # Résumé global
    st.subheader("📊 Résumé global des anomalies détectées")

    if anomalies_globales:
        df_anomalies = pd.concat(anomalies_globales, ignore_index=True)

        colonnes_finales = [identifiant_colonne] + colonnes_presentes + ["colonne_concernee", "anomalie"]
        df_anomalies = df_anomalies[colonnes_finales]

        st.error(f"{len(df_anomalies)} anomalies détectées au total.")
        st.dataframe(df_anomalies, use_container_width=True)

        # Graphique global des anomalies par colonne
        st.subheader("📊 Nombre d’anomalies par champ")
        anomalies_par_col = df_anomalies[df_anomalies["anomalie"] == "Anomalie"]["colonne_concernee"].value_counts().reset_index()
        anomalies_par_col.columns = ["Champ", "Nombre d’anomalies"]

        fig = px.bar(
            anomalies_par_col,
            x="Champ",
            y="Nombre d’anomalies",
            color="Champ",
            title="Nombre d’anomalies détectées par champ",
            text="Nombre d’anomalies"
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(showlegend=False, yaxis_title="Nombre d’anomalies", xaxis_title="Champ")
        st.plotly_chart(fig, use_container_width=True)

        # Téléchargement CSV
        csv = df_anomalies.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Télécharger les anomalies en CSV",
            data=csv,
            file_name="anomalies_detectees.csv",
            mime="text/csv"
        )
    else:
        st.success("Aucune anomalie détectée dans les colonnes analysées.")

    df_anomalies.rename(columns={"colonne_concernee": "colonnes_anormales"}, inplace=True)
    corriger_valeurs_anormales(df_anomalies, table_name="mesures_normalisees")
