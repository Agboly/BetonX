import streamlit as st
import sqlite3
import pandas as pd

def afficher_tables_sqlite(db_path="dataBeton.db"):
    st.title("📊 Visualisation des données SQLite")

    # 🔹 Étape 0 : Spécifications des colonnes
    colonnes_a_afficher = {
        "numeroNSB": {"type": "str"},
        "ouvrage_POA": {"type": "str"},
        "formule": {"type": "str"},
        "datedeproduction": {"type": "date", "format": "%d/%m/%Y"},
        "volume": {"type": "float"},
        "slump": {"type": "float"},
        "temperature": {"type": "float"},
        "jour_1": {"type": "float"},
        "jour_3": {"type": "float"},
        "jour_7": {"type": "float"},
        "jour_28": {"type": "float"},
        "jour_56": {"type": "float"}
    }

    # 🔹 Connexion à la base
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 🔹 Liste des tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    if not tables:
        st.warning("❌ Aucune table trouvée dans la base de données.")
        return

    table_name = st.selectbox("Sélectionner une table à afficher :", tables)
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    conn.close()

    # 🔹 Étape 1 : Ne garder que les colonnes utiles si elles existent
    colonnes_presentes = [col for col in colonnes_a_afficher if col in df.columns]
    df = df[colonnes_presentes].copy()

    # 🔹 Étape 2 : Nettoyage des données
    if "formule" in df.columns:
        df["formule"] = df["formule"].astype(str).str.strip()
        df = df[
            (df["formule"].notnull()) &
            (df["formule"] != "") &
            (df["formule"].str.lower() != "none")
        ]


    # 🔹 Affichage final
    st.markdown(f"### 📁 Table : `{table_name}` – {len(df)} lignes")
    st.dataframe(df, use_container_width=True)

    # 🔹 Téléchargement
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Télécharger en CSV",
        csv,
        f"{table_name}_nettoyee.csv",
        "text/csv",
        key="download-csv"
    )
