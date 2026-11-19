
import streamlit as st
import sys
from pathlib import Path

from services.database import cargar_ultimo_sorteo

from services.database import cargar_sorteos

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.statistics.ranking import calcular_ranking



st.set_page_config(
    page_title="LottoLab CR | Inicio",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 LottoLab CR")
st.caption(
    "Explora los resultados de Nuevos Tiempos "
    "de Costa Rica de forma sencilla."
)

st.divider()

st.subheader("🎱 Último sorteo registrado")

try:
    sorteo = cargar_ultimo_sorteo()
except Exception as error:
    st.error("No se pudo consultar el último sorteo.")
    st.exception(error)
    st.stop()

if sorteo is None:
    st.warning("Todavía no hay sorteos registrados.")
    st.stop()

fecha = sorteo["fecha"].strftime("%d/%m/%Y")
hora = sorteo["hora"].strftime("%I:%M %p")

st.markdown(
    """
    <style>
    .numero-ganador {
        font-size: 6rem;
        font-weight: 800;
        text-align: center;
        line-height: 1.2;
        color: #38BDF8;
    }
    .etiqueta-numero {
        text-align: center;
        color: #94A3B8;
        font-size: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="numero-ganador">{sorteo["numero"]}</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="etiqueta-numero">Número ganador</div>',
    unsafe_allow_html=True,
)

st.write("")

col1, col2, col3 = st.columns(3)

col1.metric("📅 Fecha", fecha)
col2.metric("🕒 Hora", hora)
col3.metric("🎟️ Sorteo", f'#{sorteo["sorteo"]}')

st.divider()


st.subheader("🏆 Números más frecuentes")

st.caption(
    "Descubre cuáles números han aparecido más veces "
    "en nuestros registros históricos."
)

cantidad = st.segmented_control(
    "¿Cuántos números quieres ver?",
    options=[3, 5, 10],
    default=5,
)

try:
    df_historico = cargar_sorteos()

    ranking = calcular_ranking(
        df_historico["numero"],
        cantidad=cantidad,
    )

except Exception as error:
    st.error("No se pudo calcular el ranking.")
    st.exception(error)
    st.stop()

columnas = st.columns(cantidad if cantidad <= 5 else 5)

for indice, fila in ranking.iterrows():
    with columnas[indice % len(columnas)]:
        with st.container(border=True):
            st.caption(f"Posición #{indice + 1}")

            st.markdown(
                f"### 🎱 {fila['Número']}"
            )

            st.metric(
                "Frecuencia histórica",
                f"{fila['Frecuencia histórica (%)']:.2f} %",
            )

            st.caption(
                f"{fila['Apariciones']} apariciones"
            )

st.info(
    "Estos porcentajes describen la frecuencia histórica "
    "de cada número. No representan una probabilidad "
    "predictiva validada para el próximo sorteo."
)

st.divider()


st.subheader("📊 Explora LottoLab CR")

st.write(
    "Consulta las estadísticas históricas, descubre "
    "los números más frecuentes y revisa la calidad "
    "de nuestros datos."
)

col_izq, col_der = st.columns(2)

with col_izq:
    st.page_link(
        "pages/3_Laboratorio.py",
        label="📈 Explorar estadísticas",
        use_container_width=True,
    )

with col_der:
    st.page_link(
        "pages/1_Analisis_Estadistico.py",
        label="🔬 Análisis estadístico",
        use_container_width=True,
    )

st.divider()

st.caption(
    "Fuente: registros históricos de Nuevos Tiempos. "
    "Los resultados mostrados corresponden a los datos "
    "disponibles en nuestra base de datos y no necesariamente "
    "al último sorteo celebrado por la JPS."
)
