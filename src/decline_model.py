"""
PASO 4: Modelo de curva de declinación (Arps)
================================================

¿Qué es una curva de declinación?
Cuando un pozo empieza a producir, lo hace a un ritmo alto que va bajando con
el tiempo. El modelo de Arps (1945) es el más usado en la industria petrolera
para describir matemáticamente esa caída. No es "Machine Learning" en el sentido
moderno, pero es el punto de partida clásico, y entenderlo te va a servir para
apreciar por qué el ML puede mejorar la predicción después.

La fórmula (versión hiperbólica) es:

    q(t) = qi / (1 + b * Di * t) ** (1 / b)

Donde:
    q(t) = producción (caudal) en el tiempo t
    qi   = producción inicial (al tiempo t=0)
    Di   = tasa de declinación inicial
    b    = factor de forma de la curva (entre 0 y 1 típicamente para no convencional)

No hace falta entender la fórmula de memoria: lo importante es que scipy nos
ayuda a "encontrarle" los valores de qi, Di y b que mejor se ajustan a los datos
reales de un pozo. Eso se llama "curve fitting".

Cómo correrlo:
    python src/decline_model.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit

PROCESSED_FILE = Path(__file__).resolve().parent.parent / "data" / "processed" / "produccion_limpia.csv"
REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


def arps_hiperbolica(t, qi, di, b):
    """
    La función matemática de Arps. curve_fit va a probar distintos valores
    de qi, di y b hasta encontrar los que mejor se ajusten a los datos reales.
    """
    return qi / (1 + b * di * t) ** (1 / b)


def ajustar_curva_pozo(df: pd.DataFrame, pozo_id: str):
    """
    Toma el historial de producción de UN pozo y le ajusta una curva de Arps.

    Devuelve los parámetros encontrados (qi, di, b) y los datos usados,
    para poder graficarlos después.
    """
    datos_pozo = df[df["pozo_id"] == pozo_id].sort_values("fecha")

    # Creamos una columna "meses desde el inicio" (t=0, 1, 2, 3...)
    datos_pozo = datos_pozo.assign(
        t=range(len(datos_pozo))
    )

    t = datos_pozo["t"].values
    q = datos_pozo["petroleo_m3"].values

    # Valores iniciales "de arranque" para que el algoritmo tenga por dónde empezar
    # (no tienen que ser exactos, curve_fit los va ajustando)
    p0 = [q[0] if len(q) > 0 else 100, 0.1, 0.5]

    try:
        parametros, _ = curve_fit(arps_hiperbolica, t, q, p0=p0, maxfev=5000)
        qi, di, b = parametros
        print(f"Pozo {pozo_id}: qi={qi:.1f}, Di={di:.4f}, b={b:.3f}")
        return qi, di, b, datos_pozo
    except RuntimeError:
        print(f"No se pudo ajustar una curva para el pozo {pozo_id} (datos insuficientes o muy ruidosos)")
        return None


def graficar_ajuste(pozo_id: str, qi: float, di: float, b: float, datos_pozo: pd.DataFrame) -> None:
    """Grafica los datos reales vs la curva ajustada, para ver visualmente qué tan bien encaja."""
    t = datos_pozo["t"].values
    q_real = datos_pozo["petroleo_m3"].values
    q_predicho = arps_hiperbolica(t, qi, di, b)

    plt.figure(figsize=(10, 5))
    plt.scatter(t, q_real, label="Producción real", alpha=0.7)
    plt.plot(t, q_predicho, color="red", label="Curva de Arps ajustada")
    plt.title(f"Curva de declinación - Pozo {pozo_id}")
    plt.xlabel("Meses desde el inicio de producción")
    plt.ylabel("Petróleo (m3)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / f"declinacion_{pozo_id}.png")
    plt.close()
    print(f"Gráfico guardado: declinacion_{pozo_id}.png")


if __name__ == "__main__":
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(PROCESSED_FILE, parse_dates=["fecha"])

    # TODO: elegir un pozo real del dataset para probar (uno con varios meses de historia)
    pozo_ejemplo = df["pozo_id"].value_counts().index[0]  # el pozo con más registros

    resultado = ajustar_curva_pozo(df, pozo_ejemplo)
    if resultado:
        qi, di, b, datos_pozo = resultado
        graficar_ajuste(pozo_ejemplo, qi, di, b, datos_pozo)
