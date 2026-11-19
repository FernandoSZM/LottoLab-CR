
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


CARACTERISTICAS = [
    "dia_semana",
    "mes",
    "horario",
    "numero_anterior",
    "numero_hace_2",
    "numero_hace_3",
    "terminacion_anterior",
    "terminacion_hace_2",
    "terminacion_hace_3",
]



def crear_modelo_ml(c=0.01):
    """
    Crea un modelo multiclase regularizado
    para estimar probabilidades de 00 a 99.
    """

    preprocesador = ColumnTransformer(
        transformers=[
            (
                "categoricas",
                OneHotEncoder(
                    handle_unknown="ignore"
                ),
                CARACTERISTICAS,
            )
        ]
    )

    clasificador = LogisticRegression(
        C=c,
        l1_ratio=0,
        max_iter=1000,
        solver="lbfgs",
    )

    return Pipeline(
        steps=[
            ("preprocesador", preprocesador),
            ("clasificador", clasificador),
        ]
    )


def entrenar_modelo_ml(datos, c=0.01):
    """
    Entrena el modelo con las características
    y el número ganador de cada sorteo.
    """

    x = datos[CARACTERISTICAS]
    y = datos["numero"]

    modelo = crear_modelo_ml(c=c)
    modelo.fit(x, y)

    return modelo


def obtener_probabilidades(modelo, caracteristicas):
    """
    Devuelve probabilidades ordenadas
    para los números 00 a 99.
    """

    probabilidades = modelo.predict_proba(
        caracteristicas[CARACTERISTICAS]
    )

    clases = modelo.named_steps[
        "clasificador"
    ].classes_

    resultado = np.zeros(
        (len(caracteristicas), 100),
        dtype=float,
    )

    for indice, numero in enumerate(clases):
        resultado[:, int(numero)] = (
            probabilidades[:, indice]
        )

    return resultado
