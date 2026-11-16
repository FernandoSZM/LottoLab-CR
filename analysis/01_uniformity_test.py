
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chisquare


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data/processed/nuevos_tiempos.csv"


def analizar_uniformidad():
    print("\n=== LOTTOLAB CR - UNIFORMITY TEST ===\n")

    df = pd.read_csv(
        CSV_PATH,
        dtype={"numero": "string"}
    )

    # Generar los 100 numeros posibles.
    numeros = [f"{n:02d}" for n in range(100)]

    # Contar apariciones, incluyendo numeros con frecuencia cero.
    frecuencias = (
        df["numero"]
        .value_counts()
        .reindex(numeros, fill_value=0)
    )

    total = len(df)
    esperado = total / 100

    # Prueba chi-cuadrado de bondad de ajuste.
    estadistico, p_valor = chisquare(
        f_obs=frecuencias.to_numpy(),
        f_exp=np.full(100, esperado)
    )

    print(f"Total de sorteos: {total}")
    print(f"Frecuencia esperada: {esperado:.2f}")

    print(f"\nEstadistico chi-cuadrado: {estadistico:.4f}")
    print(f"Valor p: {p_valor:.6f}")

    print("\nNumeros mas frecuentes:")
    print(frecuencias.sort_values(ascending=False).head(10).to_string())

    print("\nNumeros menos frecuentes:")
    print(frecuencias.sort_values(ascending=True).head(10).to_string())

    alpha = 0.05

    print("\n=== INTERPRETACION ===")

    if p_valor < alpha:
        print(
            "Se rechaza la hipotesis de distribucion "
            "uniforme al nivel de significancia del 5%."
        )
    else:
        print(
            "No se encuentra evidencia estadistica suficiente "
            "para rechazar una distribucion uniforme al 5%."
        )

    print("\n=== FIN DEL ANALISIS ===")


if __name__ == "__main__":
    analizar_uniformidad()
