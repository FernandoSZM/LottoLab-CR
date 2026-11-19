
import pandas as pd


class ModeloBayesiano:
    """
    Modelo probabilístico para los números 00-99.

    Utiliza una distribución Dirichlet simétrica
    para estimar probabilidades posteriores.
    """

    def __init__(self, alpha=1.0):
        if alpha <= 0:
            raise ValueError("Alpha debe ser positivo.")

        self.alpha = alpha
        self.numeros = [f"{n:02d}" for n in range(100)]
        self.conteos = pd.Series(
            0, index=self.numeros, dtype="int64"
        )
        self.total = 0

    def actualizar(self, nuevos_numeros):
        """Incorpora nuevos resultados al modelo."""

        datos = pd.Series(
            list(nuevos_numeros), dtype="string"
        )

        if datos.isna().any():
            raise ValueError("Hay números nulos.")

        if not datos.isin(self.numeros).all():
            raise ValueError(
                "Los números deben estar entre 00 y 99."
            )

        frecuencias = datos.value_counts()

        self.conteos = self.conteos.add(
            frecuencias, fill_value=0
        ).astype("int64")

        self.total += len(datos)

    def probabilidades(self):
        """Devuelve las probabilidades estimadas."""

        estimaciones = (
            (self.conteos + self.alpha)
            / (self.total + 100 * self.alpha)
        )

        return estimaciones

    def ranking(self, cantidad=5):
        """Devuelve los números con mayor estimación."""

        if cantidad not in (3, 5, 10):
            raise ValueError(
                "La cantidad debe ser 3, 5 o 10."
            )

        probabilidades = self.probabilidades()

        resultado = pd.DataFrame({
            "Número": probabilidades.index,
            "Probabilidad estimada (%)": (
                probabilidades.to_numpy() * 100
            ),
        })

        return (
            resultado.sort_values(
                ["Probabilidad estimada (%)", "Número"],
                ascending=[False, True],
            )
            .head(cantidad)
            .reset_index(drop=True)
        )
