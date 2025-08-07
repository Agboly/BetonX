# imputeData.py
import streamlit as st
import sqlite3
import pandas as pd

def corriger_valeurs_manquantes(df, table_name, db_path="dataBeton.db"):
    st.subheader("🛠 Correction manuelle des valeurs manquantes")

    lignes_na = df[df.isnull().any(axis=1)]
    lignes_na = lignes_na[lignes_na["numeroNSB"].notnull()]

    if lignes_na.empty:
        st.info("Aucune ligne à corriger.")
    else:
        nsb_selectionne = st.selectbox("🔧 Sélectionnez un `numeroNSB` à corriger :", lignes_na["numeroNSB"].unique(), key="manquantes")
        ligne_cible = lignes_na[lignes_na["numeroNSB"] == nsb_selectionne].iloc[0]

        with st.form(f"form_correction_manquantes_{nsb_selectionne}"):
            st.write("Modifier les valeurs manquantes :")

            corrections = {}
            colonnes_modifiables = ["volume", "slump", "temperature", "jour_1", "jour_3", "jour_7", "jour_28", "jour_56"]

            for col in colonnes_modifiables:
                if col in ligne_cible.index and pd.isnull(ligne_cible[col]):
                    nouvelle_val = st.number_input(f"{col} (actuellement manquant)", value=0.0, step=0.1, key=f"{col}_manquant")
                    corrections[col] = nouvelle_val

            submit = st.form_submit_button("✅ Appliquer la correction")

            if submit and corrections:
                try:
                    with sqlite3.connect(db_path) as conn:
                        for col, val in corrections.items():
                            conn.execute(
                                f"UPDATE {table_name} SET {col} = ? WHERE numeroNSB = ?", (val, nsb_selectionne)
                            )
                        conn.commit()

                    st.success("✅ Correction enregistrée pour valeurs manquantes.")
                except Exception as e:
                    st.error(f"Erreur : {e}")


import sqlite3
import pandas as pd
import streamlit as st

def corriger_valeurs_anormales(df_anomalies: pd.DataFrame, table_name: str):
    """
    Permet de corriger manuellement les valeurs anormales détectées.
    Les corrections sont sauvegardées dans la table "corrections_anomalies" de la base de données.
    """
    if df_anomalies.empty:
        st.info("Aucune valeur anormale à corriger.")
        return

    st.subheader("🛠️ Correction manuelle des valeurs anormales")
    identifiant_colonne = "numeroNSB" if "numeroNSB" in df_anomalies.columns else "NumeroBL"

    # Regrouper les anomalies par identifiant et concaténer les colonnes concernées
    df_anomalies_grouped = (
        df_anomalies.groupby(identifiant_colonne)
        .agg({
            **{col: "first" for col in df_anomalies.columns if col not in ["colonnes_anormales", "anomalie"]},
            "colonnes_anormales": lambda x: ", ".join(sorted(set(x)))
        })
        .reset_index()
    )

    colonnes_correction = df_anomalies.columns.difference(["anomalie", "colonnes_anormales"]).tolist()
    modifications = []

    for i, row in df_anomalies_grouped.iterrows():
        st.markdown(f"**🔎 Anomalie détectée pour {identifiant_colonne} : {row[identifiant_colonne]}**")
        st.markdown(f"Colonnes concernées : `{row['colonnes_anormales']}`")

        ligne_modifiee = {}
        for col in row['colonnes_anormales'].split(", "):
            val_actuelle = row[col]
            val_corrigee = st.text_input(f"Modifier la valeur de {col}", value=str(val_actuelle), key=f"{row[identifiant_colonne]}_{col}")

            if str(val_corrigee) != str(val_actuelle):
                ligne_modifiee[col] = val_corrigee

        if ligne_modifiee:
            ligne_modifiee[identifiant_colonne] = row[identifiant_colonne]
            modifications.append(ligne_modifiee)

    if modifications:
        st.success("Des corrections ont été saisies. Elles seront enregistrées ci-dessous.")
        df_modifs = pd.DataFrame(modifications)
        st.dataframe(df_modifs, use_container_width=True)

        enregistrer_corrections(df_modifs, identifiant_colonne)
    else:
        st.info("Aucune correction n’a été effectuée.")

def enregistrer_corrections(df_modifications: pd.DataFrame, identifiant_colonne: str):
    """
    Enregistre les corrections dans la base de données (table: corrections_anomalies).
    """
    conn = sqlite3.connect("donnees_beton.db")
    cursor = conn.cursor()

    # Créer la table si elle n’existe pas
    colonnes_sql = ", ".join([f"{col} TEXT" for col in df_modifications.columns])
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS corrections_anomalies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {colonnes_sql}
        )
    """)

    # Insertion des données
    for _, row in df_modifications.iterrows():
        colonnes = ", ".join(row.index)
        placeholders = ", ".join(["?"] * len(row))
        valeurs = tuple(row.values)

        cursor.execute(f"""
            INSERT INTO corrections_anomalies ({colonnes})
            VALUES ({placeholders})
        """, valeurs)

    conn.commit()
    conn.close()
    st.success("✅ Corrections enregistrées avec succès dans la base de données.")
