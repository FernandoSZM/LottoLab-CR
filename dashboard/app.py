import html
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st


DASHBOARD_DIR = Path(__file__).resolve().parent
ROOT_DIR = DASHBOARD_DIR.parent

if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from services.database import cargar_sorteos
from src.prediction.predictor import (
    MODELOS_DISPONIBLES,
    generar_prediccion,
)


st.set_page_config(
    page_title="LottoLab CR",
    page_icon="🎱",
    layout="wide",
)

st.markdown(
    """
    <style>
    .ll-hero {
        padding: 1.5rem 1.75rem;
        margin: 0.25rem 0 1.5rem;
        background: #ffffff;
        border: 1px solid #dfe7ed;
        border-left: 4px solid #0f766e;
        border-radius: 1rem;
    }

    .ll-hero-label,
    .ll-number-position,
    .ll-number-caption {
        color: #64748b;
        font-size: 0.82rem;
    }

    .ll-hero-number {
        color: #102a36;
        font-size: clamp(2.5rem, 7vw, 4.5rem);
        font-weight: 700;
        line-height: 1.1;
        letter-spacing: -0.04em;
        margin: 0.2rem 0;
    }

    .ll-result-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(112px, 1fr));
        gap: 0.75rem;
        margin: 1rem 0;
    }

    .ll-number-card {
        min-width: 0;
        padding: 1rem 0.75rem;
        text-align: center;
        background: #ffffff;
        border: 1px solid #dfe7ed;
        border-radius: 0.9rem;
    }

    .ll-number-value {
        display: block;
        margin: 0.35rem 0;
        color: #0f766e;
        font-size: clamp(1.9rem, 5vw, 2.5rem);
        font-weight: 700;
        line-height: 1.1;
        font-variant-numeric: tabular-nums;
    }

    @media (max-width: 480px) {
        .ll-hero {
            padding: 1.1rem;
        }

        .ll-result-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False, max_entries=16)
def generar_prediccion_cacheada(
    historial: pd.DataFrame,
    fecha_objetivo: date,
    hora_objetivo: str,
    modelo_nombre: str,
):
    return generar_prediccion(
        historial=historial,
        fecha_objetivo=fecha_objetivo,
        hora_objetivo=hora_objetivo,
        modelo_nombre=modelo_nombre,
        cantidad=10,
    )


def render_inicio():
    st.title("LottoLab CR")
    st.caption(
        "Explora resultados de Nuevos Tiempos y genera "
        "una estimación experimental a partir del historial disponible."
    )

    try:
        historial = cargar_sorteos()
    except Exception as error:
        st.error("No se pudo cargar el historial desde PostgreSQL.")
        with st.expander("Detalles técnicos"):
            st.exception(error)
        st.stop()

    if historial.empty:
        st.warning("No hay sorteos disponibles para generar una estimación.")
        st.stop()

    historial = historial.sort_values(
        ["fecha", "hora", "sorteo"]
    ).reset_index(drop=True)

    ultimo = historial.iloc[-1]
    ultima_fecha = pd.Timestamp(ultimo["fecha"]).date()
    ultima_hora = str(ultimo["hora"])[:5]
    fecha_objetivo_inicial = ultima_fecha + timedelta(days=1)
    horarios_observados = sorted(
        {
            str(horario)[:5]
            for horario in historial.loc[
                historial["fecha"].dt.date == ultima_fecha,
                "hora",
            ]
        }
    )

    if not horarios_observados:
        st.error(
            "No se encontraron horarios en los registros "
            "de la última fecha disponible."
        )
        st.stop()

    esta_desactualizado = (
        ultima_fecha < date.today() - timedelta(days=7)
    )

    if esta_desactualizado:
        st.warning(
            "Modo de demostración. "
            f"El historial llega hasta {ultima_fecha:%d/%m/%Y}; "
            "esta estimación no representa un pronóstico vigente."
        )
    else:
        st.caption(
            f"Historial disponible hasta {ultima_fecha:%d/%m/%Y}. "
            "La estimación es experimental."
        )

    st.subheader("Generar una estimación")
    st.write(
        "Elige una fecha, un horario observado en el último día registrado "
        "y el tamaño del ranking."
    )

    with st.form("formulario_predictor"):
        col_fecha, col_horario, col_ranking = st.columns(3)

        with col_fecha:
            fecha_objetivo = st.date_input(
                "Fecha objetivo",
                value=fecha_objetivo_inicial,
                min_value=fecha_objetivo_inicial,
            )

        with col_horario:
            hora_objetivo = st.selectbox(
                "Horario registrado",
                options=horarios_observados,
                help=(
                    "Opciones registradas en la última fecha del historial; "
                    "no son una confirmación de horarios oficiales vigentes."
                ),
            )

        with col_ranking:
            cantidad = st.selectbox(
                "Mostrar números",
                options=[3, 5, 10],
                index=1,
                format_func=lambda valor: f"Top {valor}",
            )

        with st.expander("Ajustes avanzados · modelo"):
            modelo_nombre = st.selectbox(
                "Modelo experimental",
                options=MODELOS_DISPONIBLES,
                index=MODELOS_DISPONIBLES.index(
                    "Regresión logística"
                ),
                help=(
                    "El modelo uniforme es una referencia: asigna "
                    "la misma probabilidad a los 100 números."
                ),
            )

        generar = st.form_submit_button(
            "Generar estimación",
            type="primary",
            use_container_width=True,
        )

    if generar:
        st.session_state.pop("estimacion_lottolab", None)
        try:
            with st.spinner("Calculando la estimación…"):
                resultado = generar_prediccion_cacheada(
                    historial=historial,
                    fecha_objetivo=fecha_objetivo,
                    hora_objetivo=hora_objetivo,
                    modelo_nombre=modelo_nombre,
                )
            resultado["ranking"] = (
                resultado["ranking"]
                .head(cantidad)
                .reset_index(drop=True)
            )
            st.session_state["estimacion_lottolab"] = resultado
        except Exception as error:
            st.error("No fue posible generar la estimación.")
            with st.expander("Detalles técnicos"):
                st.exception(error)

    resultado = st.session_state.get("estimacion_lottolab")

    if resultado is not None:
        st.divider()
        st.subheader(
            f"Estimación para {pd.Timestamp(resultado['fecha_objetivo']):%d/%m/%Y}"
        )
        st.caption(
            f"{resultado['hora_objetivo']} · {resultado['modelo']} · "
            f"Basado en {resultado['sorteos_entrenamiento']:,} sorteos"
        )

        if resultado["modelo"] == "Uniforme":
            st.info(
                "El modelo uniforme asigna 1 % a cada uno de los 100 números. "
                "Todos están empatados, así que no hay favoritos ni un ranking "
                "que sea significativo."
            )
        else:
            st.write("Números mejor posicionados por el modelo")
            tarjetas = []
            for posicion, fila in resultado["ranking"].iterrows():
                numero = html.escape(str(fila["Número"]))
                probabilidad = float(
                    fila["Probabilidad estimada (%)"]
                )
                tarjetas.append(
                    "<article class='ll-number-card'>"
                    f"<span class='ll-number-position'>#{posicion + 1}</span>"
                    f"<strong class='ll-number-value'>{numero}</strong>"
                    "<span class='ll-number-caption'>"
                    f"Estimación del modelo: {probabilidad:.2f} %"
                    "</span></article>"
                )

            st.markdown(
                "<div class='ll-result-grid'>"
                + "".join(tarjetas)
                + "</div>",
                unsafe_allow_html=True,
            )
            st.caption(
                "El orden y los porcentajes son resultados experimentales; "
                "no demuestran una ventaja predictiva frente al azar."
            )

    st.divider()
    st.subheader("Último resultado disponible")

    numero_ultimo = html.escape(str(ultimo["numero"]).zfill(2))
    st.markdown(
        "<section class='ll-hero'>"
        "<span class='ll-hero-label'>Número registrado</span>"
        f"<p class='ll-hero-number'>{numero_ultimo}</p>"
        f"<span class='ll-hero-label'>"
        f"{ultima_fecha:%d/%m/%Y} · {html.escape(ultima_hora)}"
        f" · Sorteo #{html.escape(str(ultimo['sorteo']))}"
        "</span></section>",
        unsafe_allow_html=True,
    )
    st.caption(
        "Es el último registro disponible en la base de datos; "
        "no necesariamente corresponde al sorteo más reciente celebrado."
    )

    st.divider()
    st.subheader("Explora LottoLab")
    col_stats, col_lab, col_quality = st.columns(3)

    with col_stats:
        st.page_link(
            estadisticas_page,
            label="Estadísticas históricas",
            icon=":material/monitoring:",
            use_container_width=True,
        )

    with col_lab:
        st.page_link(
            laboratorio_page,
            label="Laboratorio de modelos",
            icon=":material/science:",
            use_container_width=True,
        )

    with col_quality:
        st.page_link(
            calidad_page,
            label="Calidad de datos",
            icon=":material/fact_check:",
            use_container_width=True,
        )


inicio_page = st.Page(
    render_inicio,
    title="Inicio",
    icon=":material/home:",
    url_path="inicio",
    default=True,
)

estadisticas_page = st.Page(
    "pages/1_Analisis_Estadistico.py",
    title="Estadísticas",
    icon=":material/monitoring:",
    url_path="estadisticas",
)

laboratorio_page = st.Page(
    "pages/3_Laboratorio.py",
    title="Laboratorio",
    icon=":material/science:",
    url_path="laboratorio",
)

calidad_page = st.Page(
    "pages/2_Calidad_de_Datos.py",
    title="Calidad de datos",
    icon=":material/fact_check:",
    url_path="calidad",
)

pagina_actual = st.navigation(
    [
        inicio_page,
        estadisticas_page,
        laboratorio_page,
        calidad_page,
    ],
    position="top",
)
pagina_actual.run()
