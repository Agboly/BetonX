# Chargement + Exploration exploreData.py
import streamlit as st
import pandas as pd
import sqlite3

def charger_donnees_sqlite(table_name="NSB_Liste_273983CC", db_path="dataBeton.db"):
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
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
