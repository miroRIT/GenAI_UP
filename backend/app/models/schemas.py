from pydantic import BaseModel


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict[str, str]]
    related_metrics: list[dict[str, object]]
    recommended_actions: list[str]
    risk_or_opportunity_level: str
    data_limitations: list[str]


class UploadResponse(BaseModel):
    category: str
    rows_loaded: int
    message: str
