
import numpy as np
import pandas as pd

from src.prediction.ml_model import (
    entrenar_modelo_ml,
    obtener_probabilidades,
)


def validacion_temporal_ml(
    datos,
    c=0.01,
    entrenamiento_inicial=2500,
    bloque=500,
):
    """
    Evalúa un modelo ML en múltiples períodos
    cronológicos sin utilizar información futura.
    """

    if entrenamiento_inicial < 100:
        raise ValueError(
            "El entrenamiento inicial es demasiado pequeño."
        )

    if bloque <= 0:
        raise ValueError("El bloque debe ser positivo.")

    if len(datos) <= entrenamiento_inicial:
        raise ValueError("No hay datos para validar.")

    resultados = []

    for inicio in range(
        entrenamiento_inicial,
        len(datos),
        bloque,
    ):
        fin = min(inicio + bloque, len(datos))

        train = datos.iloc[:inicio].copy()
        validacion = datos.iloc[inicio:fin].copy()

        modelo = entrenar_modelo_ml(train, c=c)

        probabilidades = obtener_probabilidades(
            modelo,
            validacion,
        )

        reales = (
            validacion["numero"]
            .astype(int)
            .to_numpy()
        )

        indices = np.arange(len(reales))

        perdidas = -np.log(
            probabilidades[indices, reales]
        )

        ranking = np.argsort(
            probabilidades,
            axis=1,
        )[:, -5:]

        aciertos = np.any(
            ranking == reales[:, None],
            axis=1,
        )

        resultados.append({
            "inicio": inicio,
            "fin": fin,
            "sorteos": len(validacion),
            "log_loss": float(perdidas.mean()),
            "top_5": float(aciertos.mean() * 100),
            "aciertos": int(aciertos.sum()),
        })

    return pd.DataFrame(resultados)
