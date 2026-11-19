
import numpy as np

from src.prediction.rolling import modelo_ventana_movil


def backtesting_ventana_movil(
    numeros,
    ventana=100,
    alpha=1.0,
    inicio=1000,
):
    """
    Simula predicciones cronológicas.

    Cada predicción utiliza solamente los sorteos
    anteriores al resultado que se intenta predecir.
    """

    historial = list(numeros)

    if ventana <= 0:
        raise ValueError("La ventana debe ser positiva.")

    if not 0 < inicio < len(historial):
        raise ValueError("Inicio inválido.")

    if ventana > inicio:
        raise ValueError(
            "La ventana no puede superar el historial inicial."
        )

    numeros_validos = {f"{n:02d}" for n in range(100)}

    if any(numero not in numeros_validos for numero in historial):
        raise ValueError("Hay números inválidos.")

    perdidas = []
    aciertos_top_5 = 0

    for indice in range(inicio, len(historial)):
        anteriores = historial[:indice]

        modelo = modelo_ventana_movil(
            anteriores,
            ventana=ventana,
            alpha=alpha,
        )

        probabilidades = modelo.probabilidades()
        resultado_real = historial[indice]

        probabilidad_real = float(
            probabilidades.loc[resultado_real]
        )

        perdidas.append(-np.log(probabilidad_real))

        top_5 = set(modelo.ranking(5)["Número"])

        if resultado_real in top_5:
            aciertos_top_5 += 1

    total_predicciones = len(perdidas)

    return {
        "ventana": ventana,
        "alpha": alpha,
        "predicciones": total_predicciones,
        "log_loss": float(np.mean(perdidas)),
        "aciertos_top_5": aciertos_top_5,
        "porcentaje_top_5": (
            aciertos_top_5 / total_predicciones * 100
        ),
    }
