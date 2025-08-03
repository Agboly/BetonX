import streamlit as st
import pandas as pd
import sqlite3

import pandas as pd
import sqlite3

def corriger_valeurs_manquantes(db_path, nom_table):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {nom_table}", conn)
    conn.close()

    colonnes_a_corriger = ["slump", "volume", "temperature", "jour_1", "jour_3", "jour_7", "jour_28", "jour_56"]
    lignes_na = df[df[colonnes_a_corriger].isnull().any(axis=1)]

    if lignes_na.empty:
        st.info("🎉 Il n'y a aucune valeur manquante à corriger.")
        return

    # Liste des numeroNSB uniques dans les lignes avec NA
    numero_nsb_list = lignes_na["numeroNSB"].unique()
    selected_nsb = st.selectbox("Choisir un NumeroNSB à corriger :", numero_nsb_list)

    if selected_nsb:
        # Extraire la ligne correspondant au NumeroNSB sélectionné
        ligne_selectionnee = lignes_na[lignes_na["numeroNSB"] == selected_nsb].iloc[0]

        st.write(f"**Formule** : {ligne_selectionnee['formule']}")
        st.write(f"**NumeroNSB** : {selected_nsb}")

        corrections = {}
        for col in colonnes_a_corriger:
            val_actuelle = ligne_selectionnee[col]
            valeur_str = "" if pd.isna(val_actuelle) else str(val_actuelle)
            nouv_val = st.text_input(f"Valeur pour {col} (actuelle : {valeur_str})", value=valeur_str, key=f"{selected_nsb}_{col}")

            try:
                corrections[col] = float(nouv_val) if nouv_val.strip() != "" else None
            except ValueError:
                st.error(f"Valeur invalide pour {col} : {nouv_val}")
                return

        if st.button("Valider la correction"):
            conn = sqlite3.connect(db_path)
            curseur = conn.cursor()

            # Création de la table NSB_Impute si elle n'existe pas
            curseur.execute("""
                CREATE TABLE IF NOT EXISTS NSB_Impute (
                    numeroNSB TEXT PRIMARY KEY,
                    formule TEXT,
                    slump REAL,
                    volume REAL,
                    temperature REAL,
                    jour_1 REAL,
                    jour_3 REAL,
                    jour_7 REAL,
                    jour_28 REAL,
                    jour_56 REAL,
                    date_correction TEXT DEFAULT (datetime('now'))
                )
            """)

            valeurs = (
                selected_nsb,
                ligne_selectionnee['formule'],
                corrections["slump"],
                corrections["volume"],
                corrections["temperature"],
                corrections["jour_1"],
                corrections["jour_3"],
                corrections["jour_7"],
                corrections["jour_28"],
                corrections["jour_56"]
            )

            # Insert ou update avec ON CONFLICT
            curseur.execute("""
                INSERT INTO NSB_Impute (numeroNSB, formule, slump, volume, temperature, jour_1, jour_3, jour_7, jour_28, jour_56)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(numeroNSB) DO UPDATE SET
                    formule=excluded.formule,
                    slump=excluded.slump,
                    volume=excluded.volume,
                    temperature=excluded.temperature,
                    jour_1=excluded.jour_1,
                    jour_3=excluded.jour_3,
                    jour_7=excluded.jour_7,
                    jour_28=excluded.jour_28,
                    jour_56=excluded.jour_56
            """, valeurs)

            conn.commit()
            conn.close()

            st.success("✅ Correction enregistrée avec succès !")
