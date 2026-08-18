"""
PASO 6: Reportes en lenguaje natural con la API de OpenAI
=============================================================
¿Qué hace este script?
Toma los NÚMEROS que ya calculamos (top operadoras, tendencia de producción,
resultado del modelo de ML) y le pide a un modelo de OpenAI que redacte un
resumen ejecutivo, como si fuera un analista senior explicándoselo a un gerente
sin conocimientos técnicos.

¿Por qué esto es valioso?
En proyectos reales, los datos y los modelos son solo la mitad del trabajo — la
otra mitad es comunicar los hallazgos de forma clara. Usar un LLM para automatizar
esa redacción es una skill muy pedida hoy en día.

Antes de correr esto:
1. Necesitás una cuenta de OpenAI con API key: https://platform.openai.com/api-keys
2. Copiá .env.example como .env y pegá tu clave ahí (OPENAI_API_KEY=...)
3. Instalá las dependencias: pip install -r requirements.txt

Cómo correrlo:
    python src/openai_insights.py
"""

import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Cargamos las variables de entorno del archivo .env (ahí vive nuestra API key)
load_dotenv()

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def generar_reporte(resumen_datos: dict) -> str:
    """
    Le pasa a OpenAI un resumen de los datos y le pide que redacte un reporte.

    Parámetros:
        resumen_datos: un diccionario con los números clave del análisis,
                        por ejemplo:
                        {
                            "operadora_lider": "YPF",
                            "produccion_total_petroleo_m3": 1500000,
                            "tendencia": "creciente",
                            "mae_modelo_ml": 320.5,
                        }
    """
    # Obtenemos la fecha actual en formato día/mes/año (ej: 14/08/2026)
    fecha_actual = datetime.now().strftime("%d/%m/%Y")

    # Convertimos el diccionario a un texto legible para incluir en el prompt
    datos_como_texto = "\n".join(f"- {clave}: {valor}" for clave, valor in resumen_datos.items())

    # Se solicita explícitamente el uso de formato Markdown
    prompt = f"""Fecha del reporte: {fecha_actual}

Sos un analista de datos de la industria de petróleo y gas en Argentina.

Te paso un resumen de un análisis de producción de Vaca Muerta:

{datos_como_texto}

Redactá un reporte ejecutivo breve (máximo 200 palabras) en español, para un público general que NO es técnico. 
Formateá la respuesta en Markdown (usá encabezados #, negritas **palabra** y viñetas para que quede bien estructurado).

Requisitos clave:
1. Incluí un título principal y la fecha actual ({fecha_actual}) al inicio.
2. Explicá qué significan estos números en términos de negocio, sin usar jerga técnica innecesaria.
3. Terminá con una recomendación concreta. 
4. Mencioná al final que este proyecto fue hecho por Cristian Contreras y Adela Cervantes Ortiz.
"""

    respuesta = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=500,
        messages=[
            {"role": "system", "content": f"Sos un analista de datos senior de la industria de petróleo y gas. Hoy es {fecha_actual}."},
            {"role": "user", "content": prompt},
        ],
    )

    texto_reporte = respuesta.choices[0].message.content

    return texto_reporte


if __name__ == "__main__":
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # TODO: reemplazar estos valores de ejemplo por los resultados reales
    # que salen de eda.py, decline_model.py y ml_model.py
    resumen_ejemplo = {
        "operadora_lider": "YPF",
        "produccion_total_petroleo_m3": 1_500_000,
        "tendencia_ultimos_12_meses": "creciente (+18%)",
        "error_promedio_modelo_ml_m3": 320.5,
    }

    reporte = generar_reporte(resumen_ejemplo)

    print("\n--- Reporte generado por OpenAI ---\n")
    print(reporte)

    # CAMBIO: Guardamos el reporte en un archivo Markdown (.md)
    archivo_salida = REPORTS_DIR / "reporte_ejecutivo.md"
    archivo_salida.write_text(reporte, encoding="utf-8")
    print(f"\nReporte guardado en: {archivo_salida}")