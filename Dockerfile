# ==========================================
# STAGE 1: Builder
# ==========================================
FROM python:3.14-slim AS builder

WORKDIR /app

# Verhindert, dass Python .pyc Dateien schreibt und puffert die Logs nicht
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# System-Abhängigkeiten installieren (falls Pakete kompiliert werden müssen)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Virtuelle Umgebung im Container erstellen
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================
# STAGE 2: Final Runtime
# ==========================================
FROM python:3.14-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Kopiere nur die fertige virtuelle Umgebung aus dem Builder
COPY --from=builder /opt/venv /opt/venv

# Kopiere den eigentlichen Quellcode
COPY . .

# Erstelle einen Non-Root User aus Sicherheitsgründen
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh appuser && \
    chown -R appuser:appgroup /app

USER appuser

# Port freigeben (Standard für FastAPI/Uvicorn)
EXPOSE 8000

# Startbefehl für die Anwendung
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
