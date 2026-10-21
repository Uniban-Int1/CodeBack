FROM python:3.11-slim

WORKDIR /code

# Instalar dependencias del sistema mínimas necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias con wheels binarios para Python 3.11
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Comando de arranque para Render usando la variable $PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
