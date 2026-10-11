# ==============================================================================
# Dockerfile Multi-Stage: Sistema de Gestión de Trajes Formales
# Optimizado para ligereza, seguridad (usuario no-root) y producción
# ==============================================================================

# Etapa 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /build

# Evitar escritura de archivos .pyc y activar unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Etapa 2: Runner final
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# Crear usuario sin privilegios por seguridad (OWASP Container Hardening)
RUN useradd -m -u 1000 appuser

# Copiar dependencias compiladas desde la etapa builder
COPY --from=builder /root/.local /home/appuser/.local

# Copiar código fuente y asignar permisos al usuario no-root
COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

# Healthcheck para orquestadores (Docker Compose / Kubernetes)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
