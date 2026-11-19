
import numpy as np
import pandas as pd

from src.prediction.bayesian import ModeloBayesiano
from src.prediction.features import (
    crear_caracteristicas,
    crear_caracteristicas_futuras,
)
from src.prediction.ml_model import (
    entrenar_modelo_ml,
    obtener_probabilidades,
)
from src.prediction.tree_model import (
    entrenar_modelo_arboles,
    obtener_probabilidades_arboles,
)


MODELOS_DISPONIBLES = (
    "Bayesiano",
    "Regresión logística",
    "Árboles potenciados",
    "Uniforme",
)


def generar_prediccion(
    historial,
    fecha_objetivo,
    hora_objetivo,
    modelo_nombre="Regresión logística",
    cantidad=5,
):
    """
    Genera una distribución experimental para
    un sorteo posterior al historial disponible.

    No modifica la base de datos.
    """

    if modelo_nombre not in MODELOS_DISPONIBLES:
        raise ValueError("Modelo no reconocido.")

    if cantidad not in (3, 5, 10):
        raise ValueError(
            "El ranking debe contener 3, 5 o 10 números."
        )

    datos = historial.sort_values(
        ["fecha", "hora", "sorteo"]
    ).reset_index(drop=True)

    # Validamos el objetivo para todos los modelos.
    entrada = crear_caracteristicas_futuras(
        historial=datos,
        fecha_objetivo=fecha_objetivo,
        hora_objetivo=hora_objetivo,
    )

    if modelo_nombre == "Uniforme":
        probabilidades = np.full(100, 0.01)

    elif modelo_nombre == "Bayesiano":
        modelo = ModeloBayesiano(alpha=1.0)
        modelo.actualizar(datos["numero"])

        probabilidades = (
            modelo.probabilidades()
            .to_numpy(dtype=float)
        )

    else:
        entrenamiento = crear_caracteristicas(datos)

        if modelo_nombre == "Regresión logística":
            modelo = entrenar_modelo_ml(
                entrenamiento,
                c=0.00001,
            )
            probabilidades = obtener_probabilidades(
                modelo,
                entrada,
            )[0]

        else:
            modelo = entrenar_modelo_arboles(
                entrenamiento
            )
            probabilidades = (
                obtener_probabilidades_arboles(
                    modelo,
                    entrada,
                )[0]
            )

    probabilidades = np.asarray(
        probabilidades,
        dtype=float,
    )

    if probabilidades.shape != (100,):
        raise ValueError(
            "El modelo no devolvió 100 probabilidades."
        )

    if not np.all(np.isfinite(probabilidades)):
        raise ValueError(
            "El modelo devolvió probabilidades no finitas."
        )

    if np.any(probabilidades < 0):
        raise ValueError(
            "El modelo devolvió probabilidades negativas."
        )

    if not np.isclose(
        probabilidades.sum(),
        1.0,
        rtol=0,
        atol=1e-8,
    ):
        raise ValueError(
            "Las probabilidades no suman 1."
        )

    ranking = pd.DataFrame({
        "Número": [f"{n:02d}" for n in range(100)],
        "Probabilidad estimada (%)": probabilidades * 100,
    })

    ranking = ranking.sort_values(
        ["Probabilidad estimada (%)", "Número"],
        ascending=[False, True],
    ).head(cantidad).reset_index(drop=True)

    return {
        "modelo": modelo_nombre,
        "fecha_objetivo": str(
            pd.Timestamp(fecha_objetivo).date()
        ),
        "hora_objetivo": str(hora_objetivo)[:5],
        "sorteos_entrenamiento": len(datos),
        "probabilidades": probabilidades,
        "ranking": ranking,
    }
