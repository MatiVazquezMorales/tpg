FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY docs/backend/ ./backend/
COPY docs/frontend/ ./frontend/

ENV PYTHONPATH=/app/backend

EXPOSE 8000

# Para producción, usar sin --reload
CMD ["uvicorn", "main.main:app", "--host", "0.0.0.0", "--port", "8000"]
