
import numpy as np

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

from src.prediction.ml_model import CARACTERISTICAS


def crear_modelo_arboles():
    """
    Crea un modelo de árboles potenciados
    con variables categóricas.
    """

    preprocesador = ColumnTransformer(
        transformers=[
            (
                "categoricas",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=np.nan,
                ),
                CARACTERISTICAS,
            )
        ]
    )

    clasificador = HistGradientBoostingClassifier(
        learning_rate=0.03,
        max_iter=100,
        max_leaf_nodes=7,
        min_samples_leaf=50,
        l2_regularization=10.0,
        categorical_features=list(
            range(len(CARACTERISTICAS))
        ),
        random_state=42,
    )

    return Pipeline(
        steps=[
            ("preprocesador", preprocesador),
            ("clasificador", clasificador),
        ]
    )


def entrenar_modelo_arboles(datos):
    """
    Entrena el modelo utilizando los
    resultados históricos disponibles.
    """

    modelo = crear_modelo_arboles()

    modelo.fit(
        datos[CARACTERISTICAS],
        datos["numero"],
    )

    return modelo


def obtener_probabilidades_arboles(
    modelo,
    caracteristicas,
):
    """
    Devuelve probabilidades para
    los 100 números posibles.
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
