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
