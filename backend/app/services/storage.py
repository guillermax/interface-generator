"""
StorageService — сохранение истории запросов и результатов генерации в PostgreSQL.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ComponentLog, Conversation, GenerationResult, Request


class StorageService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ------------------------------------------------------------------ write

    async def create_conversation(self, title: str) -> uuid.UUID:
        """INSERT conversation, returns conversation_id."""
        conv = Conversation(title=title[:100])
        self._db.add(conv)
        await self._db.flush()
        await self._db.commit()
        return conv.conversation_id

    async def save_request(self, text: str, conversation_id: uuid.UUID | None = None) -> uuid.UUID:
        """INSERT request со статусом pending, возвращает request_id."""
        req = Request(text=text, status="pending", conversation_id=conversation_id)
        self._db.add(req)
        await self._db.flush()
        await self._db.commit()
        return req.request_id

    async def save_result(
        self,
        request_id: uuid.UUID,
        html: str,
        css: str,
        ami_graph: dict,
        generation_time_ms: int,
        nlp_result: list[dict] | None,
        components_log: list[tuple] | None = None,
    ) -> uuid.UUID:
        """
        В одной транзакции:
          1. INSERT в generation_results
          2. INSERT в components_log (из списка tuples, переданного Template Engine)
          3. UPDATE requests: status='done', nlp_result=<данные NLP>

        components_log: list of (component_type, generation_method, llm_attempts)
        """
        result = GenerationResult(
            request_id=request_id,
            html=html,
            css=css,
            ami_graph=ami_graph,
            generation_time_ms=generation_time_ms,
        )
        self._db.add(result)
        await self._db.flush()

        for component_type, generation_method, llm_attempts in (components_log or []):
            log = ComponentLog(
                result_id=result.result_id,
                component_type=component_type,
                generation_method=generation_method,
                llm_attempts=llm_attempts,
            )
            self._db.add(log)

        await self._db.execute(
            update(Request)
            .where(Request.request_id == request_id)
            .values(status="done", nlp_result=nlp_result)
        )
        await self._db.commit()
        return result.result_id

    async def update_conversation_timestamp(self, conversation_id: uuid.UUID) -> None:
        """UPDATE conversations.updated_at = now() after a new request is added."""
        await self._db.execute(
            update(Conversation)
            .where(Conversation.conversation_id == conversation_id)
            .values(updated_at=datetime.now(timezone.utc).replace(tzinfo=None))
        )
        await self._db.commit()

    async def mark_error(self, request_id: uuid.UUID, error_message: str) -> None:
        """UPDATE requests: status='error'."""
        await self._db.execute(
            update(Request)
            .where(Request.request_id == request_id)
            .values(status="error")
        )
        await self._db.commit()

    # ------------------------------------------------------------------ read

    async def get_conversations(self, limit: int = 50) -> list[dict]:
        """SELECT conversations with message count, ordered by updated_at DESC."""
        rows = await self._db.execute(
            select(
                Conversation,
                func.count(Request.request_id).label("message_count"),
            )
            .outerjoin(Request, Request.conversation_id == Conversation.conversation_id)
            .group_by(Conversation.conversation_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
        return [
            {
                "conversation_id": str(conv.conversation_id),
                "title": conv.title,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "message_count": count,
            }
            for conv, count in rows
        ]

    async def get_conversation_messages(self, conversation_id: str) -> list[dict]:
        """Return all requests + results for a conversation, ordered by time."""
        try:
            cid = uuid.UUID(conversation_id)
        except ValueError:
            return []

        rows = await self._db.execute(
            select(Request)
            .where(Request.conversation_id == cid)
            .order_by(Request.created_at.asc())
        )
        requests = rows.scalars().all()

        messages = []
        for req in requests:
            result_row = await self._db.execute(
                select(GenerationResult)
                .where(GenerationResult.request_id == req.request_id)
                .order_by(GenerationResult.generated_at.desc())
                .limit(1)
            )
            result = result_row.scalar_one_or_none()
            messages.append({
                "request_id": str(req.request_id),
                "text": req.text,
                "created_at": req.created_at.isoformat(),
                "status": req.status,
                "html": result.html if result else None,
                "css": result.css if result else None,
                "generation_time_ms": result.generation_time_ms if result else None,
            })
        return messages

    async def delete_conversation(self, conversation_id: str) -> bool:
        """DELETE conversation (cascades to requests → results → logs). Returns True if found."""
        try:
            cid = uuid.UUID(conversation_id)
        except ValueError:
            return False

        row = await self._db.execute(
            select(Conversation).where(Conversation.conversation_id == cid)
        )
        conv = row.scalar_one_or_none()
        if conv is None:
            return False

        await self._db.delete(conv)
        await self._db.commit()
        return True

    async def get_history(self, limit: int = 50) -> list[dict]:
        """SELECT requests ORDER BY created_at DESC."""
        rows = await self._db.execute(
            select(Request)
            .order_by(Request.created_at.desc())
            .limit(limit)
        )
        return [
            {
                "request_id": str(r.request_id),
                "text": r.text,
                "created_at": r.created_at.isoformat(),
                "status": r.status,
            }
            for r in rows.scalars()
        ]

    async def get_full_result(self, request_id: str) -> dict | None:
        """JOIN requests + generation_results по request_id."""
        try:
            rid = uuid.UUID(request_id)
        except ValueError:
            return None

        row = await self._db.execute(
            select(Request).where(Request.request_id == rid)
        )
        req = row.scalar_one_or_none()
        if req is None:
            return None

        result_row = await self._db.execute(
            select(GenerationResult)
            .where(GenerationResult.request_id == rid)
            .order_by(GenerationResult.generated_at.desc())
            .limit(1)
        )
        result = result_row.scalar_one_or_none()
        if result is None:
            return None

        return {
            "request_id": str(req.request_id),
            "text": req.text,
            "created_at": req.created_at.isoformat(),
            "status": req.status,
            "html": result.html,
            "css": result.css,
            "ami_graph": result.ami_graph,
            "generation_time_ms": result.generation_time_ms,
        }

