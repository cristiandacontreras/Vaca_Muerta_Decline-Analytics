"""
PASO 1: Ingestión de datos
===========================

¿Qué hace este script?
Descarga el dataset público de "producción de petróleo y gas por pozo" desde
datos.gob.ar y lo guarda tal cual (sin tocar nada) en data/raw/.

¿Por qué guardamos el dato "crudo" sin tocar?
Es buena práctica en ciencia de datos: si algo sale mal en la limpieza, siempre
podés volver a este archivo original y empezar de nuevo, sin tener que descargarlo
otra vez.

Cómo correrlo:
    python src/data_ingestion.py
"""

from pathlib import Path

import pandas as pd
import requests

# Carpeta donde vamos a guardar el archivo descargado
RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUTPUT_FILE = RAW_DATA_DIR / "produccion_pozos.csv"

# URL real del recurso "Producción de Pozos de Gas y Petróleo No Convencional".
# Fuente: https://datos.gob.ar/dataset/produccion-de-petroleo-y-gas-por-pozo
# Ojo: "Capítulo IV - Pozos" (otro recurso del mismo dataset) es el PADRÓN de pozos
# (ubicación, formación, profundidad) pero NO tiene producción mensual - por eso usamos este otro.
# Como Vaca Muerta es no convencional, este archivo ya viene filtrado a lo que nos interesa.
# Ojo: es un archivo grande (años de historia), la descarga puede tardar.
# Nota: el gobierno lo publica en http:// (no https://), es así en origen.
DATASET_URL = "http://datos.energia.gob.ar/dataset/c846e79c-026c-4040-897f-1ad3543b407c/resource/b5b58cdc-9e07-41f9-b392-fb9ec68b0725/download/produccin-de-pozos-de-gas-y-petrleo-no-convencional.csv"


def descargar_dataset(url: str, destino: Path) -> None:
    """
    Descarga un archivo desde una URL y lo guarda en el disco.

    Parámetros:
        url: la dirección de internet de donde bajamos el archivo
        destino: el path (ubicación) donde lo vamos a guardar
    """
    print(f"Descargando datos desde:\n  {url}")

    # requests.get hace la petición HTTP, como cuando el navegador entra a una página
    respuesta = requests.get(url, timeout=60)

    # Si algo salió mal (ej: error 404 o 500), esto tira un error legible
    respuesta.raise_for_status()

    # Nos aseguramos de que la carpeta destino exista antes de guardar
    destino.parent.mkdir(parents=True, exist_ok=True)

    # Guardamos el contenido tal cual vino, en modo binario ("wb" = write binary)
    with open(destino, "wb") as archivo:
        archivo.write(respuesta.content)

    print(f"Listo! Datos guardados en: {destino}")


def verificar_dataset(path: Path) -> None:
    """
    Abre el CSV descargado y muestra un resumen rápido para confirmar
    que la descarga funcionó y que el archivo tiene la pinta esperada.
    """
    df = pd.read_csv(path, sep=None, engine="python")  # sep=None detecta el separador solo (, o ;)
    print("\n--- Vista previa del dataset ---")
    print(f"Filas: {len(df):,} | Columnas: {len(df.columns)}")
    print("\nColumnas encontradas:")
    print(list(df.columns))
    print("\nPrimeras filas:")
    print(df.head())


if __name__ == "__main__":
    descargar_dataset(DATASET_URL, OUTPUT_FILE)
    verificar_dataset(OUTPUT_FILE)
