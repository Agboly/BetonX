import streamlit as st
import pandas as pd
import sqlite3


def charger_donnees_sqlite(table_name="NSB_Liste_273983CC", db_path="dataBeton.db"):
    try:
        with sqlite3.connect(db_path) as conn:
            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return pd.DataFrame()

    # Colonnes numériques attendues (adapter selon ta base)
    colonnes_num = ["slump", "volume", "temperature", "jour_1", "jour_3", "jour_7", "jour_28", "jour_56"]

    for col in colonnes_num:
        if col in df.columns:
            # Remplace ',' par '.' puis convertit en float, coercer en NaN si échec
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')

    return df


def nettoyer_dataframe(df):
    colonnes_flottantes = ["jour_1", "jour_3", "jour_7", "jour_28", "jour_56", "slump", "volume", "temperature"]
    for col in colonnes_flottantes:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def afficher_resume(df):
    st.subheader("📊 Résumé statistique des données")
    st.write(df.describe())

    st.subheader("🔎 Valeurs manquantes par colonne")
    valeurs_manquantes = df.isnull().sum()
    valeurs_manquantes = valeurs_manquantes[valeurs_manquantes > 0]

    if not valeurs_manquantes.empty:
        st.write(valeurs_manquantes)

        st.subheader("📌 Détails des lignes avec des valeurs manquantes")
        lignes_incompletes = df[df.isnull().any(axis=1)]
        st.dataframe(lignes_incompletes)
    else:
        st.success("✅ Aucune valeur manquante détectée.")

    # ➕ Moyennes des résistances par âge et par formule
    st.subheader("📈 Moyennes des résistances par âge et par formule de béton")

    colonnes_resistance = ["jour_1", "jour_3", "jour_7", "jour_28", "jour_56"]
    if "formule" in df.columns:
        moyennes = df.groupby("formule")[colonnes_resistance].mean().round(2)
        st.dataframe(moyennes)
    else:
        st.warning("⚠️ La colonne 'formule' est absente du dataset.")
