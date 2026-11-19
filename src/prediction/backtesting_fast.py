
import numpy as np


def backtesting_rapido(
    numeros,
    ventana=100,
    alpha=1.0,
    inicio=1000,
):
    """
    Backtesting walk-forward con ventana móvil.

    Cada predicción utiliza exclusivamente
    resultados anteriores al sorteo evaluado.
    """

    if not isinstance(ventana, int) or ventana <= 0:
        raise ValueError("Ventana inválida.")

    if not np.isfinite(alpha) or alpha <= 0:
        raise ValueError("Alpha debe ser positivo.")

    historial = list(numeros)

    if not 0 < inicio < len(historial):
        raise ValueError("Inicio inválido.")

    if ventana > inicio:
        raise ValueError("Ventana mayor que historial inicial.")

    validos = {f"{n:02d}" for n in range(100)}

    if any(numero not in validos for numero in historial):
        raise ValueError("Hay números inválidos.")

    datos = np.array(
        [int(numero) for numero in historial],
        dtype=np.int64,
    )

    conteos = np.bincount(
        datos[inicio - ventana:inicio],
        minlength=100,
    ).astype(np.int64)

    perdidas = []
    aciertos = 0

    for indice in range(inicio, len(datos)):
        probabilidades = (
            (conteos + alpha)
            / (ventana + 100 * alpha)
        )

        resultado = datos[indice]

        perdidas.append(
            -np.log(probabilidades[resultado])
        )

        # Empates: priorizar el número menor,
        # igual que en el modelo original.
        top_5 = np.lexsort(
            (np.arange(100), -conteos)
        )[:5]

        if resultado in top_5:
            aciertos += 1

        # Retirar el sorteo que sale de la ventana.
        anterior = datos[indice - ventana]
        conteos[anterior] -= 1

        # Incorporar el sorteo recién observado.
        conteos[resultado] += 1

    total = len(perdidas)

    return {
        "ventana": ventana,
        "alpha": alpha,
        "predicciones": total,
        "log_loss": float(np.mean(perdidas)),
        "aciertos_top_5": int(aciertos),
        "porcentaje_top_5": float(
            aciertos / total * 100
        ),
    }
