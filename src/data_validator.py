
from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data/processed/nuevos_tiempos.csv"


def validar_datos():
    df = pd.read_csv(
        CSV_PATH,
        dtype={"numero": "string"}
    )

    print("\n=== LOTTOLAB CR - DATA QUALITY REPORT ===\n")

    print(f"Total de registros: {len(df)}")

    # 1. Valores nulos
    print("\n1. VALORES NULOS")
    print(df.isna().sum())

    # 2. Sorteos duplicados
    duplicados = df["sorteo"].duplicated().sum()
    print(f"\n2. SORTEOS DUPLICADOS: {duplicados}")

    # 3. Validacion de numeros
    formato_valido = df["numero"].str.fullmatch(r"\d{2}").fillna(False)
    rango_valido = pd.to_numeric(
        df["numero"], errors="coerce"
    ).between(0, 99)

    numeros_invalidos = (~(formato_valido & rango_valido)).sum()
    print(f"\n3. NUMEROS INVALIDOS: {numeros_invalidos}")

    # 4. Continuidad de sorteos
    ids = set(df["sorteo"].dropna().astype(int))
    esperados = set(range(min(ids), max(ids) + 1))
    faltantes = sorted(esperados - ids)

    print(f"\n4. IDENTIFICADORES FALTANTES: {len(faltantes)}")
    print(f"Primeros faltantes: {faltantes[:20]}")

    # 5. Distribucion anual
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    print(f"\n5. FECHAS INVALIDAS: {df['fecha'].isna().sum()}")

    print("\n6. SORTEOS POR ANO")
    print(df.groupby(df["fecha"].dt.year).size())

    # 7. Dias sin registros
    fechas = df["fecha"].dropna().dt.normalize()
    calendario = pd.date_range(fechas.min(), fechas.max())
    dias_sin_sorteos = calendario.difference(
        pd.DatetimeIndex(fechas.unique())
    )

    print(f"\n7. DIAS SIN REGISTROS: {len(dias_sin_sorteos)}")
    print("Primeros dias sin registros:")
    print(dias_sin_sorteos[:20].strftime("%Y-%m-%d").tolist())

    print("\n=== FIN DEL REPORTE ===")


if __name__ == "__main__":
    validar_datos()
