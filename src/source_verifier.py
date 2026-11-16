
from pathlib import Path
from datetime import datetime
import random
import re

import pandas as pd
import pymupdf


BASE_DIR = Path(__file__).resolve().parent.parent

PDF_PATH = BASE_DIR / "data/raw/nuevos_tiempos_2019_2025.pdf"
CSV_PATH = BASE_DIR / "data/processed/nuevos_tiempos.csv"

SAMPLE_SIZE = 100
RANDOM_SEED = 42

PATRON = re.compile(
    r"^\s*(\d{5,6})\s+"
    r"(\d{2}/\d{2}/\d{4})\s+"
    r"(\d{1,2}:\d{2}:\d{2})\s*"
    r"(am|pm)\s+"
    r"(\d{1,2})\s+"
    r"(.+)$",
    re.IGNORECASE,
)


def leer_fuente_pdf():
    """Lee los sorteos directamente del documento original."""
    registros = {}

    with pymupdf.open(PDF_PATH) as documento:
        for pagina in documento:
            texto = pagina.get_text("text", sort=True)

            for linea in texto.splitlines():
                coincidencia = PATRON.match(linea)

                if not coincidencia:
                    continue

                sorteo, fecha, hora, periodo, numero, descripcion = (
                    coincidencia.groups()
                )

                sorteo = int(sorteo)

                if sorteo in registros:
                    raise ValueError(
                        f"Sorteo duplicado en PDF: {sorteo}"
                    )

                fecha_normalizada = datetime.strptime(
                    fecha, "%d/%m/%Y"
                ).date().isoformat()

                hora_normalizada = datetime.strptime(
                    f"{hora} {periodo.upper()}",
                    "%I:%M:%S %p",
                ).strftime("%H:%M:%S")

                registros[sorteo] = {
                    "fecha": fecha_normalizada,
                    "hora": hora_normalizada,
                    "numero": numero.zfill(2),
                    "descripcion": descripcion.strip(),
                }

    return registros


def verificar_fuente():
    print("\n=== LOTTOLAB CR - SOURCE VERIFICATION ===\n")

    # Leer CSV preservando los ceros iniciales.
    df = pd.read_csv(
        CSV_PATH,
        dtype={"numero": "string"},
        keep_default_na=False,
    )

    if df["sorteo"].duplicated().any():
        raise ValueError("El CSV contiene sorteos duplicados.")

    # Obtener los registros originales del PDF.
    registros_pdf = leer_fuente_pdf()

    if not registros_pdf:
        raise ValueError("No se encontraron sorteos en el PDF.")

    ids_csv = set(df["sorteo"].astype(int))
    ids_pdf = set(registros_pdf)

    faltantes_csv = sorted(ids_pdf - ids_csv)
    extras_csv = sorted(ids_csv - ids_pdf)

    print(f"Registros en PDF: {len(ids_pdf)}")
    print(f"Registros en CSV: {len(ids_csv)}")
    print(f"Faltantes en CSV: {len(faltantes_csv)}")
    print(f"Extras en CSV: {len(extras_csv)}")

    if faltantes_csv:
        print(f"Primeros faltantes: {faltantes_csv[:10]}")

    if extras_csv:
        print(f"Primeros extras: {extras_csv[:10]}")

    # Muestra aleatoria reproducible.
    ids_comunes = sorted(ids_pdf & ids_csv)

    random.seed(RANDOM_SEED)
    muestra = random.sample(
        ids_comunes,
        min(SAMPLE_SIZE, len(ids_comunes)),
    )

    csv_por_sorteo = df.set_index("sorteo")
    diferencias = []

    campos = ["fecha", "hora", "numero", "descripcion"]

    for sorteo in muestra:
        registro_pdf = registros_pdf[sorteo]
        registro_csv = csv_por_sorteo.loc[sorteo]

        for campo in campos:
            valor_pdf = str(registro_pdf[campo])
            valor_csv = str(registro_csv[campo])

            if valor_pdf != valor_csv:
                diferencias.append({
                    "sorteo": sorteo,
                    "campo": campo,
                    "valor_pdf": valor_pdf,
                    "valor_csv": valor_csv,
                })

    print(f"\nSorteos comparados: {len(muestra)}")
    print(f"Diferencias encontradas: {len(diferencias)}")

    if diferencias:
        print("\nPrimeras diferencias:")
        for diferencia in diferencias[:10]:
            print(diferencia)

    if not faltantes_csv and not extras_csv and not diferencias:
        print("\nRESULTADO: VERIFICACION SATISFACTORIA")
    else:
        print("\nRESULTADO: SE REQUIERE REVISION")

    print("\n=== FIN DE LA VERIFICACION ===")


if __name__ == "__main__":
    verificar_fuente()
