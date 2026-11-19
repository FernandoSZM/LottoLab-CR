
import pandas as pd
from scipy.stats import chi2_contingency


def analizar_horarios(df):
    """
    Analiza la asociación entre el horario
    y la terminación del número ganador.
    """

    columnas = {"hora", "numero"}

    if not columnas.issubset(df.columns):
        raise ValueError("Faltan columnas obligatorias.")

    datos = df[["hora", "numero"]].copy()

    if datos.isna().any().any():
        raise ValueError("Hay datos nulos.")

    validos = {f"{n:02d}" for n in range(100)}

    if not datos["numero"].isin(validos).all():
        raise ValueError("Hay números inválidos.")

    datos["horario"] = datos["hora"].astype(str).str[:5]
    datos["terminacion"] = datos["numero"].str[-1]

    matriz = pd.crosstab(
        datos["horario"],
        datos["terminacion"],
    ).reindex(
        columns=[str(n) for n in range(10)],
        fill_value=0,
    )

    # Una sola categoría horaria no permite
    # contrastar diferencias entre horarios.
    if len(matriz) < 2:
        raise ValueError(
            "Se necesitan al menos dos horarios."
        )

    chi2, p_valor, grados_libertad, esperados = (
        chi2_contingency(matriz)
    )

    porcentajes = matriz.div(
        matriz.sum(axis=1),
        axis=0,
    ) * 100

    return {
        "matriz": matriz,
        "porcentajes": porcentajes,
        "chi2": float(chi2),
        "p_valor": float(p_valor),
        "grados_libertad": int(grados_libertad),
        "esperada_minima": float(esperados.min()),
    }
