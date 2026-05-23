# ── Stage 1: builder ──────────────────────────────────────────────────────────
# Используем виртуальное окружение /venv вместо pip install --user.
# Это надёжнее: /venv/bin в PATH работает одинаково для root и appuser,
# не нужны PYTHONPATH хаки и проверки прав на /root/.
FROM python:3.11-slim AS builder

# Системные зависимости нужны только на этапе сборки (gcc для C-расширений)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Создаём venv и устанавливаем зависимости отдельным слоем —
# этот слой кешируется пока requirements.txt не меняется
COPY requirements.txt .
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Только runtime-зависимость: libpq5 нужна asyncpg и psycopg2 в рантайме
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Копируем venv из builder — всё в одном месте, без мусора build toolchain
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

WORKDIR /app

# Копируем только prod-артефакты (тесты, venv, .env* исключены .dockerignore)
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Непривилегированный пользователь
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup --no-create-home appuser
USER appuser

EXPOSE 8000

# alembic читает DATABASE_URL из переменной окружения (load_dotenv не найдёт .env
# в контейнере — он не копируется, .dockerignore исключает .env*)
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2"]
