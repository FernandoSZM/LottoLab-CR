
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chisquare


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data/processed/nuevos_tiempos.csv"


def analizar_por_anio():
    print("\n=== LOTTOLAB CR - YEARLY ANALYSIS ===\n")

    df = pd.read_csv(
        CSV_PATH,
        dtype={"numero": "string"},
    )

    df["fecha"] = pd.to_datetime(df["fecha"])
    df["anio"] = df["fecha"].dt.year

    numeros = [f"{n:02d}" for n in range(100)]
    resultados = []

    for anio, grupo in df.groupby("anio"):
        frecuencias = (
            grupo["numero"]
            .value_counts()
            .reindex(numeros, fill_value=0)
        )

        total = len(grupo)
        esperado = total / 100

        estadistico, p_valor = chisquare(
            f_obs=frecuencias.to_numpy(),
            f_exp=np.full(100, esperado),
        )

        resultados.append({
            "anio": int(anio),
            "sorteos": total,
            "frecuencia_esperada": round(esperado, 2),
            "chi_cuadrado": round(estadistico, 4),
            "p_valor": round(p_valor, 6),
            "numero_mas_frecuente": frecuencias.idxmax(),
            "apariciones_maximas": int(frecuencias.max()),
            "numero_menos_frecuente": frecuencias.idxmin(),
            "apariciones_minimas": int(frecuencias.min()),
        })

    resultado_df = pd.DataFrame(resultados)

    print(resultado_df.to_string(index=False))

    print("\n=== INTERPRETACION ===")

    for fila in resultados:
        estado = (
            "Desviacion significativa"
            if fila["p_valor"] < 0.05
            else "Sin evidencia suficiente de desviacion"
        )

        print(f"{fila['anio']}: {estado}")

    print(
        "\nNota: estas son pruebas exploratorias por anio. "
        "Al realizar multiples pruebas, pueden aparecer "
        "resultados significativos por azar."
    )


if __name__ == "__main__":
    analizar_por_anio()
