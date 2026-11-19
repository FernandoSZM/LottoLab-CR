
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency


def analizar_transiciones(numeros):
    """
    Analiza la relación entre terminaciones
    de sorteos consecutivos.
    """

    historial = list(numeros)

    if len(historial) < 2:
        raise ValueError(
            "Se necesitan al menos dos sorteos."
        )

    validos = {f"{n:02d}" for n in range(100)}

    if any(numero not in validos for numero in historial):
        raise ValueError("Hay números inválidos.")

    terminaciones = np.array([
        int(numero[-1]) for numero in historial
    ])

    anteriores = terminaciones[:-1]
    siguientes = terminaciones[1:]

    matriz = pd.crosstab(
        pd.Series(anteriores, name="Anterior"),
        pd.Series(siguientes, name="Siguiente"),
    ).reindex(
        index=range(10),
        columns=range(10),
        fill_value=0,
    )

    chi2, p_valor, grados_libertad, esperados = (
        chi2_contingency(matriz)
    )

    probabilidades = matriz.div(
        matriz.sum(axis=1),
        axis=0,
    ).fillna(0)

    return {
        "matriz": matriz,
        "probabilidades": probabilidades,
        "chi2": float(chi2),
        "p_valor": float(p_valor),
        "grados_libertad": int(grados_libertad),
        "frecuencia_esperada_minima": float(
            esperados.min()
        ),
    }
