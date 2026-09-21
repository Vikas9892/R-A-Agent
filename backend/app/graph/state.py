from typing import TypedDict


class AgentState(TypedDict):
    """The central state passed across nodes in the LangGraph workflow."""

    user_input: str
    research: str
    final_answer: str
    tool_calls: int
