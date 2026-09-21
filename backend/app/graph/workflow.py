from langgraph.graph import END, START, StateGraph
from app.graph.state import AgentState
from app.agents.research_agent import run_research_agent
from app.agents.answer_agent import run_answer_agent


def input_guardrail_node(state: AgentState) -> dict:
    """Validate and sanitize user input before passing to agents."""
    return {"user_input": state.get("user_input", "").strip()}


def research_agent_node(state: AgentState) -> dict:
    """Execute the Research Agent with bounded tool-calling loop."""
    user_input = state.get("user_input", "")
    result = run_research_agent(user_input)
    return {
        "research": result["research"],
        "tool_calls": result["tool_calls"],
    }


def answer_agent_node(state: AgentState) -> dict:
    """Execute the Answer Agent to synthesize final answer from research."""
    user_input = state.get("user_input", "")
    research = state.get("research", "")
    answer = run_answer_agent(user_input, research)
    return {"final_answer": answer}


def output_guardrail_node(state: AgentState) -> dict:
    """Validate and sanitize the final synthesized answer."""
    return {"final_answer": state.get("final_answer", "").strip()}


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
