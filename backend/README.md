# Backend API

This backend is a FastAPI application that serves endpoints for interface generation.

## Requirements

- Python 3.11+
- `pip`

## Setup

1. Create and activate a virtual environment:
   - PowerShell:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - Command Prompt:
     ```cmd
     python -m venv .venv
     .\.venv\Scripts\activate.bat
     ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Run

Start the backend server:

```powershell
uvicorn app.main:app --reload --port 8000
```

The API is available at `http://127.0.0.1:8000`.

## Swagger UI

Visit `http://127.0.0.1:8000/docs` for interactive API documentation.

## CORS

The backend allows CORS requests from `http://localhost:5173` so the frontend running with Vite can call the API directly.

## Endpoints

- `GET /` - Root endpoint with service information
- `GET /api/health` - Health check
- `POST /api/generate` - Generate interface (accepts `{"text": "string"}`, returns generated HTML/CSS)

## Example request

```bash
curl -X POST http://127.0.0.1:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"text":"Create a login form"}'
```

---

## LLM Fallback

### Зачем нужен LLM Fallback

Шаблонная библиотека (Jinja2) покрывает стандартные Atomic Design компоненты — кнопки, поля ввода, формы, навигацию.
Для сложных составных виджетов (ImageSlider, Modal, Accordion и будущих типов) заранее написать шаблоны затруднительно или нецелесообразно.
LLM Fallback вызывается автоматически, когда Template Engine встречает тип компонента без шаблонного файла.

### Режимы работы

| `LLM_MODE` | Поведение |
|---|---|
| `mock` (по умолчанию) | Возвращает готовые HTML-заглушки без сетевых вызовов. Быстро, без ключей. |
| `real` | Реальный API-вызов к выбранному провайдеру (GigaChat или OpenAI-совместимый). |

### Получение ключа GigaChat

1. Зарегистрируйтесь на [developers.sber.ru](https://developers.sber.ru).
2. Создайте новый проект в разделе **GigaChat API**.
3. Перейдите в настройки проекта → **Credentials** → скопируйте **Authorization Key** (строка в формате base64).
4. Выберите тип доступа: `GIGACHAT_API_PERS` (личный) или `GIGACHAT_API_CORP` (корпоративный).

### Настройка .env для GigaChat

```env
LLM_MODE=real
LLM_PROVIDER=gigachat
GIGACHAT_AUTH_KEY=<ваш Authorization Key>
GIGACHAT_SCOPE=GIGACHAT_API_PERS
GIGACHAT_MODEL=GigaChat
```

### Заметка про SSL и сертификаты Минцифры

GigaChat API использует TLS-сертификаты, выданные российским удостоверяющим центром Минцифры.
Эти сертификаты не входят в стандартный Python trust store.

В текущем прототипе (`GigaChatLLMClient`) используется `httpx.AsyncClient(verify=False)`.

**Для продакшна** установите сертификат Минцифры в системный truststore или укажите путь явно:
```python
httpx.AsyncClient(verify="/path/to/russiantrustedca.pem")
```
Актуальный файл сертификата доступен на [gosuslugi.ru](https://www.gosuslugi.ru/crt).

### Переключение на OpenAI-совместимый провайдер

Если нужно использовать OpenAI, Qwen, OpenRouter или любой другой OpenAI-совместимый API:

```env
LLM_MODE=real
LLM_PROVIDER=openai_compatible
LLM_API_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o
```

`OpenAICompatibleLLMClient` работает без двухступенчатой OAuth-авторизации — только `Authorization: Bearer {api_key}`.
