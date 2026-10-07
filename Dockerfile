# --- Stage 1: build das dependências ---
# Separado do estágio final pra imagem de produção não carregar
# compiladores/ferramentas de build que só servem pra instalar os pacotes.
FROM python:3.12-slim AS builder

WORKDIR /app

# Dependências de sistema necessárias só para compilar psycopg2 e afins.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia só o requirements.txt primeiro: se o código mudar mas as
# dependências não, o Docker reaproveita esse layer e o build fica
# muito mais rápido.
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt


# --- Stage 2: imagem final, enxuta ---
FROM python:3.12-slim

WORKDIR /app

# libpq-dev não é necessário em runtime, só a lib compartilhada (libpq5).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Usuário não-root — boa prática de segurança, evita rodar a aplicação
# como root dentro do container.
RUN useradd --create-home appuser

# Pacotes Python instalados no stage anterior (modo --user).
COPY --from=builder /root/.local /home/appuser/.local
COPY ./app ./app
COPY alembic.ini .
COPY ./alembic ./alembic

RUN chown -R appuser:appuser /app
USER appuser

ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
