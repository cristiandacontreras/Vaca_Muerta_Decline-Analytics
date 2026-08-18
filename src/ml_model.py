"""
PASO 5: Modelo de Machine Learning
=====================================

¿Qué vamos a predecir?
La producción de petróleo del PRÓXIMO mes de un pozo, usando como pistas (features)
datos como: cuántos meses lleva produciendo, su producción de los últimos meses,
la operadora, el yacimiento, etc.

¿Por qué esto y no otra cosa?
Es un problema de regresión clásico (predecir un número, no una categoría) y es
justo el tipo de tarea donde el ML le puede ganar al modelo de Arps: puede aprender
patrones que dependen de varias variables a la vez, no solo del tiempo.

¿Qué algoritmo usamos?
Random Forest: es un buen primer modelo para empezar porque funciona bien "de
fábrica" sin mucho ajuste fino, y es fácil de interpretar (nos dice qué variables
importan más).

Cómo correrlo:
    python src/ml_model.py
"""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

PROCESSED_FILE = Path(__file__).resolve().parent.parent / "data" / "processed" / "produccion_limpia.csv"
MODELS_DIR = Path(__file__).resolve().parent.parent / "reports"


def crear_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye las "pistas" (features) que el modelo va a usar para predecir.

    Idea clave en series temporales: usamos los valores de meses ANTERIORES
    como pistas para predecir el mes SIGUIENTE. Esto se llama "lag features".
    """
    df = df.sort_values(["pozo_id", "fecha"]).copy()

    # Producción de los 1, 2 y 3 meses anteriores del mismo pozo
    for lag in [1, 2, 3]:
        df[f"petroleo_lag_{lag}"] = df.groupby("pozo_id")["petroleo_m3"].shift(lag)

    # Cuántos meses lleva produciendo el pozo (la "edad" del pozo)
    df["edad_pozo_meses"] = df.groupby("pozo_id").cumcount()

    # La variable objetivo: lo que queremos predecir es la producción de ESTE mes
    # (usando como pistas los meses anteriores)
    df["objetivo"] = df["petroleo_m3"]

    # Sacamos las filas donde no hay suficiente historia para calcular los lags
    df = df.dropna(subset=["petroleo_lag_1", "petroleo_lag_2", "petroleo_lag_3"])

    return df


def entrenar_modelo(df: pd.DataFrame):
    """Entrena un Random Forest y evalúa qué tan bien predice en datos que no vio."""
    columnas_features = [
        "petroleo_lag_1", "petroleo_lag_2", "petroleo_lag_3", "edad_pozo_meses"
    ]

    X = df[columnas_features]
    y = df["objetivo"]

    # Separamos en train (para entrenar) y test (para evaluar de forma honesta)
    # shuffle=False porque son series temporales: no queremos mezclar el orden del tiempo
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    modelo = RandomForestRegressor(n_estimators=200, random_state=42)
    modelo.fit(X_train, y_train)

    predicciones = modelo.predict(X_test)

    # Métricas para saber qué tan bueno es el modelo
    mae = mean_absolute_error(y_test, predicciones)
    r2 = r2_score(y_test, predicciones)

    print(f"MAE (error promedio en m3): {mae:.2f}")
    print(f"R² (qué % de la variación explica el modelo): {r2:.3f}")

    # Qué tan importante fue cada feature para el modelo
    importancias = pd.Series(modelo.feature_importances_, index=columnas_features)
    print("\nImportancia de cada variable:")
    print(importancias.sort_values(ascending=False))

    return modelo


if __name__ == "__main__":
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(PROCESSED_FILE, parse_dates=["fecha"])

    df_features = crear_features(df)
    modelo = entrenar_modelo(df_features)

    # Guardamos el modelo entrenado para poder usarlo después sin reentrenar
    joblib.dump(modelo, MODELS_DIR / "modelo_produccion.pkl")
    print(f"\nModelo guardado en: {MODELS_DIR / 'modelo_produccion.pkl'}")
