import requests
import sqlite3

# === 1. Requête API
url = "https://all-data-apims.azure-api.net/qc/v2/rows"
params = {
    "table": "NSB_Liste_273983CC"
}
headers = {
    "Ocp-Apim-Subscription-Key": "1400728e1a594a2fa5717600b738c722",
    "X-FACET-QC-D8": "abdj"
}

response = requests.get(url, params=params, headers=headers)
data = response.json()

# === 2. Vérifier que c'est une liste de dictionnaires
if not isinstance(data, list) or len(data) == 0:
    raise ValueError("Le format des données n'est pas une liste valide.")

# === 3. Extraire les colonnes à partir du premier élément
columns = list(data[0].keys())

# Supprimer 'id' si déjà présent pour éviter conflit avec PRIMARY KEY
if "id" in columns:
    columns.remove("id")

table_name = "NSB_Liste_273983CC"

# Connexion SQLite
conn = sqlite3.connect("dataBeton.db")
cursor = conn.cursor()

# Suppression éventuelle de la table existante
cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

# Création dynamique de la table
columns_sql = ", ".join([f'"{col}" TEXT' for col in columns])

create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    {columns_sql}
)
"""
cursor.execute(create_table_sql)

# Insertion
placeholders = ", ".join(["?"] * len(columns))
insert_sql = f"""
INSERT INTO {table_name} ({", ".join(columns)})
VALUES ({placeholders})
"""

for row in data:
    values = [str(row.get(col, "")) for col in columns]
    cursor.execute(insert_sql, values)

conn.commit()
conn.close()

print(f"✅ {len(data)} lignes insérées dans la table '{table_name}'.")
