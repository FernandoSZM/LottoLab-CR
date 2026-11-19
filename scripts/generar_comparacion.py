
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.prediction.comparison import comparar_modelos
from src.prediction.dataset import dividir_datos_cronologicamente


RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
ARCHIVO_RESULTADOS = (
    RAIZ_PROYECTO / "results" / "comparacion_modelos.csv"
)


def generar_comparacion():
    # Importamos aquí para utilizar el servicio existente.
    from dashboard.services.database import cargar_sorteos

    print("\nLottoLab CR — Comparación de modelos")
    print("-" * 50)

    datos = cargar_sorteos()

    if datos.empty:
        raise ValueError("No hay sorteos disponibles.")

    # Conservamos el 20 % final fuera del
    # proceso de desarrollo de modelos.
    entrenamiento, evaluacion_final = (
        dividir_datos_cronologicamente(datos)
    )

    corte = int(len(entrenamiento) * 0.80)

    train = entrenamiento.iloc[:corte].copy()
    validacion = entrenamiento.iloc[corte:].copy()

    print(f"Entrenamiento: {len(train)} sorteos")
    print(f"Validación: {len(validacion)} sorteos")
    print(
        "Evaluación final separada:",
        len(evaluacion_final),
        "sorteos",
    )

    resultados = comparar_modelos(
        train,
        validacion,
    )

    # Metadatos para identificar el experimento.
    resultados["fecha_generacion_utc"] = (
        datetime.now(timezone.utc).isoformat()
    )
    resultados["primer_sorteo_validacion"] = (
        int(validacion["sorteo"].iloc[0])
    )
    resultados["ultimo_sorteo_validacion"] = (
        int(validacion["sorteo"].iloc[-1])
    )

    ARCHIVO_RESULTADOS.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    resultados.to_csv(
        ARCHIVO_RESULTADOS,
        index=False,
        encoding="utf-8",
    )

    print("\nRESULTADOS")
    print(resultados.to_string(index=False))

    print(
        "\nArchivo generado:",
        ARCHIVO_RESULTADOS,
    )


if __name__ == "__main__":
    generar_comparacion()
