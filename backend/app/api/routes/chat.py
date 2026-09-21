import logging
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field
from app.graph.workflow import workflow

logger = logging.getLogger("app.api.chat")

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
def chat_endpoint(request: ChatRequest, req: Request) -> ChatResponse:
    """Synchronous endpoint executing the full LangGraph workflow.

    Workflow execution steps:
    1. Input Guardrail
    2. Research Agent (with tool execution loop)
    3. Answer Agent (factual synthesis)
    4. Output Guardrail
    """
    request_id = getattr(req.state, "request_id", "local")
    logger.info("[%s] Processing chat request (input_length=%d)", request_id, len(request.message))

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

        logger.info(
            "[%s] Workflow completed successfully (tool_calls=%d, answer_length=%d)",
            request_id,
            tool_calls,
            len(answer),
        )

        return ChatResponse(answer=answer, tool_calls=tool_calls)
    except Exception as exc:
        logger.error("[%s] Workflow execution error: %s", request_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {exc}",
        ) from exc
