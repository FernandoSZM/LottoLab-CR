
import pytest

from src.statistics.uniformity import calcular_uniformidad


def test_distribucion_uniforme():
    """Cada número aparece exactamente 10 veces."""

    numeros = [
        f"{numero:02d}"
        for numero in range(100)
        for _ in range(10)
    ]

    resultado = calcular_uniformidad(numeros)

    assert resultado["total"] == 1000
    assert resultado["esperada"] == 10
    assert resultado["chi2"] == pytest.approx(0)
    assert resultado["p_valor"] == pytest.approx(1)


def test_distribucion_no_uniforme():
    """Todos los sorteos contienen el número 00."""

    numeros = ["00"] * 1000

    resultado = calcular_uniformidad(numeros)

    assert resultado["total"] == 1000
    assert resultado["frecuencias"]["00"] == 1000
    assert resultado["frecuencias"]["01"] == 0
    assert resultado["p_valor"] < 0.05


def test_lista_vacia():
    """Una lista sin sorteos debe generar un error."""

    with pytest.raises(ValueError):
        calcular_uniformidad([])
