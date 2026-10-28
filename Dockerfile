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

# Migraciones + arranque. "Pre-Deploy Command" está bloqueado en el plan free de
# Render, así que las migraciones van aquí: corren en cada arranque del contenedor,
# son idempotentes (Alembic no repite lo ya aplicado), así que no hace daño correrlas
# también en cada reinicio por inactividad del plan free.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
