
from pathlib import Path
import os

import pandas as pd
import plotly.express as px
import psycopg
import streamlit as st
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

st.set_page_config(
    page_title="LottoLab CR",
    page_icon="🎯",
    layout="wide",
)


@st.cache_data(ttl=300)
def cargar_sorteos():
    conexion = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    with psycopg.connect(**conexion) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    draw_id,
                    draw_date,
                    draw_time,
                    winning_number
                FROM draws
                ORDER BY draw_date, draw_time, draw_id
            """)

            registros = cursor.fetchall()
            columnas = [
                "sorteo",
                "fecha",
                "hora",
                "numero",
            ]

    df = pd.DataFrame(registros, columns=columnas)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["anio"] = df["fecha"].dt.year

    return df


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

anios = sorted(df["anio"].unique().tolist())

anios_seleccionados = st.sidebar.multiselect(
    "Seleccionar años",
    options=anios,
    default=anios,
)

df_filtrado = df[
    df["anio"].isin(anios_seleccionados)
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

fig = px.bar(
    frecuencias,
    x="Número",
    y="Apariciones",
    title="Distribución de los 100 números",
)

fig.update_layout(
    xaxis=dict(type="category"),
    height=450,
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
