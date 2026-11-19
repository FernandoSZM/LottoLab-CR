
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
    datos["dia_semana"] = datos["fecha"].dt.dayofweek

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
