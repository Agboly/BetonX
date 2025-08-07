# correctionAnomalies.py

import streamlit as st
import pandas as pd
import sqlite3

def corriger_valeurs_anormales(df_anomalies, table_name, db_path="dataBeton.db"):
    st.subheader("🛠 Correction manuelle des valeurs anormales")

    if df_anomalies.empty:
        st.info("Aucune anomalie détectée à corriger.")
        return

    nsb_selectionne = st.selectbox("Sélectionnez un `numeroNSB` à corriger :", df_anomalies["numeroNSB"].unique())
    ligne_anormale = df_anomalies[df_anomalies["numeroNSB"] == nsb_selectionne].iloc[0]

    colonnes_anormales = ligne_anormale["colonnes_anormales"].split(", ")

    # Charger les données originales pour ce numeroNSB
    with sqlite3.connect(db_path) as conn:
        ligne_complete = pd.read_sql_query(
            f"SELECT * FROM {table_name} WHERE numeroNSB = ?", conn, params=(nsb_selectionne,)
        ).iloc[0]

    with st.form(f"form_anomalie_{nsb_selectionne}"):
        st.write("Modifier les valeurs anormales :")

        corrections = {}
        for col in colonnes_anormales:
            if col in ligne_complete.index:
                val_actuelle = ligne_complete[col]
                nouvelle_val = st.number_input(f"{col} (valeur actuelle : {val_actuelle})", value=val_actuelle, step=0.1)
                corrections[col] = nouvelle_val

        submit = st.form_submit_button("✅ Appliquer les corrections")

        if submit and corrections:
            try:
                with sqlite3.connect(db_path) as conn:
                    for col, val in corrections.items():
                        conn.execute(
                            f"UPDATE {table_name} SET {col} = ? WHERE numeroNSB = ?", (val, nsb_selectionne)
                        )
                    conn.commit()

                st.success("✅ Correction enregistrée avec succès.")

                # Recharger ligne mise à jour
                with sqlite3.connect(db_path) as conn:
                    ligne_modifiee = pd.read_sql_query(
                        f"SELECT * FROM {table_name} WHERE numeroNSB = ?", conn, params=(nsb_selectionne,)
                    )

                def highlight_changes(valeur, col):
                    return "background-color: lightgreen" if col in corrections else ""

                st.write("🧾 **Ligne mise à jour :**")
                styled = ligne_modifiee.style.apply(
                    lambda row: [highlight_changes(row[col], col) for col in ligne_modifiee.columns],
                    axis=1
                )
                st.dataframe(styled)

            except Exception as e:
                st.error(f"Erreur lors de la mise à jour : {e}")
