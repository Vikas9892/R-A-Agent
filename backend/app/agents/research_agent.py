import json
import logging
from typing import Any
from app.config import settings
from app.llm.client import generate_response
from app.tools.calculator import calculator
from app.tools.weather import get_weather
from app.tools.web_search import web_search

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Research Agent. Your job is to gather accurate information to answer the user's question.
You have access to the following tools:
1. calculator(expression: str) - For arithmetic math operations.
2. weather(city: str) - For current weather data of any city.
3. web_search(query: str) - For current facts, documentation, or search results.

Instructions:
- If you need a tool, respond ONLY with a JSON object:
  {"action": "tool", "tool": "<calculator|weather|web_search>", "input": "<tool argument string>"}
- If you have enough information or no tool is needed, respond ONLY with a JSON object:
  {"action": "finish", "findings": "<summary of facts discovered>"}
"""


def _execute_tool(tool_name: str, tool_input: str) -> str:
    """Safely execute a tool with error handling."""
    clean_tool = tool_name.strip().lower()
    try:
        if clean_tool == "calculator":
            return calculator.invoke({"expression": tool_input})
        if clean_tool in ("weather", "get_weather"):
            return get_weather.invoke({"city": tool_input})
        if clean_tool in ("web_search", "search"):
            return web_search.invoke({"query": tool_input})
        return f"Error: Unknown tool '{tool_name}'."
    except Exception as exc:
        logger.error("Error invoking tool '%s': %s", tool_name, exc)
        return f"Error executing {tool_name}: {exc}"


def run_research_agent(user_input: str, max_tool_calls: int | None = None) -> dict[str, Any]:
    """Execute the Research Agent loop.

    Gathers information using tools up to the configured tool limit.
    """
    limit = max_tool_calls if max_tool_calls is not None else settings.max_tool_calls
    tool_calls_count = 0
    research_log: list[str] = []

    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"User question: {user_input}"},
    ]

    while tool_calls_count < limit:
        llm_output = generate_response(messages, model=settings.model_2 or settings.model_1)
        
        # Parse decision JSON
        try:
            # Handle potential markdown code fencing in LLM response
            clean_output = llm_output.strip()
            if clean_output.startswith("```"):
                clean_output = clean_output.strip("`").replace("json\n", "", 1)
            decision = json.loads(clean_output)
        except Exception:
            # Fallback if raw text returned: treat as finished research
            research_log.append(llm_output)
            break

        action = decision.get("action")
        if action == "finish":
            findings = decision.get("findings", "")
            if findings:
                research_log.append(findings)
            break

        if action == "tool":
            tool_name = decision.get("tool", "")
            tool_input = decision.get("input", "")
            tool_calls_count += 1

            logger.info("Research Agent calling tool '%s' with input '%s' (call %d/%d)",
                        tool_name, tool_input, tool_calls_count, limit)
            
            tool_result = _execute_tool(tool_name, tool_input)
            research_log.append(f"Tool [{tool_name}]: {tool_result}")

            # Feed tool result back into context for next iteration
            messages.append({"role": "assistant", "content": llm_output})
            messages.append({"role": "user", "content": f"Tool [{tool_name}] result: {tool_result}"})
        else:
            research_log.append(str(decision))
            break

    if not research_log:
        research_log.append("No external research gathered.")

    return {
        "research": "\n\n".join(research_log),
        "tool_calls": tool_calls_count,
    }
