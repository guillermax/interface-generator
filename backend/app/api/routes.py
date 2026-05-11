from fastapi import APIRouter

from app.schemas.generate import GenerateRequest, GenerateResponse
from app.services.generator import generate_interface

router = APIRouter()

@router.post('/generate', response_model=GenerateResponse)
async def generate_interface_endpoint(request: GenerateRequest) -> GenerateResponse:
    result = generate_interface(request.text)
    
    # Вытащить ami из результата для отдельной передачи
    ami = result.pop('ami')
    
    response = GenerateResponse(
        **result,
        ami=ami
    )
    return response

@router.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}
