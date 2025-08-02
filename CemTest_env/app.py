import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Essai Béton", layout="wide")

# Menu simple dans sidebar
page = st.sidebar.selectbox("Navigation", ["Accueil", "Visualisation"])

if page == "Accueil":
    st.title("🧱 Bienvenue sur l'application Essai Béton")
    st.markdown("""
    ## Objectif 🎯
    Cette application permet :
    - de récupérer les données d'essais béton
    - de les stocker dans une base SQLite
    - de visualiser et télécharger les données

    ➡️ Utilisez le menu à gauche pour accéder aux différentes fonctionnalités.
    """)

elif page == "Visualisation":
    st.title("📊 Visualisation des données SQLite")

    # Connexion à la base de données
    db_path = "dataBeton.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Récupérer toutes les tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    if not tables:
        st.warning("❌ Aucune table trouvée dans la base de données.")
    else:
        table_name = st.selectbox("Sélectionner une table à afficher :", tables)
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)

        st.markdown(f"### 📁 Table : `{table_name}` – {len(df)} lignes")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Télécharger en CSV", csv, f"{table_name}.csv", "text/csv", key="download-csv")

    conn.close()
