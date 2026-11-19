
import pandas as pd


def dividir_datos_cronologicamente(df, proporcion=0.80):
    """
    Divide los sorteos en entrenamiento y evaluación,
    respetando el orden cronológico.
    """

    if not 0 < proporcion < 1:
        raise ValueError(
            "La proporción debe estar entre 0 y 1."
        )

    columnas = ["sorteo", "fecha", "hora", "numero"]

    if not set(columnas).issubset(df.columns):
        raise ValueError("Faltan columnas obligatorias.")

    datos = df[columnas].copy()

    datos = datos.sort_values(
        ["fecha", "hora", "sorteo"]
    ).reset_index(drop=True)

    if len(datos) < 2:
        raise ValueError(
            "Se necesitan al menos dos sorteos."
        )

    punto_corte = int(len(datos) * proporcion)

    punto_corte = max(
        1, min(punto_corte, len(datos) - 1)
    )

    entrenamiento = datos.iloc[:punto_corte].copy()
    evaluacion = datos.iloc[punto_corte:].copy()

    return entrenamiento, evaluacion
