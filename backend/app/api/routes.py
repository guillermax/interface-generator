from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.generate import GenerateRequest, GenerateResponse
from app.schemas.history import ConversationItem, ConversationMessage, FullResult, HistoryItem
from app.services.generator import generate_interface
from app.services.storage import StorageService

router = APIRouter()


@router.post("/generate", response_model=GenerateResponse)
async def generate_interface_endpoint(
    request: GenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await generate_interface(request.text, db, request.conversation_id)
        return GenerateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.get("/history", response_model=list[HistoryItem])
async def get_history(db: AsyncSession = Depends(get_db)):
    storage = StorageService(db)
    return await storage.get_history()


@router.get("/history/{request_id}", response_model=FullResult)
async def get_history_item(request_id: str, db: AsyncSession = Depends(get_db)):
    storage = StorageService(db)
    result = await storage.get_full_result(request_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return result


@router.get("/conversations", response_model=list[ConversationItem])
async def get_conversations(db: AsyncSession = Depends(get_db)):
    storage = StorageService(db)
    return await storage.get_conversations()


@router.get("/conversations/{conversation_id}/messages", response_model=list[ConversationMessage])
async def get_conversation_messages(conversation_id: str, db: AsyncSession = Depends(get_db)):
    storage = StorageService(db)
    return await storage.get_conversation_messages(conversation_id)


@router.delete("/conversations/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    storage = StorageService(db)
    deleted = await storage.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
