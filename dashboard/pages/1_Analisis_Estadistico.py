import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from services.database import cargar_sorteos
# Permite importar los módulos del proyecto desde dashboard/pages/
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.statistics.uniformity import calcular_uniformidad


st.set_page_config(
    page_title="Análisis estadístico | LottoLab CR",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Análisis estadístico")
st.caption(
    "Evaluación de la distribución de números "
    "ganadores de Nuevos Tiempos"
)

try:
    df = cargar_sorteos()
except Exception as error:
    st.error("No se pudieron cargar los sorteos.")
    st.exception(error)
    st.stop()

if df.empty:
    st.warning("No hay datos disponibles.")
    st.stop()

# Filtro independiente para esta página
anio_minimo = int(df["anio"].min())
anio_maximo = int(df["anio"].max())

rango = st.sidebar.slider(
    "Período de análisis",
    min_value=anio_minimo,
    max_value=anio_maximo,
    value=(anio_minimo, anio_maximo),
)

df_filtrado = df[
    df["anio"].between(rango[0], rango[1])
].copy()


# Análisis estadístico centralizado
resultado = calcular_uniformidad(df_filtrado["numero"])

numeros = resultado["frecuencias"].index.tolist()
frecuencias = resultado["frecuencias"]

total_sorteos = resultado["total"]
frecuencia_esperada = resultado["esperada"]

estadistico = resultado["chi2"]
p_valor = resultado["p_valor"]


col1, col2, col3 = st.columns(3)

col1.metric("Sorteos analizados", f"{total_sorteos:,}")
col2.metric("Estadístico χ²", f"{estadistico:.4f}")
col3.metric("Valor p", f"{p_valor:.6f}")

st.divider()

st.subheader("Prueba de uniformidad")

nivel_significancia = 0.05

if p_valor < nivel_significancia:
    st.warning(
        "Se rechaza la hipótesis de distribución uniforme "
        "al nivel de significancia del 5 %."
    )
else:
    st.success(
        "No se encontró evidencia estadística suficiente "
        "para rechazar la distribución uniforme al 5 %."
    )

st.info(
    "Este resultado no demuestra que los sorteos sean "
    "independientes ni permite predecir resultados futuros."
)

st.subheader("Frecuencias observadas y esperadas")

datos = pd.DataFrame({
    "Número": numeros,
    "Observadas": frecuencias.to_numpy(),
    "Esperadas": frecuencia_esperada,
})

fig = px.bar(
    datos,
    x="Número",
    y="Observadas",
    title="Distribución de frecuencias observadas",
)

fig.add_hline(
    y=frecuencia_esperada,
    line_dash="dash",
    line_color="#F59E0B",
    annotation_text=f"Esperada: {frecuencia_esperada:.2f}",
)

fig.update_layout(
    xaxis=dict(type="category"),
    height=480,
)

st.plotly_chart(fig, width="stretch")

st.subheader("Detalle por número")

datos["Diferencia"] = (
    datos["Observadas"] - datos["Esperadas"]
)

st.dataframe(
    datos,
    hide_index=True,
    width="stretch",
)
