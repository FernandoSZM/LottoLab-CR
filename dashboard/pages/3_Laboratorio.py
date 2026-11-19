
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from components.charts import grafico_frecuencias
from services.database import cargar_sorteos


RAIZ_PROYECTO = Path(__file__).resolve().parents[2]

ARCHIVO_COMPARACION = (
    RAIZ_PROYECTO
    / "results"
    / "comparacion_modelos.csv"
)


st.set_page_config(
    page_title="Laboratorio | LottoLab CR",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 Laboratorio")
st.caption(
    "Análisis estadístico y evaluación experimental "
    "de Nuevos Tiempos — Costa Rica"
)


@st.cache_data
def cargar_comparacion(ruta, fecha_modificacion):
    return pd.read_csv(ruta)


try:
    df = cargar_sorteos()
except Exception as error:
    st.error("No se pudo conectar con PostgreSQL.")
    st.exception(error)
    st.stop()

if df.empty:
    st.warning("No hay sorteos disponibles.")
    st.stop()


tab_estadistica, tab_modelos = st.tabs(
    [
        "📊 Análisis estadístico",
        "🧠 Modelos predictivos",
    ]
)


# ==================================================
# PESTAÑA 1 — ANÁLISIS ESTADÍSTICO
# ==================================================

with tab_estadistica:

    anio_minimo = int(df["anio"].min())
    anio_maximo = int(df["anio"].max())

    rango_anios = st.slider(
        "Período de análisis",
        min_value=anio_minimo,
        max_value=anio_maximo,
        value=(anio_minimo, anio_maximo),
        step=1,
    )

    df_filtrado = df[
        df["anio"].between(
            rango_anios[0],
            rango_anios[1],
        )
    ].copy()

    if df_filtrado.empty:
        st.info("No hay sorteos en el período seleccionado.")
    else:
        total = len(df_filtrado)
        numeros_unicos = df_filtrado["numero"].nunique()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Sorteos analizados",
            f"{total:,}",
        )
        col2.metric(
            "Números distintos",
            numeros_unicos,
        )
        col3.metric(
            "Período",
            (
                f"{df_filtrado['anio'].min()}"
                f"–{df_filtrado['anio'].max()}"
            ),
        )

        st.divider()
        st.subheader("Frecuencia de números ganadores")

        numeros = [
            f"{n:02d}"
            for n in range(100)
        ]

        frecuencias = (
            df_filtrado["numero"]
            .value_counts()
            .reindex(numeros, fill_value=0)
            .rename_axis("Número")
            .reset_index(name="Apariciones")
        )

        vista_frecuencias = st.segmented_control(
            "Visualización",
            options=[
                "Todos",
                "10 más frecuentes",
                "10 menos frecuentes",
            ],
            default="Todos",
        )

        fig = grafico_frecuencias(
            frecuencias=frecuencias,
            total_sorteos=total,
            vista=vista_frecuencias,
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

        col_izq, col_der = st.columns(2)

        with col_izq:
            st.subheader("10 más frecuentes")
            st.dataframe(
                frecuencias.nlargest(
                    10,
                    "Apariciones",
                ),
                hide_index=True,
                width="stretch",
            )

        with col_der:
            st.subheader("10 menos frecuentes")
            st.dataframe(
                frecuencias.nsmallest(
                    10,
                    "Apariciones",
                ),
                hide_index=True,
                width="stretch",
            )

        st.divider()
        st.subheader("Sorteos por año")

        sorteos_anuales = (
            df_filtrado.groupby("anio")
            .size()
            .reset_index(name="Sorteos")
        )

        fig_anual = px.bar(
            sorteos_anuales,
            x="anio",
            y="Sorteos",
            labels={"anio": "Año"},
        )

        fig_anual.update_xaxes(
            type="category"
        )

        st.plotly_chart(
            fig_anual,
            width="stretch",
        )

        st.subheader("Explorador de registros")

        st.dataframe(
            df_filtrado.sort_values(
                ["fecha", "hora", "sorteo"],
                ascending=False,
            ),
            hide_index=True,
            width="stretch",
        )


# ==================================================
# PESTAÑA 2 — MODELOS PREDICTIVOS
# ==================================================

with tab_modelos:

    st.subheader("Comparación de modelos")

    st.write(
        "Evaluamos distintas estrategias para estimar "
        "la probabilidad de los números del 00 al 99."
    )

    if not ARCHIVO_COMPARACION.exists():

        st.warning(
            "Todavía no hay resultados guardados "
            "de la comparación de modelos."
        )

        st.code(
            "PYTHONPATH=.:dashboard "
            "python -m scripts.generar_comparacion",
            language="bash",
        )

    else:

        try:
            resultados = cargar_comparacion(
                str(ARCHIVO_COMPARACION),
                ARCHIVO_COMPARACION.stat().st_mtime_ns,
            )
        except Exception as error:
            st.error(
                "No se pudo leer el archivo de resultados."
            )
            st.exception(error)
            st.stop()

        columnas_requeridas = {
            "modelo",
            "log_loss",
            "top_5",
            "aciertos_top_5",
            "empates_top_5",
            "top_5_sin_empates",
            "probabilidad_maxima",
            "sorteos",
        }

        if not columnas_requeridas.issubset(
            resultados.columns
        ):
            st.error(
                "El archivo de resultados no tiene "
                "todas las columnas esperadas."
            )
            st.stop()

        mejor_modelo = resultados.loc[
            resultados["log_loss"].idxmin()
        ]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Modelos evaluados",
            len(resultados),
        )

        col2.metric(
            "Sorteos de validación",
            f"{int(mejor_modelo['sorteos']):,}",
        )

        col3.metric(
            "Menor log loss",
            f"{mejor_modelo['log_loss']:.4f}",
        )

        st.divider()

        st.subheader("Resultados comparativos")

        tabla = resultados[
            [
                "modelo",
                "log_loss",
                "top_5_sin_empates",
                "empates_top_5",
                "probabilidad_maxima",
            ]
        ].copy()

        tabla.columns = [
            "Modelo",
            "Log loss",
            "Top 5 sin empates (%)",
            "Sorteos con empate",
            "Probabilidad máxima (%)",
        ]

        st.dataframe(
            tabla,
            hide_index=True,
            width="stretch",
            column_config={
                "Log loss": st.column_config.NumberColumn(
                    format="%.4f",
                ),
                "Top 5 sin empates (%)": (
                    st.column_config.NumberColumn(
                        format="%.2f %%",
                    )
                ),
                "Probabilidad máxima (%)": (
                    st.column_config.NumberColumn(
                        format="%.2f %%",
                    )
                ),
            },
        )

        st.caption(
            "Un Top 5 sin empates no está definido "
            "cuando varios números comparten la "
            "probabilidad del quinto puesto."
        )

        st.divider()

        st.subheader("Calidad de las probabilidades")

        figura_logloss = px.bar(
            resultados,
            x="modelo",
            y="log_loss",
            color="modelo",
            text="log_loss",
            labels={
                "modelo": "Modelo",
                "log_loss": "Log loss",
            },
        )

        figura_logloss.update_traces(
            texttemplate="%{text:.4f}",
            textposition="outside",
        )

        figura_logloss.update_layout(
            showlegend=False,
            yaxis_range=[
                0,
                max(resultados["log_loss"]) * 1.15,
            ],
        )

        st.plotly_chart(
            figura_logloss,
            width="stretch",
        )

        st.info(
            "**¿Cómo interpretar el log loss?** "
            "Cuanto menor sea, mejor es la calidad "
            "de las probabilidades asignadas a los "
            "resultados reales. "
            "Una distribución uniforme sobre "
            "100 números obtiene aproximadamente "
            "4.6052."
        )

        st.divider()

        st.subheader("Interpretación del experimento")

        if mejor_modelo["modelo"] == "Uniforme":

            st.warning(
                "En esta validación, ninguno de los "
                "modelos experimentales superó al "
                "modelo uniforme en log loss. "
                "No encontramos evidencia de una "
                "ventaja predictiva con estos métodos."
            )

        else:

            st.info(
                f"El menor log loss observado fue el "
                f"del modelo {mejor_modelo['modelo']}. "
                "Este resultado exploratorio no "
                "demuestra una ventaja predictiva "
                "estable ni garantiza aciertos futuros."
            )

        if (
            "fecha_generacion_utc"
            in resultados.columns
        ):
            st.caption(
                "Experimento generado (UTC): "
                f"{resultados['fecha_generacion_utc'].iloc[0]}"
            )

        st.caption(
            "Las métricas corresponden a una "
            "validación histórica interna. "
            "No son pronósticos de sorteos futuros."
        )
