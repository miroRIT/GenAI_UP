from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse
from app.services.ai_service import answer_question


router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> dict[str, object]:
    return answer_question(request.question)
