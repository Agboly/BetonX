
import sqlite3
import pandas as pd
import numpy as np

# Modèles de régression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.linear_model import Ridge, Lasso, LinearRegression
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.multioutput import MultiOutputRegressor

# Évaluation et validation
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import mean_squared_error

# Sauvegarde du modèle
import joblib


# Chemins
DB_PATH = "dataBeton.db"          # adapte selon ton projet
TABLE = "NSB_Liste_273983CC"
MODEL_SAVE_PATH = "model/modele_multi_resistance.pkl"


def charger_donnees():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"""
        SELECT slump, volume, temperature, 
               jour_1, jour_3, jour_7, jour_28, jour_56
        FROM {TABLE}
        WHERE slump IS NOT NULL AND volume IS NOT NULL AND temperature IS NOT NULL
    """, conn)
    conn.close()

    # Nettoyage des valeurs numériques
    colonnes_numeriques = ["slump", "volume", "temperature", "jour_1", "jour_3", "jour_7", "jour_28", "jour_56"]
    for col in colonnes_numeriques:
        df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna()  # optionnel : on enlève les lignes avec NaN
    return df


def preparer_X_y(df):
    X = df[["slump", "volume", "temperature"]].copy()
    y = df[["jour_1", "jour_3", "jour_7", "jour_28", "jour_56"]].copy()
    return X, y

def evaluer_modele(model, X, y):
    # Cross validation (score négatif MSE)
    scores = cross_val_score(model, X, y, cv=5, scoring='neg_mean_squared_error')
    rmse_scores = np.sqrt(-scores)
    print(f"RMSE CV: {rmse_scores.mean():.3f} ± {rmse_scores.std():.3f}")
    return rmse_scores.mean()

def entrainer_et_sauvegarder():
    df = charger_donnees()
    X, y = preparer_X_y(df)

    # Liste des modèles à tester
    modeles = {
    "RandomForest": MultiOutputRegressor(RandomForestRegressor(n_estimators=100, random_state=42)),
    "GradientBoosting": MultiOutputRegressor(GradientBoostingRegressor(n_estimators=100, random_state=42)),
    "LinearRegression": MultiOutputRegressor(LinearRegression()),
    "Ridge": MultiOutputRegressor(Ridge(alpha=1.0)),
    "Lasso": MultiOutputRegressor(Lasso(alpha=0.1)),
    "KNN": MultiOutputRegressor(KNeighborsRegressor(n_neighbors=5)),
    "XGBoost": MultiOutputRegressor(XGBRegressor(n_estimators=100, random_state=42)),
    "LightGBM": MultiOutputRegressor(LGBMRegressor(n_estimators=100, random_state=42))
}


    meilleurs_score = float("inf")
    meilleur_modele = None
    meilleur_nom = ""

    for nom, modele in modeles.items():
        print(f"Évaluation du modèle : {nom}")
        score = evaluer_modele(modele, X, y)
        if score < meilleurs_score:
            meilleurs_score = score
            meilleur_modele = modele
            meilleur_nom = nom

    print(f"Meilleur modèle : {meilleur_nom} avec RMSE = {meilleurs_score:.3f}")

    # Entraîner le meilleur modèle sur tout le jeu
    print("Entraînement final du meilleur modèle sur toutes les données...")
    meilleur_modele.fit(X, y)

    # Sauvegarder le modèle
    joblib.dump(meilleur_modele, MODEL_SAVE_PATH)
    print(f"Modèle sauvegardé dans {MODEL_SAVE_PATH}")

if __name__ == "__main__":
    entrainer_et_sauvegarder()
