# ==========================================
# STAGE 1: Builder
# ==========================================
FROM python:3.14-rc-slim AS builder

# Install uv securely from astral-sh
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1

# Install dependencies using uv to a virtual environment
COPY pyproject.toml .
RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv .

# ==========================================
# STAGE 2: Final Runtime
# ==========================================
FROM python:3.14-rc-slim AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv
COPY src/ /app/src/
COPY wsgi.py /app/

# Create non-root user for maximum security
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh appuser && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Use Gunicorn (WSGI server) for production-grade Flask deployments
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "wsgi:app"]