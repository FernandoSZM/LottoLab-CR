
import plotly.express as px
import streamlit as st

from components.charts import grafico_frecuencias
from services.database import cargar_sorteos





st.set_page_config(
    page_title="LottoLab CR",
    page_icon="🎯",
    layout="wide",
)




st.title("🎯 LottoLab CR")
st.caption(
    "Laboratorio de análisis estadístico "
    "de Nuevos Tiempos — Costa Rica"
)

try:
    df = cargar_sorteos()
except Exception as error:
    st.error("No se pudo conectar con PostgreSQL.")
    st.exception(error)
    st.stop()

if df.empty:
    st.warning("No hay sorteos disponibles.")
    st.stop()

st.sidebar.header("Filtros")


anio_minimo = int(df["anio"].min())
anio_maximo = int(df["anio"].max())

rango_anios = st.sidebar.slider(
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
    st.info("Selecciona al menos un año.")
    st.stop()

total = len(df_filtrado)
numeros_unicos = df_filtrado["numero"].nunique()

col1, col2, col3 = st.columns(3)

col1.metric("Sorteos analizados", f"{total:,}")
col2.metric("Números distintos", numeros_unicos)
col3.metric(
    "Período",
    f"{df_filtrado['anio'].min()}–{df_filtrado['anio'].max()}"
)

st.divider()

st.subheader("Frecuencia de números ganadores")

numeros = [f"{n:02d}" for n in range(100)]

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

st.plotly_chart(fig, width="stretch")


col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("10 más frecuentes")
    st.dataframe(
        frecuencias.nlargest(10, "Apariciones"),
        hide_index=True,
    )

with col_der:
    st.subheader("10 menos frecuentes")
    st.dataframe(
        frecuencias.nsmallest(10, "Apariciones"),
        hide_index=True,
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

fig_anual.update_xaxes(type="category")
st.plotly_chart(fig_anual, width="stretch")

st.subheader("Explorador de registros")

st.dataframe(
    df_filtrado.sort_values(
        ["fecha", "hora", "sorteo"],
        ascending=False,
    ),
    hide_index=True,
)
