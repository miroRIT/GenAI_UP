from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.agent_service import answer_urban_intelligence_query


router = APIRouter(tags=["agent"])


class AgentQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural-language city operations question.")


@router.post("/agent/query")
def query_agent(request: AgentQueryRequest) -> dict[str, object]:
    return answer_urban_intelligence_query(request.query)
