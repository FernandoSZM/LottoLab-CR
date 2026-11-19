
from pathlib import Path
import os

import pandas as pd
import psycopg
import streamlit as st
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


@st.cache_data(ttl=300)
def cargar_sorteos():
    """Obtiene los sorteos históricos desde PostgreSQL."""

    conexion = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    with psycopg.connect(**conexion) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    draw_id,
                    draw_date,
                    draw_time,
                    winning_number
                FROM draws
                ORDER BY draw_date, draw_time, draw_id
            """)

            registros = cursor.fetchall()

    columnas = ["sorteo", "fecha", "hora", "numero"]

    df = pd.DataFrame(registros, columns=columnas)

    df["fecha"] = pd.to_datetime(df["fecha"])
    df["anio"] = df["fecha"].dt.year

    return df


@st.cache_data(ttl=300)
def cargar_ultimo_sorteo():
    """Obtiene el último sorteo registrado en PostgreSQL."""

    conexion = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    with psycopg.connect(**conexion) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    draw_id,
                    draw_date,
                    draw_time,
                    winning_number
                FROM draws
                ORDER BY draw_date DESC,
                         draw_time DESC,
                         draw_id DESC
                LIMIT 1
            """)

            registro = cursor.fetchone()

    if registro is None:
        return None

    return {
        "sorteo": registro[0],
        "fecha": registro[1],
        "hora": registro[2],
        "numero": registro[3],
    }
