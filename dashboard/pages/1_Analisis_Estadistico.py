import sys
from pathlib import Path

import plotly.express as px
import streamlit as st


DASHBOARD_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = DASHBOARD_DIR.parent

if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from components.charts import grafico_frecuencias
from services.database import cargar_sorteos
from src.statistics.ranking import calcular_ranking
from src.statistics.uniformity import calcular_uniformidad


st.set_page_config(
    page_title="Estadísticas | LottoLab CR",
    layout="wide",
)

st.title("Estadísticas")
st.caption(
    "Frecuencias históricas y comportamiento de los registros "
    "en el período que elijas."
)

try:
    df = cargar_sorteos()
except Exception as error:
    st.error("No se pudieron cargar los sorteos.")
    with st.expander("Detalles técnicos"):
        st.exception(error)
    st.stop()

if df.empty:
    st.warning("No hay datos disponibles para analizar.")
    st.stop()

anio_minimo = int(df["anio"].min())
anio_maximo = int(df["anio"].max())

rango_anios = st.slider(
    "Período",
    min_value=anio_minimo,
    max_value=anio_maximo,
    value=(anio_minimo, anio_maximo),
    step=1,
)

df_filtrado = df[
    df["anio"].between(rango_anios[0], rango_anios[1])
].copy()

if df_filtrado.empty:
    st.info("No hay sorteos dentro del período seleccionado.")
    st.stop()

total = len(df_filtrado)
numeros = [f"{numero:02d}" for numero in range(100)]
frecuencias = (
    df_filtrado["numero"]
    .value_counts()
    .reindex(numeros, fill_value=0)
    .rename_axis("Número")
    .reset_index(name="Apariciones")
)

st.subheader("Frecuencias de los números")
col_periodo, col_total = st.columns(2)
col_periodo.metric(
    "Período analizado",
    f"{rango_anios[0]}–{rango_anios[1]}",
)
col_total.metric("Sorteos registrados", f"{total:,}")

cantidad_ranking = st.segmented_control(
    "Tamaño del ranking",
    options=[3, 5, 10],
    default=5,
    format_func=lambda valor: f"Top {valor}",
)
ranking = calcular_ranking(
    df_filtrado["numero"],
    cantidad=cantidad_ranking,
)

columnas = st.columns(min(cantidad_ranking, 5))
for indice, fila in ranking.iterrows():
    with columnas[indice % len(columnas)]:
        with st.container(border=True):
            st.caption(f"Posición {indice + 1}")
            st.markdown(f"### {fila['Número']}")
            st.write(f"{int(fila['Apariciones']):,} apariciones")
            st.caption(
                f"Frecuencia histórica: "
                f"{fila['Frecuencia histórica (%)']:.2f} %"
            )

st.caption(
    "Las frecuencias describen el período seleccionado; "
    "no son probabilidades predictivas."
)

vista = st.segmented_control(
    "Visualización",
    options=[
        "Todos",
        "10 más frecuentes",
        "10 menos frecuentes",
    ],
    default="Todos",
)
figura_frecuencias = grafico_frecuencias(
    frecuencias=frecuencias,
    total_sorteos=total,
    vista=vista,
)
figura_frecuencias.update_layout(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#172B3A",
    height=420,
)
st.plotly_chart(figura_frecuencias, width="stretch")

with st.expander("Explorar el período en detalle"):
    col_mas, col_menos = st.columns(2)

    with col_mas:
        st.subheader("10 más frecuentes")
        st.dataframe(
            frecuencias.nlargest(10, "Apariciones"),
            hide_index=True,
            width="stretch",
        )

    with col_menos:
        st.subheader("10 menos frecuentes")
        st.dataframe(
            frecuencias.nsmallest(10, "Apariciones"),
            hide_index=True,
            width="stretch",
        )

    st.subheader("Sorteos registrados por año")
    sorteos_anuales = (
        df_filtrado.groupby("anio")
        .size()
        .reset_index(name="Sorteos")
    )
    figura_anual = px.bar(
        sorteos_anuales,
        x="anio",
        y="Sorteos",
        labels={"anio": "Año"},
    )
    figura_anual.update_xaxes(type="category")
    figura_anual.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#172B3A",
    )
    st.plotly_chart(figura_anual, width="stretch")

    st.subheader("Registros del período")
    st.dataframe(
        df_filtrado.sort_values(
            ["fecha", "hora", "sorteo"],
            ascending=False,
        ),
        hide_index=True,
        width="stretch",
    )

with st.expander("Prueba estadística de uniformidad"):
    resultado = calcular_uniformidad(df_filtrado["numero"])
    col_total, col_chi2, col_p = st.columns(3)
    col_total.metric("Sorteos analizados", f"{resultado['total']:,}")
    col_chi2.metric("Estadístico χ²", f"{resultado['chi2']:.4f}")
    col_p.metric("Valor p", f"{resultado['p_valor']:.6f}")

    if resultado["p_valor"] < 0.05:
        st.warning(
            "En este período se rechaza la hipótesis de distribución "
            "uniforme al nivel del 5 %."
        )
    else:
        st.write(
            "En este período no se encontró evidencia suficiente para "
            "rechazar la distribución uniforme al nivel del 5 %."
        )

    st.caption(
        "Esta prueba no demuestra independencia ni permite predecir "
        "resultados futuros."
    )
