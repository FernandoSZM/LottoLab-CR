# LottoLab CR

Aplicación Streamlit para explorar el historial de Nuevos Tiempos de Costa Rica,
revisar su calidad y consultar estimaciones experimentales.

## Ejecutar

1. Instala las dependencias del proyecto:

   ```bash
   python -m pip install -r requirements.txt
   ```

2. Configura `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y `DB_PASSWORD` en un
   archivo `.env` en la raíz del proyecto. No compartas ni subas ese archivo.
3. Inicia la aplicación desde la raíz:

   ```bash
   streamlit run dashboard/app.py
   ```

La pantalla Inicio concentra el predictor. Si el historial disponible tiene
más de siete días, la aplicación identifica la consulta como demostración y
usa como fecha inicial el día posterior al último registro. Las frecuencias y
estimaciones no demuestran una ventaja predictiva.

## Pruebas

```bash
python -m pytest -q
```
