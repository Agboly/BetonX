import streamlit as st
import pandas as pd

def afficher_resume_statistiques(df):
    st.subheader("Filtrage : Lignes avec une formule renseignée")

    # Nettoyage de la colonne "formule"
    df['formule'] = df['formule'].astype(str).str.strip()

    # Ne conserver que les lignes avec une formule non vide et non 'None'
    df_filtre = df[
        (df['formule'].notnull()) &
        (df['formule'] != "") &
        (df['formule'].str.lower() != "none")
    ]

    st.write(f"Nombre de lignes avec formule renseignée : {len(df_filtre)}")
    st.dataframe(df_filtre)

    # Conversion de la colonne datedeproduction
    if 'datedeproduction' in df_filtre.columns:
        df_filtre['datedeproduction'] = pd.to_datetime(df_filtre['datedeproduction'], errors='coerce')

    # Conversion des colonnes numériques
    colonnes_a_convertir = ["volume", "slump", "temperature", "jour_1", "jour_3", "jour_7", "jour_28", "jour_56"]
    for col in colonnes_a_convertir:
        if col in df_filtre.columns:
            if df_filtre[col].dtype == object:
                df_filtre[col] = df_filtre[col].str.replace(',', '.', regex=False)
            df_filtre[col] = pd.to_numeric(df_filtre[col], errors="coerce")

    # Calcul des dates associées aux jours
    jours_cols = ["jour_1", "jour_3", "jour_7", "jour_28", "jour_56"]
    for col in jours_cols:
        if col in df_filtre.columns and 'datedeproduction' in df_filtre.columns:
            jour_n = int(col.split("_")[1])
            df_filtre[f"date_{col}"] = df_filtre["datedeproduction"] + pd.to_timedelta(jour_n, unit="D")

    # Résumé statistique
    st.subheader("Résumé statistique des variables quantitatives")
    vars_quanti = df_filtre.select_dtypes(include=["float", "int"]).columns.tolist()
    if not vars_quanti:
        st.warning("Aucune variable quantitative détectée.")
    else:
        st.write(df_filtre[vars_quanti].describe())

    # Valeurs manquantes globales
    total_na = df_filtre.isnull().sum().sum()
    taux_na = (total_na / (df_filtre.shape[0] * df_filtre.shape[1])) * 100
    st.write(f"Nombre total de valeurs manquantes : {total_na}")
    st.write(f"Taux global de NA : {taux_na:.2f} %")

    st.subheader("Individus contenant des valeurs manquantes")
    lignes_na = df_filtre[df_filtre.isnull().any(axis=1)]
    if lignes_na.empty:
        st.success("Aucune ligne avec des valeurs manquantes.")
    else:
        st.write(f"{len(lignes_na)} lignes avec des valeurs manquantes :")
        st.dataframe(lignes_na)
        csv_lignes_na = lignes_na.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Télécharger ces lignes", csv_lignes_na, "lignes_avec_NA.csv", "text/csv")

    st.subheader("Analyse détaillée des valeurs manquantes par variable")
    colonnes_a_analyser = ["slump", "volume", "temperature", "jour_1", "jour_3", "jour_7", "jour_28", "jour_56"]
    for col in colonnes_a_analyser:
        if col in df_filtre.columns:
            na_lignes = df_filtre[df_filtre[col].isnull()]
            nb_na = len(na_lignes)
            st.write(f"📌 `{col}` a {nb_na} valeurs manquantes.")
            if nb_na > 0:
                sous_df = na_lignes[["numeroNSB", "formule"]].drop_duplicates()
                st.dataframe(sous_df)
                csv_na = sous_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    f"📥 Télécharger les NSB/formules manquants pour {col}",
                    csv_na,
                    f"NA_{col}.csv",
                    "text/csv"
                )
