
from src.prediction.bayesian import ModeloBayesiano


def modelo_ventana_movil(
    numeros_historicos,
    ventana=100,
    alpha=1.0,
):
    """
    Estima probabilidades utilizando únicamente
    los sorteos más recientes.
    """

    if ventana <= 0:
        raise ValueError(
            "La ventana debe ser mayor que cero."
        )

    historial = list(numeros_historicos)

    if not historial:
        raise ValueError(
            "No hay sorteos para analizar."
        )

    recientes = historial[-ventana:]

    modelo = ModeloBayesiano(alpha=alpha)
    modelo.actualizar(recientes)

    return modelo
