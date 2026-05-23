# Interface Generator

Прототип системы генерации HTML/CSS-интерфейсов по текстовому описанию на русском языке.
Пользователь пишет «форма входа с email и паролем» — система возвращает готовый HTML с CSS, WCAG-валидацией и сохраняет результат в историю.
Архитектура: NLP (rule-based) → Abstract Markup Interface → Template Engine / LLM Fallback → CSS Builder → Validator.

---

## Запуск через Docker Compose (production)

```bash
git clone <repo-url> && cd interface-generator
cp .env.docker.example .env.docker        # при необходимости измени пароль БД
docker compose --env-file .env.docker up --build -d
# Открой http://localhost
```

Три сервиса поднимаются как единая система: `db` (PostgreSQL 15) → `backend` (FastAPI + alembic) → `nginx` (статика React + reverse proxy).
БД не пробрасывается наружу — изолирована в Docker-сети.

---

## Запуск в режиме разработки

**Backend** (требует запущенный PostgreSQL):
```bash
cd backend
python -m venv .venv && .\.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev   # http://localhost:5173
```

---

## Структура проекта

```
interface-generator/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI роуты
│   │   ├── db/           # SQLAlchemy модели, сессия
│   │   ├── schemas/      # Pydantic схемы
│   │   ├── services/     # NLP, AMI, Template, CSS, Validator, LLM Client
│   │   └── templates/    # Jinja2 шаблоны (Atomic Design: atoms/molecules/organisms)
│   ├── alembic/          # Миграции БД
│   ├── tests/            # 76 тестов (pytest)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # ChatInterface, PreviewPanel, ChatHistory, ChatInput
│   │   └── api.ts        # HTTP-клиент (VITE_API_BASE_URL)
│   ├── Dockerfile
│   └── package.json
├── nginx/
│   └── nginx.conf        # Reverse proxy /api/ + SPA fallback
├── docker-compose.yml
├── .env.docker.example
└── README.md
```

---

## Технологии

| Слой | Технология | Версия |
|---|---|---|
| Frontend | React + TypeScript + Vite | React 19, Vite 8 |
| Стили | Tailwind CSS | 4.x |
| Backend | FastAPI + Uvicorn | 0.104 / 0.24 |
| ORM | SQLAlchemy async + asyncpg | 2.0 / 0.31 |
| Миграции | Alembic + psycopg2-binary | 1.13 / 2.9 |
| БД | PostgreSQL | 15-alpine |
| LLM | GigaChat / OpenAI-compatible (mock default) | — |
| Прокси | nginx | alpine |
| Тесты | pytest + pytest-asyncio + pytest-httpx | 76 тестов |
