
import numpy as np
import pytest

from src.prediction.metrics import evaluar_probabilidades


def test_distribucion_uniforme():
    probabilidades = np.full((3, 100), 0.01)
    resultados = [35, 72, 10]

    metricas = evaluar_probabilidades(
        probabilidades,
        resultados,
    )

    assert metricas["log_loss"] == pytest.approx(
        np.log(100)
    )
    assert metricas["empates_top_5"] == 3
    assert metricas["top_5_sin_empates"] is None
    assert metricas["sorteos"] == 3


def test_top5_sin_empates():
    probabilidades = np.full((1, 100), 0.005)
    probabilidades[0, :5] = 0.105

    assert probabilidades.sum() == pytest.approx(1.0)

    metricas = evaluar_probabilidades(
        probabilidades,
        [3],
    )

    assert metricas["empates_top_5"] == 0
    assert metricas["top_5_sin_empates"] == 100.0
    assert metricas["aciertos_top_5"] == 1


def test_prediccion_perfecta():
    probabilidades = np.zeros((1, 100))
    probabilidades[0, 35] = 1.0

    metricas = evaluar_probabilidades(
        probabilidades,
        [35],
    )

    assert metricas["log_loss"] == 0.0


def test_probabilidad_cero_para_ganador():
    probabilidades = np.zeros((1, 100))
    probabilidades[0, 72] = 1.0

    metricas = evaluar_probabilidades(
        probabilidades,
        [35],
    )

    assert np.isinf(metricas["log_loss"])


def test_probabilidades_negativas():
    probabilidades = np.full((1, 100), 0.01)
    probabilidades[0, 0] = -0.01

    with pytest.raises(ValueError):
        evaluar_probabilidades(
            probabilidades,
            [35],
        )


def test_probabilidades_no_normalizadas():
    probabilidades = np.full((1, 100), 0.02)

    with pytest.raises(ValueError):
        evaluar_probabilidades(
            probabilidades,
            [35],
        )


def test_cantidad_incorrecta_de_probabilidades():
    probabilidades = np.full((1, 99), 1 / 99)

    with pytest.raises(ValueError):
        evaluar_probabilidades(
            probabilidades,
            [35],
        )


def test_resultado_fuera_de_rango():
    probabilidades = np.full((1, 100), 0.01)

    with pytest.raises(ValueError):
        evaluar_probabilidades(
            probabilidades,
            [100],
        )


def test_datos_vacios():
    probabilidades = np.empty((0, 100))

    with pytest.raises(ValueError):
        evaluar_probabilidades(
            probabilidades,
            [],
        )
