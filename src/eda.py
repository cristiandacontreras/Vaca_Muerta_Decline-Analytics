"""
PASO 3: Análisis Exploratorio de Datos (EDA)
===============================================

¿Qué es el EDA?
"Exploratory Data Analysis" = mirar los datos con gráficos y estadísticas simples
ANTES de meterte a hacer Machine Learning. Sirve para entender qué hay en los datos,
detectar cosas raras, y decidir qué preguntas vale la pena responder.

¿Qué hace este script?
Genera algunos gráficos clave sobre la producción de Vaca Muerta y los guarda
como imágenes en reports/.

Cómo correrlo:
    python src/eda.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

PROCESSED_FILE = Path(__file__).resolve().parent.parent / "data" / "processed" / "produccion_limpia.csv"
REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"

sns.set_theme(style="whitegrid")  # un estilo de gráficos más prolijo que el default


def produccion_total_por_mes(df: pd.DataFrame) -> None:
    """
    Grafica cómo evolucionó la producción total de petróleo mes a mes.
    Útil para ver la tendencia general: ¿está creciendo Vaca Muerta o no?
    """
    serie = df.groupby("fecha")["petroleo_m3"]

    plt.figure(figsize=(10, 5))
    serie.plot()
    plt.title("Producción total de petróleo por mes - Cuenca Neuquina")
    plt.xlabel("Fecha")
    plt.ylabel("Petróleo (m3)")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "produccion_total_por_mes.png")
    plt.close()
    print("Gráfico guardado: produccion_total_por_mes.png")


def top_operadoras(df: pd.DataFrame, n: int = 10) -> None:
    """
    Muestra qué empresas produjeron más en total.
    Útil como primera pregunta de negocio: ¿quién domina Vaca Muerta?
    """
    ranking = (
        df.groupby("operadora")["petroleo_m3"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
    )

    plt.figure(figsize=(10, 6))
    ranking.plot(kind="barh")
    plt.title(f"Top {n} operadoras por producción total de petróleo")
    plt.xlabel("Petróleo (m3)")
    plt.gca().invert_yaxis()  # para que el #1 quede arriba
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "top_operadoras.png")
    plt.close()
    print("Gráfico guardado: top_operadoras.png")


def distribucion_produccion_por_pozo(df: pd.DataFrame) -> None:
    """
    Muestra cómo se distribuye la producción entre pozos: ¿la mayoría producen
    poco y unos pocos producen mucho? (esto suele pasar mucho en no convencional)
    """
    produccion_por_pozo = df.groupby("pozo_id")["petroleo_m3"].sum()

    plt.figure(figsize=(10, 5))
    sns.histplot(produccion_por_pozo, bins=50, log_scale=(False, True))
    plt.title("Distribución de producción acumulada por pozo")
    plt.xlabel("Petróleo acumulado (m3)")
    plt.ylabel("Cantidad de pozos (escala log)")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "distribucion_por_pozo.png")
    plt.close()
    print("Gráfico guardado: distribucion_por_pozo.png")


if __name__ == "__main__":
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(PROCESSED_FILE, parse_dates=["fecha"])

    produccion_total_por_mes(df)
    top_operadoras(df)
    distribucion_produccion_por_pozo(df)

    print("\nEDA completo. Revisá los gráficos en la carpeta reports/")
