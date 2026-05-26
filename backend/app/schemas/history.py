from pydantic import BaseModel


class HistoryItem(BaseModel):
    request_id: str
    text: str
    created_at: str
    status: str


class FullResult(HistoryItem):
    html: str
    css: str
    ami_graph: dict | None = None
    generation_time_ms: int | None = None


class ConversationItem(BaseModel):
    conversation_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int


class ConversationMessage(BaseModel):
    request_id: str
    text: str
    created_at: str
    status: str
    html: str | None = None
    css: str | None = None
    generation_time_ms: int | None = None
