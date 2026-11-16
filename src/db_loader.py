
from pathlib import Path
import os

import pandas as pd
import psycopg
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data/processed/nuevos_tiempos.csv"

load_dotenv(BASE_DIR / ".env")


def cargar_datos():
    print("\n=== LOTTOLAB CR - DATABASE LOADER ===\n")

    df = pd.read_csv(
        CSV_PATH,
        dtype={"numero": "string"},
        keep_default_na=False,
    )

    print(f"Registros leidos del CSV: {len(df)}")

    registros = [
        (
            int(fila.sorteo),
            fila.fecha,
            fila.hora,
            str(fila.numero),
            fila.descripcion,
        )
        for fila in df.itertuples(index=False)
    ]

    conexion = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    if any(not valor for valor in conexion.values()):
        raise ValueError(
            "Faltan variables de conexion en el archivo .env"
        )

    consulta = """
        INSERT INTO draws (
            draw_id,
            draw_date,
            draw_time,
            winning_number,
            description
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (draw_id) DO NOTHING;
    """

    with psycopg.connect(**conexion) as conn:
        with conn.cursor() as cursor:
            cursor.executemany(consulta, registros)

            cursor.execute("SELECT COUNT(*) FROM draws;")
            total = cursor.fetchone()[0]

    print(f"Registros enviados: {len(registros)}")
    print(f"Total de registros en PostgreSQL: {total}")
    print("\nCarga finalizada correctamente.")


if __name__ == "__main__":
    cargar_datos()
