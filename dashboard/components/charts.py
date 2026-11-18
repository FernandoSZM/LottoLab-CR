
import plotly.express as px


def grafico_frecuencias(frecuencias, total_sorteos, vista):
    """Construye el gráfico de frecuencias según la vista elegida."""

    if vista == "10 más frecuentes":
        datos = frecuencias.nlargest(10, "Apariciones")
    elif vista == "10 menos frecuentes":
        datos = frecuencias.nsmallest(10, "Apariciones")
    else:
        datos = frecuencias.sort_values("Número")

    fig = px.bar(
        datos,
        x="Número",
        y="Apariciones",
        title=f"Frecuencia de números — {vista}",
        labels={
            "Número": "Número ganador",
            "Apariciones": "Cantidad de apariciones",
        },
    )

    frecuencia_esperada = total_sorteos / 100

    fig.add_hline(
        y=frecuencia_esperada,
        line_dash="dash",
        line_color="#F59E0B",
        annotation_text=f"Esperada: {frecuencia_esperada:.2f}",
        annotation_position="top right",
    )

    fig.update_layout(
        height=480,
        xaxis=dict(type="category"),
        margin=dict(l=20, r=20, t=60, b=20),
    )

    return fig
