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
