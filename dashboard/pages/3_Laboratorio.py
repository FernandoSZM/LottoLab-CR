from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[2]
ARCHIVO_COMPARACION = (
    ROOT_DIR / "results" / "comparacion_modelos.csv"
)


st.set_page_config(
    page_title="Laboratorio | LottoLab CR",
    layout="wide",
)

st.title("Laboratorio")
st.caption(
    "Consulta cómo se comportaron los modelos en una validación "
    "histórica, sin confundirla con resultados futuros."
)


@st.cache_data(show_spinner=False)
def cargar_comparacion(ruta, fecha_modificacion):
    if Path(ruta).stat().st_mtime_ns != fecha_modificacion:
        raise RuntimeError(
            "El archivo de validación cambió durante la lectura."
        )
    return pd.read_csv(ruta)


if not ARCHIVO_COMPARACION.exists():
    st.warning(
        "Todavía no hay resultados guardados para comparar los modelos."
    )
    st.code(
        "PYTHONPATH=.:dashboard "
        "python -m scripts.generar_comparacion",
        language="bash",
    )
    st.stop()

try:
    resultados = cargar_comparacion(
        str(ARCHIVO_COMPARACION),
        ARCHIVO_COMPARACION.stat().st_mtime_ns,
    )
except Exception as error:
    st.error("No se pudieron leer los resultados de validación.")
    with st.expander("Detalles técnicos"):
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

if not columnas_requeridas.issubset(resultados.columns):
    st.error(
        "El archivo de validación no contiene todas las columnas esperadas."
    )
    st.stop()

if resultados.empty:
    st.warning("El archivo de validación no contiene resultados.")
    st.stop()

modelo_uniforme = resultados.loc[
    resultados["modelo"] == "Uniforme"
]
mejor_modelo = resultados.loc[
    resultados["log_loss"].idxmin()
]

col_modelos, col_sorteos, col_log_loss = st.columns(3)
col_modelos.metric("Modelos evaluados", len(resultados))
col_sorteos.metric(
    "Sorteos de validación",
    f"{int(mejor_modelo['sorteos']):,}",
)
col_log_loss.metric(
    "Menor log loss",
    f"{mejor_modelo['log_loss']:.4f}",
)

st.subheader("Comparación")
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
        "Log loss": st.column_config.NumberColumn(format="%.4f"),
        "Top 5 sin empates (%)": st.column_config.NumberColumn(
            format="%.2f %%"
        ),
        "Probabilidad máxima (%)": st.column_config.NumberColumn(
            format="%.2f %%"
        ),
    },
)
st.caption(
    "Top 5 sin empates no se define cuando varios números comparten "
    "la probabilidad del quinto puesto."
)

figura_logloss = px.bar(
    resultados,
    x="modelo",
    y="log_loss",
    color="modelo",
    text="log_loss",
    labels={"modelo": "Modelo", "log_loss": "Log loss"},
)
figura_logloss.update_traces(
    texttemplate="%{text:.4f}",
    textposition="outside",
)
figura_logloss.update_layout(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#172B3A",
    showlegend=False,
    yaxis_range=[0, max(resultados["log_loss"]) * 1.15],
)
st.plotly_chart(figura_logloss, width="stretch")

with st.expander("Cómo leer la validación"):
    st.write(
        "El log loss mide la calidad de las probabilidades asignadas a "
        "los resultados observados; un valor menor es mejor. La referencia "
        "uniforme obtiene aproximadamente 4.6052 para 100 números."
    )

    if modelo_uniforme.empty:
        st.warning(
            "No hay un resultado del modelo uniforme en este archivo, "
            "así que esta comparación no permite evaluar modelos frente "
            "a esa referencia."
        )
    else:
        log_loss_uniforme = float(
            modelo_uniforme.iloc[0]["log_loss"]
        )
        modelos_no_uniformes = resultados.loc[
            resultados["modelo"] != "Uniforme"
        ]
        supera_referencia = (
            not modelos_no_uniformes.empty
            and modelos_no_uniformes["log_loss"].min()
            < log_loss_uniforme
        )

        if supera_referencia:
            st.info(
                "Al menos un modelo tuvo menor log loss que la referencia "
                "uniforme en esta validación. Es un resultado exploratorio; "
                "no demuestra una ventaja estable ni anticipa aciertos."
            )
        else:
            st.warning(
                "En esta validación, ningún modelo experimental superó "
                "al modelo uniforme en log loss."
            )

if "fecha_generacion_utc" in resultados.columns:
    st.caption(
        "Validación generada (UTC): "
        f"{resultados['fecha_generacion_utc'].iloc[0]}"
    )
if {
    "primer_sorteo_validacion",
    "ultimo_sorteo_validacion",
}.issubset(resultados.columns):
    st.caption(
        "Sorteos del período de validación: "
        f"#{int(resultados['primer_sorteo_validacion'].iloc[0]):,} "
        f"a #{int(resultados['ultimo_sorteo_validacion'].iloc[0]):,}."
    )

st.caption(
    "Estas métricas describen una evaluación histórica; "
    "no son pronósticos para sorteos futuros."
)
