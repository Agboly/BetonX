import pandas as pd
import sqlite3
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

# 1. Chargement des données
def charger_donnees(db_path="dataBeton.db", table="NSB_Liste_273983CC"):
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
    return df

# 2. Préparation des données
def preparer_donnees(df):
    df = df.copy()
    colonnes_resistance = ["jour_1", "jour_3", "jour_7", "jour_28", "jour_56"]
    colonnes_features = ["slump", "volume", "temperature"]

    # Drop NA
    df = df.dropna(subset=colonnes_resistance + colonnes_features)

    X = df[colonnes_features]
    Y = df[colonnes_resistance]
    return X, Y

# 3. Entraînement du modèle
def entrainer_model(X, Y):
    base_model = RandomForestRegressor(n_estimators=100, random_state=42)
    model = MultiOutputRegressor(base_model)
    model.fit(X, Y)
    return model

# 4. Sauvegarde du modèle
def sauvegarder_modele(model, chemin="model/modele_multi_resistance.pkl"):
    joblib.dump(model, chemin)

# 5. Évaluation rapide (optionnel)
def evaluer(model, X_test, Y_test):
    Y_pred = model.predict(X_test)
    print("MAE :", mean_absolute_error(Y_test, Y_pred))
    print("R2 :", r2_score(Y_test, Y_pred))

# Script principal
if __name__ == "__main__":
    df = charger_donnees()
    X, Y = preparer_donnees(df)

    # Split pour évaluation rapide
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

    modele = entrainer_model(X_train, Y_train)
    evaluer(modele, X_test, Y_test)
    sauvegarder_modele(modele)
    print("✅ Modèle entraîné et sauvegardé avec succès.")
