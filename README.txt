Proyecto Dash listo para subir a GitHub y desplegar en Render.

Archivos:
- app.py: código completo del tablero.
- salesmonthly.csv: base de datos.
- requirements.txt: librerías necesarias.
- Procfile: comando para Render/Heroku.

En Render:
Build Command:
pip install -r requirements.txt

Start Command:
gunicorn app:server
