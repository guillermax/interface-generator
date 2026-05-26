import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Conversation(Base):
    __tablename__ = "conversations"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )

    requests: Mapped[list["Request"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )


class Request(Base):
    __tablename__ = "requests"

    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    nlp_result: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.conversation_id", ondelete="CASCADE"),
        nullable=True,
    )

    results: Mapped[list["GenerationResult"]] = relationship(
        back_populates="request", cascade="all, delete-orphan"
    )
    conversation: Mapped[Optional["Conversation"]] = relationship(
        back_populates="requests"
    )


class GenerationResult(Base):
    __tablename__ = "generation_results"

    result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("requests.request_id", ondelete="CASCADE"),
        nullable=False,
    )
    html: Mapped[str] = mapped_column(Text, nullable=False)
    css: Mapped[str] = mapped_column(Text, nullable=False)
    ami_graph: Mapped[dict] = mapped_column(JSONB, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, server_default=func.now()
    )
    generation_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    request: Mapped["Request"] = relationship(back_populates="results")
    component_logs: Mapped[list["ComponentLog"]] = relationship(
        back_populates="result", cascade="all, delete-orphan"
    )


class ComponentLog(Base):
    __tablename__ = "components_log"

    log_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    result_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("generation_results.result_id", ondelete="CASCADE"),
        nullable=False,
    )
    component_type: Mapped[str] = mapped_column(String(50), nullable=False)
    generation_method: Mapped[str] = mapped_column(String(10), nullable=False)
    llm_attempts: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    result: Mapped["GenerationResult"] = relationship(back_populates="component_logs")
