import json
from unittest.mock import patch
from app.agents.research_agent import run_research_agent


def test_research_agent_no_tool() -> None:
    """Agent immediately finishes with findings without calling any tool."""
    mock_llm_response = json.dumps({
        "action": "finish",
        "findings": "FastAPI is a modern Python web framework based on Starlette and Pydantic."
    })

    with patch("app.agents.research_agent.generate_response", return_value=mock_llm_response):
        result = run_research_agent("What is FastAPI?")
        assert result["tool_calls"] == 0
        assert "FastAPI is a modern Python web framework" in result["research"]


def test_research_agent_calls_tool() -> None:
    """Agent requests a calculator tool call then finishes."""
    step1_response = json.dumps({
        "action": "tool",
        "tool": "calculator",
        "input": "12 * 12"
    })
    step2_response = json.dumps({
        "action": "finish",
        "findings": "The calculated product is 144."
    })

    with patch("app.agents.research_agent.generate_response", side_effect=[step1_response, step2_response]):
        result = run_research_agent("What is 12 * 12?")
        assert result["tool_calls"] == 1
        assert "Tool [calculator]: 144" in result["research"]
        assert "The calculated product is 144." in result["research"]


def test_research_agent_tool_failure() -> None:
    """Agent handles tool execution error gracefully without crashing."""
    step1_response = json.dumps({
        "action": "tool",
        "tool": "calculator",
        "input": "10 / 0"
    })
    step2_response = json.dumps({
        "action": "finish",
        "findings": "Calculation failed due to division by zero."
    })

    with patch("app.agents.research_agent.generate_response", side_effect=[step1_response, step2_response]):
        result = run_research_agent("Divide 10 by 0")
        assert result["tool_calls"] == 1
        assert "Division by zero is undefined" in result["research"]


def test_research_agent_max_tool_calls_limit() -> None:
    """Agent stops tool calling loop when max_tool_calls limit is reached."""
    continuous_tool_response = json.dumps({
        "action": "tool",
        "tool": "calculator",
        "input": "1 + 1"
    })

    # Return tool request indefinitely
    with patch("app.agents.research_agent.generate_response", return_value=continuous_tool_response):
        result = run_research_agent("Loop forever", max_tool_calls=5)
        assert result["tool_calls"] == 5


def test_answer_agent_successful_synthesis() -> None:
    from app.agents.answer_agent import run_answer_agent

    mock_llm_response = "FastAPI is a modern, high-performance web framework for Python."

    with patch("app.agents.answer_agent.generate_response", return_value=mock_llm_response):
        answer = run_answer_agent("What is FastAPI?", "FastAPI is built on Starlette and Pydantic.")
        assert answer == "FastAPI is a modern, high-performance web framework for Python."


def test_answer_agent_insufficient_information() -> None:
    from app.agents.answer_agent import run_answer_agent

    mock_llm_response = "The available research is insufficient to determine the exact date."

    with patch("app.agents.answer_agent.generate_response", return_value=mock_llm_response):
        answer = run_answer_agent("When will Project X launch?", "No external research gathered.")
        assert "insufficient" in answer.lower()

