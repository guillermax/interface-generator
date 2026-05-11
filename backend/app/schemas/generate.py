from pydantic import BaseModel, Field

from app.schemas.ami import AMIGraph


class GenerateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class GenerateResponse(BaseModel):
    request_id: str
    html: str
    css: str
    generation_time_ms: float
    ami: AMIGraph | None = None
