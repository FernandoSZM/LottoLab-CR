
from pathlib import Path
from datetime import datetime
import re

import pymupdf
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = BASE_DIR / "data/raw/nuevos_tiempos_2019_2025.pdf"
OUTPUT_PATH = BASE_DIR / "data/processed/nuevos_tiempos.csv"

PATRON = re.compile(
    r"^\s*(\d{5,6})\s+"
    r"(\d{2}/\d{2}/\d{4})\s+"
    r"(\d{1,2}:\d{2}:\d{2})\s*"
    r"(am|pm)\s+"
    r"(\d{1,2})\s+"
    r"(.+)$",
    re.IGNORECASE,
)


def extraer_resultados():
    registros = []
    lineas_no_reconocidas = []

    with pymupdf.open(PDF_PATH) as documento:
        print(f"Procesando {len(documento)} paginas...")

        for pagina_num, pagina in enumerate(documento, start=1):
            texto = pagina.get_text("text", sort=True)

            for linea in texto.splitlines():
                coincidencia = PATRON.match(linea)

                if not coincidencia:
                    if re.match(r"^\s*\d{5,6}\s+\d{2}/\d{2}/\d{4}", linea):
                        lineas_no_reconocidas.append((pagina_num, linea))
                    continue

                sorteo, fecha, hora, periodo, numero, descripcion = (
                    coincidencia.groups()
                )

                hora_24 = datetime.strptime(
                    f"{hora} {periodo.upper()}",
                    "%I:%M:%S %p"
                ).strftime("%H:%M:%S")

                registros.append({
                    "sorteo": int(sorteo),
                    "fecha": datetime.strptime(
                        fecha, "%d/%m/%Y"
                    ).date().isoformat(),
                    "hora": hora_24,
                    "numero": numero.zfill(2),
                    "descripcion": descripcion.strip(),
                })

    if lineas_no_reconocidas:
        print("Se encontraron posibles sorteos sin procesar:")
        for pagina, linea in lineas_no_reconocidas[:10]:
            print(f"Pagina {pagina}: {linea}")
        raise ValueError("Revisar registros no reconocidos.")

    if not registros:
        raise ValueError("No se encontraron resultados en el PDF.")

    df = pd.DataFrame(registros)

    if df["sorteo"].duplicated().any():
        raise ValueError("Se encontraron sorteos duplicados.")

    if not df["numero"].str.fullmatch(r"\d{2}").all():
        raise ValueError("Existen numeros con formato incorrecto.")

    if not df["numero"].astype(int).between(0, 99).all():
        raise ValueError("Existen numeros fuera del rango 00-99.")

    df = df.sort_values(["fecha", "hora", "sorteo"])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    print(f"Registros extraidos: {len(df)}")
    print(f"Primer sorteo: {df['fecha'].min()}")
    print(f"Ultimo sorteo: {df['fecha'].max()}")
    print(f"Archivo generado: {OUTPUT_PATH}")

    print("\nPrimeros registros:")
    print(df.head().to_string(index=False))


if __name__ == "__main__":
    extraer_resultados()
