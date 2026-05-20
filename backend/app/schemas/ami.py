from pydantic import BaseModel, ConfigDict, Field


class AMINode(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    node_id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex[:8])
    type: str
    attributes: dict = Field(default_factory=dict)
    styles: dict = Field(default_factory=dict)
    children: list['AMINode'] = Field(default_factory=list)


AMINode.model_rebuild()


class AMIGraph(BaseModel):
    """Корневой объект AMI-графа"""
    components: list[AMINode] = Field(default_factory=list)


class Entity(BaseModel):
    """Распознанная сущность из NLP"""
    entity_id: str = Field(default_factory=lambda: __import__('uuid').uuid4().hex[:8])
    entity_type: str
    text: str
    attributes: dict = Field(default_factory=dict)
    parent_id: str | None = None
    confidence: float = 0.95
