"""
Dashboard interactivo con Flet
=================================

¿Qué es Flet? Un framework de Python para armar apps con interfaz gráfica
(como los que ya veniste usando en tu dashboard de Presupuesto Abierto).

¿Qué muestra este dashboard?
- Un selector con los pozos reales del dataset
- Un gráfico con la evolución de producción del pozo elegido (se regenera
    cada vez que cambiás de pozo — por eso es "interactivo")
- El texto del reporte generado por IA (Claude u OpenAI, el que hayas corrido)

Cómo correrlo:
    python dashboard/app.py
"""

import flet as ft
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # backend sin ventana propia: matplotlib solo genera la imagen, no la muestra él mismo
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_FILE = BASE_DIR / "data" / "processed" / "produccion_limpia.csv"
REPORTE_FILE = BASE_DIR / "reports" / "reporte_ejecutivo.md"

GRAFICOS_DIR = BASE_DIR / "dashboard" / "graficos_temp"
GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)


def path_grafico_pozo(pozo_id) -> Path:
    """Devuelve el path del archivo de imagen correspondiente a un pozo puntual."""
    return GRAFICOS_DIR / f"grafico_pozo_{pozo_id}.png"


def generar_grafico_pozo(df: pd.DataFrame, pozo_id) -> None:
    """
    PARTE 3: genera el gráfico de producción de UN pozo y lo guarda como imagen.
    """
    datos_pozo = df[df["pozo_id"] == pozo_id].sort_values("fecha")

    plt.figure(figsize=(8, 4))
    plt.plot(datos_pozo["fecha"], datos_pozo["petroleo_m3"], marker="o", markersize=3)
    plt.title(f"Producción de petróleo - Pozo {pozo_id}")
    plt.xlabel("Fecha")
    plt.ylabel("Petróleo (m3)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(path_grafico_pozo(pozo_id))
    plt.close()


def main(page: ft.Page):
    page.title = "Vaca Muerta Analytics"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # --- Encabezado ---
    titulo = ft.Text(
        "🛢️ Vaca Muerta Analytics",
        size=28,
        weight=ft.FontWeight.BOLD,
    )
    subtitulo = ft.Text(
        "Análisis y predicción de producción de pozos no convencionales",
        size=14,
        color=ft.Colors.GREY_700,
    )

    if not PROCESSED_FILE.exists():
        page.add(
            titulo,
            ft.Text(
                "⚠️ No se encontró data/processed/produccion_limpia.csv. "
                "Corré primero: python src/data_cleaning.py",
                color=ft.Colors.RED,
            ),
        )
        return

    df = pd.read_csv(PROCESSED_FILE, parse_dates=["fecha"])

    pozos_con_mas_historia = (
        df["pozo_id"].value_counts().head(50).index.tolist()
    )

    # --- Zona donde va el gráfico ---
    imagen_grafico = ft.Image(
        src=None,
        width=700,
        height=350,
        fit=ft.BoxFit.CONTAIN,
    )

    zona_grafico = ft.Container(
        content=imagen_grafico,
        bgcolor=ft.Colors.GREY_100,
        border_radius=10,
        padding=10,
        alignment=ft.Alignment.CENTER,
    )

    texto_estado = ft.Text("Elegí un pozo para ver su gráfico de producción", italic=True)

    def actualizar_grafico(e):
        pozo_elegido = selector_pozo.value
        if not pozo_elegido:
            return

        texto_estado.value = f"Generando gráfico del pozo {pozo_elegido}..."
        page.update()

        generar_grafico_pozo(df, int(pozo_elegido))

        imagen_grafico.src = str(path_grafico_pozo(int(pozo_elegido)))
        imagen_grafico.update()

        texto_estado.value = f"Mostrando producción del pozo {pozo_elegido}"
        page.update()

    selector_pozo = ft.Dropdown(
        label="Elegí un pozo",
        options=[ft.DropdownOption(str(p)) for p in pozos_con_mas_historia],
        width=300,
        on_select=actualizar_grafico,
    )

    # --- Zona del reporte generado por IA ---
    # CAMBIO: Si existe el archivo .md, renderizamos con ft.Markdown en lugar de ft.Text
    if REPORTE_FILE.exists():
        texto_reporte = REPORTE_FILE.read_text(encoding="utf-8")
        contenido_reporte = ft.Markdown(
            value=texto_reporte,
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        )
    else:
        contenido_reporte = ft.Text(
            "Todavía no se generó ningún reporte. Corré src/claude_insights.py o src/openai_insights.py primero.",
            size=14
        )

    zona_reporte = ft.Container(
        content=ft.Column([
            ft.Text("📄 Reporte ejecutivo", size=18, weight=ft.FontWeight.BOLD),
            contenido_reporte,  # Usamos el control adaptado
        ]),
        bgcolor=ft.Colors.BLUE_50,
        border_radius=10,
        padding=20,
    )

    page.add(
        titulo,
        subtitulo,
        ft.Divider(),
        selector_pozo,
        texto_estado,
        zona_grafico,
        zona_reporte,
    )

    if pozos_con_mas_historia:
        selector_pozo.value = str(pozos_con_mas_historia[0])
        actualizar_grafico(None)


if __name__ == "__main__":
    ft.run(main)
