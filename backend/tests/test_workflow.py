from app.graph.workflow import workflow


def test_workflow_execution() -> None:
    initial_state = {
        "user_input": "What is LangGraph?",
        "research": "",
        "final_answer": "",
        "tool_calls": 0,
    }

    result = workflow.invoke(initial_state)

    assert result is not None
    assert "user_input" in result
    assert result["user_input"] == "What is LangGraph?"
    assert "research" in result
    assert "final_answer" in result
    assert "Synthesized answer" in result["final_answer"]
    assert result["tool_calls"] == 0
