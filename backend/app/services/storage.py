"""
StorageService — сохранение истории запросов и результатов генерации в PostgreSQL.
"""
import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ComponentLog, GenerationResult, Request


class StorageService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    # ------------------------------------------------------------------ write

    async def save_request(self, text: str) -> uuid.UUID:
        """INSERT request со статусом pending, возвращает request_id."""
        req = Request(text=text, status="pending")
        self._db.add(req)
        await self._db.flush()        # получаем request_id до commit
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

    async def mark_error(self, request_id: uuid.UUID, error_message: str) -> None:
        """UPDATE requests: status='error'."""
        await self._db.execute(
            update(Request)
            .where(Request.request_id == request_id)
            .values(status="error")
        )
        await self._db.commit()

    # ------------------------------------------------------------------ read

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

