# Interface Generator

Прототип системы генерации HTML/CSS-интерфейсов по текстовому описанию на русском языке.
Пользователь пишет «форма входа с email и паролем» — система возвращает готовый HTML с CSS, сохраняет результат в историю и группирует запросы в чаты (conversations).

**Архитектура:** NLP (rule-based) → Abstract Markup Interface → Template Engine / LLM Fallback → CSS Builder → Validator → PostgreSQL.

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

## Что умеет система

### Поддерживаемые компоненты

| Тип запроса | Что генерируется |
|---|---|
| `форма входа` | LoginForm с полями email, password, кнопкой |
| `форма регистрации` | RegistrationForm с confirm-password |
| `карточка товара` | ProductCard с изображением и ценой |
| `навигационное меню` | Nav с NavItem-ссылками |
| `поисковая строка` | SearchBar с кнопкой поиска |
| `слайдер` / `карусель` | ImageSlider с тремя слайдами и dot-навигацией |
| `модальное окно` | Modal с заголовком и кнопкой закрытия |
| `аккордеон` | Accordion с секциями |

### Страничные паттерны (полные страницы)

| Ключевое слово | Структура страницы |
|---|---|
| `лендинг` | Header + Nav + Hero + Features + Footer |
| `интернет-магазин` | Header + Nav + SearchBar + CardGrid + Footer |
| `блог` | Header + Nav + Sidebar + Heading + Text + Footer |
| `админ-панель` / `dashboard` | Header + Nav + Sidebar + CardGrid + Footer |

Паттерны **накопительные** — «лендинг со слайдером» добавляет ImageSlider между Features и Footer.

---

## API

| Метод | Путь | Описание |
|---|---|---|
| `POST` | `/api/generate` | Генерация интерфейса по тексту |
| `GET` | `/api/conversations` | Список чатов |
| `GET` | `/api/conversations/{id}/messages` | Сообщения чата |
| `DELETE` | `/api/conversations/{id}` | Удалить чат (cascade) |
| `GET` | `/api/history` | Все запросы (плоский список) |
| `GET` | `/api/history/{id}` | Полный результат запроса |
| `GET` | `/api/health` | Health check |

### Пример запроса

```bash
curl -X POST http://localhost/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "форма входа с email и паролем"}'
```

```json
{
  "request_id": "...",
  "conversation_id": "...",
  "html": "<!DOCTYPE html>...",
  "css": "* { box-sizing: border-box; }...",
  "generation_time_ms": 12
}
```

---

## Структура проекта

```
interface-generator/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI роуты
│   │   ├── db/           # SQLAlchemy модели (Request, Conversation, GenerationResult, ComponentLog)
│   │   ├── schemas/      # Pydantic схемы
│   │   ├── services/     # NLP, AMIBuilder, TemplateEngine, CSSBuilder, Validator, LLM Client, StorageService
│   │   └── templates/    # Jinja2 шаблоны (Atomic Design: atoms / molecules / organisms)
│   ├── alembic/          # Миграции БД
│   ├── tests/            # 85 тестов (pytest-asyncio)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # ChatInterface, PreviewPanel, ChatHistory, ChatInput
│   │   ├── api.ts        # HTTP-клиент (VITE_API_BASE_URL)
│   │   └── types.ts      # TypeScript-типы
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
| Frontend | React + TypeScript + Vite | React 19, Vite 6 |
| Стили | Tailwind CSS | 4.x |
| Backend | FastAPI + Uvicorn | 0.104 / 0.24 |
| ORM | SQLAlchemy async + asyncpg | 2.0 / 0.31 |
| Миграции | Alembic + psycopg2-binary | 1.13 / 2.9 |
| БД | PostgreSQL | 15-alpine |
| LLM | GigaChat / OpenAI-compatible (mock по умолчанию) | — |
| Прокси | nginx | alpine |
| Тесты | pytest + pytest-asyncio | 85 тестов |
