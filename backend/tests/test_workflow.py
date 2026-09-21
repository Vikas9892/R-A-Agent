import json
from unittest.mock import patch
from app.graph.workflow import workflow


def test_workflow_execution() -> None:
    initial_state = {
        "user_input": "What is LangGraph?",
        "research": "",
        "final_answer": "",
        "tool_calls": 0,
    }

    mock_llm_finish = json.dumps({
        "action": "finish",
        "findings": "LangGraph is a library for building stateful, multi-actor applications with LLMs."
    })
    mock_final_answer = "LangGraph enables building robust multi-actor agent workflows."

    with (
        patch("app.agents.research_agent.generate_response", return_value=mock_llm_finish),
        patch("app.agents.answer_agent.generate_response", return_value=mock_final_answer),
    ):
        result = workflow.invoke(initial_state)

        assert result is not None
        assert "user_input" in result
        assert result["user_input"] == "What is LangGraph?"
        assert "research" in result
        assert "LangGraph is a library" in result["research"]
        assert "final_answer" in result
        assert result["final_answer"] == "LangGraph enables building robust multi-actor agent workflows."
        assert result["tool_calls"] == 0
