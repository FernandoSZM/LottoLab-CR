
import pandas as pd
import streamlit as st

from services.database import cargar_sorteos


st.set_page_config(
    page_title="Calidad de datos | LottoLab CR",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Calidad de datos")
st.caption(
    "Auditoría de integridad y consistencia "
    "de los sorteos históricos"
)

try:
    df = cargar_sorteos()
except Exception as error:
    st.error("No se pudieron cargar los datos.")
    st.exception(error)
    st.stop()

if df.empty:
    st.warning("No hay registros disponibles.")
    st.stop()

# Validaciones de calidad
total = len(df)

duplicados_id = df["sorteo"].duplicated().sum()

valores_nulos = df[
    ["sorteo", "fecha", "hora", "numero"]
].isna().sum().sum()

numeros_invalidos = (
    ~df["numero"].astype("string").str.fullmatch(r"\d{2}")
).fillna(True).sum()

# Dos sorteos registrados a la misma fecha y hora
horarios_duplicados = (
    df.groupby(["fecha", "hora"], dropna=False)
    .filter(lambda grupo: len(grupo) > 1)
    .sort_values(["fecha", "hora", "sorteo"])
)

grupos_duplicados = (
    horarios_duplicados[["fecha", "hora"]]
    .drop_duplicates()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Registros", f"{total:,}")
col2.metric("IDs duplicados", int(duplicados_id))
col3.metric("Valores nulos", int(valores_nulos))
col4.metric(
    "Horarios duplicados",
    len(grupos_duplicados),
)

st.divider()

st.subheader("Estado de las validaciones")

if duplicados_id == 0 and valores_nulos == 0 and numeros_invalidos == 0:
    st.success(
        "No se detectaron problemas de integridad "
        "en IDs, valores obligatorios ni formato de números."
    )
else:
    st.warning(
        "Se detectaron problemas de integridad "
        "que requieren revisión."
    )

st.write(f"**Números con formato inválido:** {numeros_invalidos}")

st.divider()

st.subheader("Anomalías de horarios")

if horarios_duplicados.empty:
    st.success("No se detectaron horarios duplicados.")
else:
    st.warning(
        f"Se encontraron {len(grupos_duplicados)} "
        "combinaciones de fecha y hora duplicadas."
    )

    st.dataframe(
        horarios_duplicados[
            ["sorteo", "fecha", "hora", "numero"]
        ],
        hide_index=True,
        width="stretch",
    )

    st.info(
        "Los horarios duplicados se presentan para revisión. "
        "No se modifican automáticamente los datos originales."
    )
