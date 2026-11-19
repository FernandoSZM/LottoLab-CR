
import numpy as np


def evaluar_probabilidades(probabilidades, resultados):
    """
    Evalúa distribuciones de probabilidad
    para los números del 00 al 99.

    Métricas:
    - Log loss
    - Aciertos Top 5
    - Porcentaje de aciertos Top 5
    - Empates en el límite del Top 5
    - Top 5 sin empates
    - Probabilidad máxima
    - Cantidad de sorteos evaluados
    """

    # 1. Convertir los datos a arrays.
    probabilidades = np.asarray(
        probabilidades,
        dtype=float,
    )

    resultados = np.asarray(
        resultados,
        dtype=int,
    )

    # 2. Validar dimensiones.
    if probabilidades.ndim != 2:
        raise ValueError(
            "Las probabilidades deben tener dos dimensiones."
        )

    if probabilidades.shape != (len(resultados), 100):
        raise ValueError(
            "Se esperan 100 probabilidades por sorteo."
        )

    if len(resultados) == 0:
        raise ValueError(
            "No hay sorteos para evaluar."
        )

    if resultados.ndim != 1:
        raise ValueError(
            "Los resultados deben tener una dimensión."
        )

    # 3. Validar resultados.
    if not np.all(
        (resultados >= 0) & (resultados <= 99)
    ):
        raise ValueError(
            "Hay resultados fuera del rango 00-99."
        )

    # 4. Validar probabilidades.
    if not np.all(np.isfinite(probabilidades)):
        raise ValueError(
            "Hay probabilidades no finitas."
        )

    if np.any(
        (probabilidades < 0) | (probabilidades > 1)
    ):
        raise ValueError(
            "Las probabilidades deben estar entre 0 y 1."
        )

    if not np.allclose(
        probabilidades.sum(axis=1),
        1.0,
        rtol=0,
        atol=1e-8,
    ):
        raise ValueError(
            "Las probabilidades no suman 1."
        )

    # 5. Calcular log loss.
    indices = np.arange(len(resultados))

    probabilidades_reales = probabilidades[
        indices,
        resultados,
    ]

    # Una probabilidad cero para el ganador
    # produce una pérdida infinita.
    with np.errstate(divide="ignore"):
        perdidas = -np.log(
            probabilidades_reales
        )

    log_loss = float(perdidas.mean())

    # 6. Calcular ranking Top 5.
    ranking = np.argsort(
        probabilidades,
        axis=1,
    )[:, -5:]

    aciertos = np.any(
        ranking == resultados[:, None],
        axis=1,
    )

    # 7. Detectar empates en el límite Top 5.
    ordenadas = np.sort(
        probabilidades,
        axis=1,
    )

    empates_top5 = np.isclose(
        ordenadas[:, -5],
        ordenadas[:, -6],
        rtol=1e-9,
        atol=1e-12,
    )

    cantidad_empates = int(
        empates_top5.sum()
    )

    # 8. Evaluar solamente selecciones
    # con un Top 5 claramente definido.
    sin_empates = ~empates_top5

    if sin_empates.any():
        top5_sin_empates = float(
            aciertos[sin_empates].mean() * 100
        )
    else:
        top5_sin_empates = None

    # 9. Devolver métricas.
    return {
        "log_loss": log_loss,
        "top_5": float(
            aciertos.mean() * 100
        ),
        "aciertos_top_5": int(
            aciertos.sum()
        ),
        "empates_top_5": cantidad_empates,
        "top_5_sin_empates": top5_sin_empates,
        "probabilidad_maxima": float(
            probabilidades.max() * 100
        ),
        "sorteos": len(resultados),
    }
