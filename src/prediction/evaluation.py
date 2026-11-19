
import numpy as np
import pandas as pd


def evaluar_modelo(probabilidades, resultados_reales):
    """
    Evalúa probabilidades sobre resultados no vistos.

    Devuelve log loss y aciertos del Top 5.
    """

    reales = pd.Series(
        list(resultados_reales),
        dtype="string",
    )

    if reales.empty:
        raise ValueError("No hay resultados para evaluar.")

    numeros = [f"{n:02d}" for n in range(100)]

    if reales.isna().any() or not reales.isin(numeros).all():
        raise ValueError("Hay resultados inválidos.")

    probabilidades = pd.Series(probabilidades)

    if (
        not probabilidades.index.is_unique
        or set(probabilidades.index) != set(numeros)
    ):
        raise ValueError(
            "Se requieren probabilidades para los 100 números."
        )

    probabilidades = probabilidades.reindex(numeros).astype(float)

    if (
        not np.isfinite(probabilidades.to_numpy()).all()
        or (probabilidades <= 0).any()
        or not np.isclose(probabilidades.sum(), 1.0)
    ):
        raise ValueError("Distribución de probabilidades inválida.")

    probabilidades_reales = (
        reales.map(probabilidades).to_numpy(dtype=float)
    )

    log_loss = -np.log(probabilidades_reales).mean()

    top_5 = set(
        probabilidades.sort_values(
            ascending=False,
            kind="stable",
        ).head(5).index
    )

    aciertos_top_5 = reales.isin(top_5).sum()

    return {
        "log_loss": float(log_loss),
        "aciertos_top_5": int(aciertos_top_5),
        "porcentaje_top_5": float(
            aciertos_top_5 / len(reales) * 100
        ),
    }
