"""
Tests básicos
===============

¿Para qué sirve esto?
Los tests son pequeños chequeos automáticos que verifican que el código hace
lo que se espera. No hace falta escribir tests súper completos al principio;
alcanza con probar los casos más importantes.

Cómo correrlos:
    pip install pytest
    pytest tests/
"""

import sys
from pathlib import Path

# Agregamos la carpeta src/ al path para poder importar las funciones
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from decline_model import arps_hiperbolica


def test_arps_en_t_cero_devuelve_qi():
    """
    En el tiempo t=0, la producción predicha por Arps debería ser
    exactamente igual a qi (la producción inicial). Es un buen chequeo
    porque si esto falla, algo está mal en la fórmula.
    """
    qi = 100
    di = 0.1
    b = 0.5

    resultado = arps_hiperbolica(0, qi, di, b)

    assert resultado == qi


def test_arps_declina_con_el_tiempo():
    """
    La producción predicha debería ser menor en t=12 que en t=0
    (la curva tiene que "declinar", como su nombre lo indica).
    """
    qi, di, b = 100, 0.1, 0.5

    produccion_inicial = arps_hiperbolica(0, qi, di, b)
    produccion_futura = arps_hiperbolica(12, qi, di, b)

    assert produccion_futura < produccion_inicial
