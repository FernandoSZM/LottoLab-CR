
import pandas as pd


def calcular_ranking(numeros_ganadores, cantidad=5):
    """
    Calcula los números más frecuentes y su
    porcentaje de aparición histórica.
    """

    if cantidad not in (3, 5, 10):
        raise ValueError("La cantidad debe ser 3, 5 o 10.")

    numeros = pd.Series(numeros_ganadores, dtype="string")

    if numeros.empty:
        raise ValueError("No hay sorteos para analizar.")

    if numeros.isna().any():
        raise ValueError("Hay números ganadores nulos.")

    if not numeros.str.fullmatch(r"\d{2}").all():
        raise ValueError("Hay números con formato inválido.")

    frecuencias = (
        numeros.value_counts()
        .reindex(
            [f"{numero:02d}" for numero in range(100)],
            fill_value=0,
        )
    )

    total = len(numeros)

    ranking = pd.DataFrame({
        "Número": frecuencias.index,
        "Apariciones": frecuencias.to_numpy(),
    })

    ranking["Frecuencia histórica (%)"] = (
        ranking["Apariciones"] / total * 100
    )

    ranking = (
        ranking.sort_values(
            ["Apariciones", "Número"],
            ascending=[False, True],
        )
        .head(cantidad)
        .reset_index(drop=True)
    )

    return ranking
