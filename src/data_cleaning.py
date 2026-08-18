"""
PASO 2: Limpieza de datos
===========================

¿Qué hace este script?
Toma el CSV crudo de data/raw/ y lo deja "prolijo" en data/processed/:
- Renombra columnas a nombres simples y consistentes
- Convierte fechas y números al tipo de dato correcto
- Filtra por la cuenca Neuquina (donde está Vaca Muerta)
- Elimina filas con datos faltantes clave o duplicadas

¿Por qué es un paso separado de la ingestión?
Porque separar "bajar datos" de "limpiar datos" hace que el código sea más fácil
de debuggear: si algo sale mal limpiando, no hace falta volver a descargar nada.

Cómo correrlo:
    python src/data_cleaning.py
"""

from pathlib import Path

import pandas as pd

RAW_FILE = Path(__file__).resolve().parent.parent / "data" / "raw" / "produccion_pozos.csv"
PROCESSED_FILE = Path(__file__).resolve().parent.parent / "data" / "processed" / "produccion_limpia.csv"

# Nombres reales de las columnas del dataset "Producción de Pozos No Convencional"
COLUMNAS_RENOMBRAR = {
    "anio": "anio",
    "mes": "mes",
    "cuenca": "cuenca",
    "provincia": "provincia",
    "areayacimiento": "yacimiento",
    "empresa": "operadora",
    "idpozo": "pozo_id",
    "sigla": "pozo_nombre",
    "prod_pet": "petroleo_m3",
    "prod_gas": "gas_miles_m3",
    "prod_agua": "agua_m3",
    "fecha_data": "fecha",
}


def cargar_datos_crudos(path: Path) -> pd.DataFrame:
    """Lee el CSV crudo tal cual viene."""
    df = pd.read_csv(path, sep=None, engine="python")
    print(f"Datos crudos cargados: {len(df):,} filas")
    return df


def limpiar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica todos los pasos de limpieza en orden.

    Nota para principiantes: en pandas es común encadenar transformaciones,
    pero acá las separamos en pasos chiquitos para que sea fácil de leer y debuggear.
    """
    # 1. Renombrar columnas a nombres simples (ajustar según columnas reales)
    df = df.rename(columns=COLUMNAS_RENOMBRAR)

    # 2. Sacar espacios en blanco de más en texto (un problema MUY común en datos públicos)
    columnas_texto = df.select_dtypes(include=["object", "string"]).columns
    for col in columnas_texto:
        df[col] = df[col].astype(str).str.strip()

    # 3. Filtrar solo la cuenca Neuquina (ahí está Vaca Muerta)
    if "cuenca" in df.columns:
        antes = len(df)
        df = df[df["cuenca"].str.contains("Neuquina", case=False, na=False)]
        print(f"Filtro por cuenca Neuquina: {antes:,} -> {len(df):,} filas")

    # 4. Convertir la columna de fecha (ya viene armada en el dataset) al tipo datetime real
    #    Antes de esto, pandas la trata como texto, y no podemos ordenarla ni graficarla bien
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    # 5. Asegurar que las columnas numéricas sean números (a veces vienen como texto)
    columnas_numericas = ["petroleo_m3", "gas_miles_m3", "agua_m3"]
    for col in columnas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 6. Eliminar filas sin pozo identificado o sin fecha (no sirven para el análisis)
    columnas_clave = [c for c in ["pozo_id", "fecha"] if c in df.columns]
    if columnas_clave:
        antes = len(df)
        df = df.dropna(subset=columnas_clave)
        print(f"Filas sin datos clave eliminadas: {antes:,} -> {len(df):,} filas")

    # 7. Eliminar duplicados exactos
    antes = len(df)
    df = df.drop_duplicates()
    print(f"Duplicados eliminados: {antes:,} -> {len(df):,} filas")

    return df


def guardar_datos_limpios(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"\nDatos limpios guardados en: {path}")


if __name__ == "__main__":
    df_crudo = cargar_datos_crudos(RAW_FILE)
    df_limpio = limpiar_datos(df_crudo)
    guardar_datos_limpios(df_limpio, PROCESSED_FILE)
