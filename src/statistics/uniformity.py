
import pandas as pd
from scipy.stats import chisquare


def calcular_uniformidad(numeros_ganadores):
    """
    Calcula frecuencias y prueba chi-cuadrado
    para números ganadores del 00 al 99.
    """

    numeros = [f"{n:02d}" for n in range(100)]

    frecuencias = (
        pd.Series(numeros_ganadores)
        .value_counts()
        .reindex(numeros, fill_value=0)
    )

    total = int(frecuencias.sum())

    if total == 0:
        raise ValueError("No hay sorteos para analizar.")

    estadistico, p_valor = chisquare(
        f_obs=frecuencias.to_numpy()
    )

    return {
        "total": total,
        "frecuencias": frecuencias,
        "esperada": total / 100,
        "chi2": float(estadistico),
        "p_valor": float(p_valor),
    }
