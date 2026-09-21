import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.graph.workflow import workflow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Chat"])


class ChatRequest(BaseModel):
    """Payload for submitting a user query to the R & A Agent."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User query string to be analyzed and answered.",
        examples=["What is FastAPI?"],
    )


class ChatResponse(BaseModel):
    """Result payload returned by the R & A Agent pipeline."""

    answer: str = Field(..., description="Synthesized answer produced by the Answer Agent.")
    tool_calls: int = Field(..., description="Number of external tool calls executed.")


@router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Research & Answer agent workflow",
)
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Synchronous endpoint executing the full LangGraph workflow.

    Workflow execution steps:
    1. Input Guardrail
    2. Research Agent (with tool execution loop)
    3. Answer Agent (factual synthesis)
    4. Output Guardrail
    """
    try:
        initial_state = {
            "user_input": request.message,
            "research": "",
            "final_answer": "",
            "tool_calls": 0,
        }

        result = workflow.invoke(initial_state)

        answer = result.get("final_answer", "")
        tool_calls = result.get("tool_calls", 0)

        return ChatResponse(answer=answer, tool_calls=tool_calls)
    except Exception as exc:
        logger.error("Chat endpoint workflow failure: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {exc}",
        ) from exc
