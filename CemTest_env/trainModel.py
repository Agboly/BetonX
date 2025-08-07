import pandas as pd
import sqlite3
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os

# 1. Chargement des données
def charger_donnees(db_path="dataBeton.db", table="NSB_Liste_273983CC"):
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
    return df

# 2. Préparation des données
def preparer_donnees(df):
    df = df.copy()
    colonnes_resistance = ["jour_1", "jour_3", "jour_7", "jour_28", "jour_56"]
    colonnes_features = ["slump", "temperature", "formule"]

    print("🧪 Colonnes du DataFrame :", df.columns.tolist())
    print("🔢 Forme initiale du DataFrame :", df.shape)

    # Remplacer les virgules et convertir en float pour les colonnes numériques
    for col in colonnes_resistance + ["slump", "temperature"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')

    # Supprimer les lignes avec des valeurs manquantes dans les colonnes clés
    df = df.dropna(subset=colonnes_resistance + colonnes_features)
    print("✅ Après suppression des valeurs manquantes :", df.shape)

    # Encodage one-hot de la colonne "formule"
    df = pd.get_dummies(df, columns=["formule"], drop_first=True)

    # Sélection des colonnes explicatives
    X = df[[col for col in df.columns if col.startswith("slump") or col.startswith("temperature") or col.startswith("formule_")]]
    Y = df[colonnes_resistance]

    print("📊 Exemple de features (X) :")
    print(X.head())
    print("🎯 Exemple des cibles (Y) :")
    print(Y.head())

    return X, Y

# 3. Entraînement du modèle
def entrainer_model(X, Y):
    base_model = RandomForestRegressor(n_estimators=100, random_state=42)
    model = MultiOutputRegressor(base_model)
    model.fit(X, Y)
    return model

# 4. Évaluation détaillée
def evaluer(model, X_test, Y_test):
    Y_pred = model.predict(X_test)
    mae_scores = mean_absolute_error(Y_test, Y_pred, multioutput='raw_values')
    r2_scores = r2_score(Y_test, Y_pred, multioutput='raw_values')
    for i, col in enumerate(Y_test.columns):
        print(f"{col} - MAE: {mae_scores[i]:.3f}, R2: {r2_scores[i]:.3f}")

# 5. Sauvegarde du modèle
def sauvegarder_modele(model, chemin="model/modele_multi_resistance.pkl"):
    dossier = os.path.dirname(chemin)
    if not os.path.exists(dossier):
        os.makedirs(dossier)
    print("💾 Sauvegarde du modèle...")
    joblib.dump(model, chemin)

# 6. Script principal
if __name__ == "__main__":
    print("📥 Chargement des données...")
    df = charger_donnees()
    
    print("🧹 Préparation des données...")
    X, Y = preparer_donnees(df)

    print(f"📦 Nombre d’échantillons : {len(X)}")
    if len(X) == 0:
        print("❌ Aucune donnée exploitable pour l'entraînement. Vérifie les colonnes et les valeurs manquantes.")
        exit()

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

    print("🧠 Entraînement du modèle...")
    modele = entrainer_model(X_train, Y_train)

    print("📈 Évaluation du modèle :")
    evaluer(modele, X_test, Y_test)

    print("💾 Sauvegarde du modèle...")
    sauvegarder_modele(modele)

    print("✅ Modèle entraîné et sauvegardé avec succès.")
