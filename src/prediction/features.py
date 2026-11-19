
import pandas as pd


def crear_caracteristicas(df):
    """
    Prepara características para machine learning.

    Cada fila utiliza exclusivamente información
    disponible antes del sorteo correspondiente.
    """

    columnas = {"sorteo", "fecha", "hora", "numero"}

    if not columnas.issubset(df.columns):
        raise ValueError("Faltan columnas obligatorias.")

    datos = df.copy()

    datos = datos.sort_values(
        ["fecha", "hora", "sorteo"]
    ).reset_index(drop=True)

    # Características del sorteo que vamos a predecir.
    datos["dia_semana"] = datos["fecha"].dt.day_of_week

    datos["mes"] = datos["fecha"].dt.month

    datos["horario"] = (
        datos["hora"].astype(str).str[:5]
    )

    # Resultados anteriores: nunca el actual.
    datos["numero_anterior"] = datos["numero"].shift(1)

    datos["numero_hace_2"] = datos["numero"].shift(2)

    datos["numero_hace_3"] = datos["numero"].shift(3)

    # Terminaciones de resultados anteriores.
    datos["terminacion_anterior"] = (
        datos["numero_anterior"].str[-1]
    )

    datos["terminacion_hace_2"] = (
        datos["numero_hace_2"].str[-1]
    )

    datos["terminacion_hace_3"] = (
        datos["numero_hace_3"].str[-1]
    )

    # Eliminamos las primeras filas sin historial suficiente.
    datos = datos.dropna(
        subset=[
            "numero_anterior",
            "numero_hace_2",
            "numero_hace_3",
        ]
    ).reset_index(drop=True)

    return datos


def crear_caracteristicas_futuras(
    historial,
    fecha_objetivo,
    hora_objetivo,
):
    """
    Construye las características de un sorteo
    cuyo resultado todavía no conocemos.

    Utiliza únicamente los resultados anteriores
    disponibles en el historial.
    """

    columnas = {"sorteo", "fecha", "hora", "numero"}

    if not columnas.issubset(historial.columns):
        raise ValueError(
            "El historial no tiene las columnas necesarias."
        )

    if len(historial) < 3:
        raise ValueError(
            "Se necesitan al menos tres sorteos anteriores."
        )

    fecha_objetivo = pd.Timestamp(
        fecha_objetivo
    ).normalize()

    hora_objetivo = str(
        hora_objetivo
    )[:5]

    # Ordenamos el historial cronológicamente.
    datos = historial.sort_values(
        ["fecha", "hora", "sorteo"]
    ).reset_index(drop=True)

    ultima_fecha = pd.Timestamp(
        datos.iloc[-1]["fecha"]
    ).normalize()

    ultima_hora = str(
        datos.iloc[-1]["hora"]
    )[:5]

    # No permitir estimar sorteos anteriores
    # al último resultado disponible.
    if (
        fecha_objetivo,
        hora_objetivo,
    ) <= (
        ultima_fecha,
        ultima_hora,
    ):
        raise ValueError(
            "El sorteo objetivo debe ser posterior "
            "al último sorteo del historial."
        )

    ultimos = (
        datos["numero"]
        .astype(str)
        .tail(3)
        .tolist()
    )

    anterior = ultimos[-1]
    hace_2 = ultimos[-2]
    hace_3 = ultimos[-3]

    return pd.DataFrame(
        [
            {
                "dia_semana": fecha_objetivo.day_of_week,
                "mes": fecha_objetivo.month,
                "horario": hora_objetivo,
                "numero_anterior": anterior,
                "numero_hace_2": hace_2,
                "numero_hace_3": hace_3,
                "terminacion_anterior": anterior[-1],
                "terminacion_hace_2": hace_2[-1],
                "terminacion_hace_3": hace_3[-1],
            }
        ]
    )
