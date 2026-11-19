
import numpy as np
import pandas as pd
import pytest

from src.prediction.features import (
    crear_caracteristicas,
    crear_caracteristicas_futuras,
)
from src.prediction.ml_model import CARACTERISTICAS
from src.prediction.predictor import generar_prediccion


@pytest.fixture
def historial():
    fechas = pd.date_range(
        "2025-01-01",
        periods=120,
        freq="D",
    )

    return pd.DataFrame({
        "sorteo": range(1, 121),
        "fecha": fechas,
        "hora": ["12:55"] * 120,
        "numero": [
            f"{(i * 17) % 100:02d}"
            for i in range(120)
        ],
    })


def test_caracteristicas_sin_fuga_temporal(historial):
    indice = 80

    anteriores = historial.iloc[:indice]
    objetivo = historial.iloc[indice]

    futuras = crear_caracteristicas_futuras(
        anteriores,
        objetivo["fecha"],
        objetivo["hora"],
    )

    historicas = crear_caracteristicas(
        historial.iloc[:indice + 1]
    ).iloc[-1]

    for columna in CARACTERISTICAS:
        assert str(futuras.iloc[0][columna]) == str(
            historicas[columna]
        )


def test_probabilidades_bayesianas(historial):
    resultado = generar_prediccion(
        historial,
        "2025-05-02",
        "12:55",
        modelo_nombre="Bayesiano",
        cantidad=5,
    )

    probabilidades = resultado["probabilidades"]

    assert probabilidades.shape == (100,)
    assert np.isclose(probabilidades.sum(), 1.0)
    assert np.all(probabilidades >= 0)
    assert len(resultado["ranking"]) == 5


def test_modelo_uniforme(historial):
    resultado = generar_prediccion(
        historial,
        "2025-05-02",
        "12:55",
        modelo_nombre="Uniforme",
        cantidad=10,
    )

    assert np.allclose(
        resultado["probabilidades"],
        np.full(100, 0.01),
    )
    assert len(resultado["ranking"]) == 10


def test_rechaza_fecha_anterior(historial):
    with pytest.raises(ValueError):
        generar_prediccion(
            historial,
            "2025-01-10",
            "12:55",
            modelo_nombre="Bayesiano",
        )


def test_rechaza_modelo_desconocido(historial):
    with pytest.raises(ValueError):
        generar_prediccion(
            historial,
            "2025-05-02",
            "12:55",
            modelo_nombre="Modelo inventado",
        )


def test_rechaza_ranking_invalido(historial):
    with pytest.raises(ValueError):
        generar_prediccion(
            historial,
            "2025-05-02",
            "12:55",
            cantidad=7,
        )
