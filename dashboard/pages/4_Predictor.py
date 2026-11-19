
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from services.database import cargar_sorteos
from src.prediction.predictor import (
    MODELOS_DISPONIBLES,
    generar_prediccion,
)


st.set_page_config(
    page_title="LottoLab CR | Predictor",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 Predictor LottoLab CR")

st.caption(
    "Generá estimaciones experimentales utilizando "
    "los modelos estadísticos y de machine learning "
    "de LottoLab CR."
)

st.divider()


# =====================================================
# CARGA DEL HISTORIAL
# =====================================================

try:
    historial = cargar_sorteos()
except Exception as error:
    st.error("No se pudo cargar el historial de sorteos.")
    st.exception(error)
    st.stop()

if historial.empty:
    st.warning("No hay sorteos disponibles.")
    st.stop()

historial = historial.sort_values(
    ["fecha", "hora", "sorteo"]
).reset_index(drop=True)

ultimo = historial.iloc[-1]

ultima_fecha = pd.Timestamp(
    ultimo["fecha"]
).date()

ultima_hora = str(ultimo["hora"])[:5]

st.subheader("📊 Información disponible")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Sorteos registrados",
    f"{len(historial):,}",
)

col2.metric(
    "Última fecha registrada",
    ultima_fecha.strftime("%d/%m/%Y"),
)

col3.metric(
    "Último número ganador",
    ultimo["numero"],
)

st.info(
    "El historial disponible termina el "
    f"{ultima_fecha.strftime('%d/%m/%Y')} "
    f"a las {ultima_hora}. "
    "Las estimaciones generadas aquí son experimentales. "
    "Antes de utilizarlas para sorteos actuales, "
    "debemos actualizar la base de datos."
)

st.divider()


# =====================================================
# CONFIGURACIÓN
# =====================================================

st.subheader("⚙️ Configurar estimación")

with st.form("formulario_predictor"):

    col1, col2 = st.columns(2)

    with col1:
        modelo_nombre = st.selectbox(
            "Modelo predictivo",
            options=MODELOS_DISPONIBLES,
            index=1,
        )

        cantidad = st.segmented_control(
            "Cantidad de números",
            options=[3, 5, 10],
            default=5,
        )

    with col2:
        fecha_objetivo = st.date_input(
            "Fecha del sorteo objetivo",
            value=ultima_fecha + timedelta(days=1),
            min_value=ultima_fecha,
        )

        hora_objetivo = st.selectbox(
            "Horario del sorteo",
            options=["12:55", "16:30", "19:30"],
        )

    generar = st.form_submit_button(
        "🎯 Generar estimación",
        type="primary",
        use_container_width=True,
    )


# =====================================================
# PREDICCIÓN
# =====================================================

if generar:

    objetivo = (
        fecha_objetivo,
        hora_objetivo,
    )

    ultimo_registro = (
        ultima_fecha,
        ultima_hora,
    )

    if objetivo <= ultimo_registro:
        st.error(
            "El sorteo objetivo debe ser posterior "
            "al último sorteo registrado."
        )
        st.stop()

    try:
        with st.spinner(
            "Entrenando el modelo y calculando estimaciones..."
        ):
            resultado = generar_prediccion(
                historial=historial,
                fecha_objetivo=fecha_objetivo,
                hora_objetivo=hora_objetivo,
                modelo_nombre=modelo_nombre,
                cantidad=cantidad,
            )

    except Exception as error:
        st.error("No fue posible generar la estimación.")
        st.exception(error)
        st.stop()

    st.divider()

    st.subheader("🏆 Ranking estimado")

    st.caption(
        f"Modelo: {resultado['modelo']} · "
        f"Fecha objetivo: {resultado['fecha_objetivo']} · "
        f"Horario: {resultado['hora_objetivo']}"
    )

    ranking = resultado["ranking"]

    columnas = st.columns(
        min(len(ranking), 5)
    )

    for indice, fila in ranking.iterrows():

        with columnas[indice % len(columnas)]:

            with st.container(border=True):

                st.caption(
                    f"Posición #{indice + 1}"
                )

                st.markdown(
                    f"## {fila['Número']}"
                )

                st.metric(
                    "Probabilidad estimada",
                    f"{fila['Probabilidad estimada (%)']:.3f} %",
                )

    st.divider()

    st.subheader("📋 Resultados detallados")

    st.dataframe(
        ranking,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Las estimaciones son resultados de modelos "
        "experimentales. Ninguno ha demostrado todavía "
        "una ventaja predictiva sobre el azar."
    )
