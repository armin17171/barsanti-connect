FROM python:3.12-slim

# Evita file .pyc e output bufferizzato
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dipendenze prima del codice per sfruttare la cache dei layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Codice applicativo
COPY app ./app

# Cartella dei media caricati (montata come volume in compose)
RUN mkdir -p /app/media

EXPOSE 8000

# entrypoint: attende il DB, crea tabelle + admin, avvia uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
