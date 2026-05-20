from dotenv import load_dotenv
load_dotenv()  # загружает .env до любого импорта, использующего DATABASE_URL

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

app = FastAPI(title='Interface Generator API', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix='/api')

@app.get('/')
async def root() -> dict[str, str]:
    return {'message': 'Interface Generator API', 'version': '1.0.0'}
