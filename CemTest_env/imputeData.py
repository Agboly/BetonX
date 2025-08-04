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
        return

    nsb_selectionne = st.selectbox("Sélectionnez un `numeroNSB` à corriger :", lignes_na["numeroNSB"].unique())
    ligne_cible = lignes_na[lignes_na["numeroNSB"] == nsb_selectionne].iloc[0]

    with st.form(f"form_correction_{nsb_selectionne}"):
        st.write("Modifier les valeurs manquantes :")

        corrections = {}
        colonnes_modifiables = ["volume", "slump", "temperature", "jour_1", "jour_3", "jour_7", "jour_28", "jour_56"]

        for col in colonnes_modifiables:
            if col in ligne_cible.index and pd.isnull(ligne_cible[col]):
                nouvelle_val = st.number_input(f"{col} (actuellement manquant)", value=0.0, step=0.1)
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
                st.success("✅ Correction enregistrée.")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")
