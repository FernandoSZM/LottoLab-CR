
import numpy as np
import pandas as pd

from src.prediction.bayesian import ModeloBayesiano
from src.prediction.features import crear_caracteristicas
from src.prediction.metrics import evaluar_probabilidades
from src.prediction.ml_model import (
    entrenar_modelo_ml,
    obtener_probabilidades,
)
from src.prediction.tree_model import (
    entrenar_modelo_arboles,
    obtener_probabilidades_arboles,
)


def comparar_modelos(
    entrenamiento,
    validacion,
    c_logistica=0.00001,
):
    """
    Compara cuatro estrategias predictivas.

    Todos los modelos se evalúan sobre los
    mismos sorteos de validación.

    Los datos deben estar ordenados
    cronológicamente.
    """

    if entrenamiento.empty or validacion.empty:
        raise ValueError(
            "Entrenamiento y validación no pueden estar vacíos."
        )

    columnas_orden = ["fecha", "hora", "sorteo"]

    train = entrenamiento.sort_values(
        columnas_orden
    ).copy()

    test = validacion.sort_values(
        columnas_orden
    ).copy()

    if (
        tuple(train[columnas_orden].iloc[-1])
        >= tuple(test[columnas_orden].iloc[0])
    ):
        raise ValueError(
            "La validación debe ser posterior al entrenamiento."
        )

    # Construimos características con el historial
    # disponible hasta cada sorteo.
    historial = pd.concat(
        [train, test],
        ignore_index=True,
    )

    caracteristicas = crear_caracteristicas(historial)

    train_ml = caracteristicas.iloc[
        :len(train) - 3
    ].copy()

    test_ml = caracteristicas.iloc[
        len(train) - 3:
    ].copy()

    if len(test_ml) != len(test):
        raise ValueError(
            "La cantidad de sorteos de validación no coincide."
        )

    reales = test["numero"].astype(int).to_numpy()

    resultados = []

    def registrar(nombre, probabilidades):
        metricas = evaluar_probabilidades(
            probabilidades,
            reales,
        )

        resultados.append({
            "modelo": nombre,
            **metricas,
        })

    # 1. Modelo uniforme
    probabilidades_uniformes = np.full(
        (len(test), 100),
        0.01,
    )

    registrar(
        "Uniforme",
        probabilidades_uniformes,
    )

    # 2. Modelo bayesiano
    bayesiano = ModeloBayesiano(alpha=1.0)

    bayesiano.actualizar(train["numero"])

    distribucion = (
        bayesiano.probabilidades()
        .to_numpy(dtype=float)
    )

    probabilidades_bayesianas = np.tile(
        distribucion,
        (len(test), 1),
    )

    registrar(
        "Bayesiano",
        probabilidades_bayesianas,
    )

    # 3. Regresión logística
    logistica = entrenar_modelo_ml(
        train_ml,
        c=c_logistica,
    )

    probabilidades_logisticas = (
        obtener_probabilidades(
            logistica,
            test_ml,
        )
    )

    registrar(
        "Regresión logística",
        probabilidades_logisticas,
    )

    # 4. Árboles potenciados
    arboles = entrenar_modelo_arboles(
        train_ml
    )

    probabilidades_arboles = (
        obtener_probabilidades_arboles(
            arboles,
            test_ml,
        )
    )

    registrar(
        "Árboles potenciados",
        probabilidades_arboles,
    )

    return (
        pd.DataFrame(resultados)
        .sort_values("log_loss")
        .reset_index(drop=True)
    )
