from langgraph.graph import END, START, StateGraph
from app.config import settings
from app.graph.state import AgentState
from app.guardrails.input import validate_input
from app.guardrails.output import validate_output
from app.agents.research_agent import run_research_agent
from app.agents.answer_agent import run_answer_agent


def input_guardrail_node(state: AgentState) -> dict:
    """Validate user input deterministically before passing to agents."""
    user_input = state.get("user_input", "")
    is_valid, msg = validate_input(user_input)

    if not is_valid:
        return {
            "final_answer": msg,
            "research": "Skipped due to input guardrail rejection.",
            "tool_calls": 0,
        }

    return {"user_input": msg}


def research_agent_node(state: AgentState) -> dict:
    """Execute the Research Agent if input guardrail passed."""
    # If input guardrail rejected, skip agent execution
    if state.get("final_answer"):
        return {}

    user_input = state.get("user_input", "")
    result = run_research_agent(user_input)
    # Enforce MAX_TOOL_CALLS = 5
    safe_tool_calls = min(result["tool_calls"], settings.max_tool_calls)
    return {
        "research": result["research"],
        "tool_calls": safe_tool_calls,
    }


def answer_agent_node(state: AgentState) -> dict:
    """Execute the Answer Agent to synthesize final answer from research."""
    # If already set by guardrail, preserve it
    if state.get("final_answer"):
        return {}

    user_input = state.get("user_input", "")
    research = state.get("research", "")
    answer = run_answer_agent(user_input, research)
    return {"final_answer": answer}


def output_guardrail_node(state: AgentState) -> dict:
    """Validate and sanitize the final synthesized answer."""
    raw_answer = state.get("final_answer", "")
    is_valid, sanitized = validate_output(raw_answer)

    if not is_valid:
        return {"final_answer": f"Error: Output rejected: {sanitized}"}

    return {"final_answer": sanitized}


def create_workflow() -> StateGraph:
    """Build and link the explicit LangGraph pipeline."""
    builder = StateGraph(AgentState)

    builder.add_node("input_guardrail", input_guardrail_node)
    builder.add_node("research_agent", research_agent_node)
    builder.add_node("answer_agent", answer_agent_node)
    builder.add_node("output_guardrail", output_guardrail_node)

    builder.add_edge(START, "input_guardrail")
    builder.add_edge("input_guardrail", "research_agent")
    builder.add_edge("research_agent", "answer_agent")
    builder.add_edge("answer_agent", "output_guardrail")
    builder.add_edge("output_guardrail", END)

    return builder


workflow = create_workflow().compile()
