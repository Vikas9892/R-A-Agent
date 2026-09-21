# R & A Agent — Research & Answer Agent

A lightweight, interview-friendly, two-agent AI system built with **FastAPI**, **LangGraph**, **LiteLLM**, and **Next.js**.

The system splits agentic reasoning into two distinct, explainable roles:
1. **Research Agent**: Analyzes user intent and queries external tools (Calculator, Weather, Web Search) up to a bounded limit.
2. **Answer Agent**: Synthesizes the gathered research into a concise, factual, and hallucination-free final response.

---

## Current Architecture

```
                    ┌─────────────────────┐
                    │     Next.js UI      │
                    │  Clean Chat + Trace │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │    /api/v1/chat     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     LangGraph       │
                    │                     │
                    │  Input Guardrail    │
                    │        ↓            │
                    │  Research Agent     │
                    │        ↓            │
                    │    Tool Calling     │
                    │        ↓            │
                    │    Answer Agent     │
                    │        ↓            │
                    │  Output Guardrail   │
                    └──────────┬──────────┘
                               │
                               ▼
                          LiteLLM
                               │
                 ┌─────────────┼─────────────┐
                 ▼             ▼             ▼
              Model 1       Model 2       Model 3
```

### LiteLLM Multi-Model Architecture

Instead of hardcoding agents to a specific LLM provider (OpenAI, Anthropic, Groq, Google, etc.), all completions pass through a unified LiteLLM client (`backend/app/llm/client.py`).

Three model tiers are configured via environment variables:
- **`MODEL_1`**: Primary reasoning model (e.g. `groq/llama-3.3-70b-versatile` or `gemini/gemini-1.5-flash`).
- **`MODEL_2`**: Secondary / specialized model.
- **`MODEL_3`**: Fallback model (e.g. `openai/gpt-4o-mini`).

This eliminates vendor lock-in and allows seamless provider switching without altering agent code.

### Agent Tools

The Research Agent is equipped with three clean, typed tools:

1. **Calculator** (`backend/app/tools/calculator.py`):
   - Evaluates arithmetic expressions safely using Python's Abstract Syntax Tree (`ast`).
   - Supports addition, subtraction, multiplication, division, modulo, exponents, and parentheses.
   - **Zero raw `eval()`**: completely prevents arbitrary code execution.
2. **Weather** (`backend/app/tools/weather.py`):
   - Retrieves live weather conditions (temperature, windspeed) for any city using Open-Meteo's geocoding and forecast APIs.
   - Fully mockable and requires no mandatory third-party key.
3. **Web Search** (`backend/app/tools/web_search.py`):
   - Performs lightweight live web search queries via DuckDuckGo to obtain up-to-date documentation, definitions, and articles.

### LangGraph Workflow & State

The workflow is built with LangGraph's `StateGraph` for explicit execution control.

#### Agent State:
```python
class AgentState(TypedDict):
    user_input: str
    research: str
    final_answer: str
    tool_calls: int
```

#### Graph Pipeline:
```
START
  ↓
[input_guardrail]
  ↓
[research_agent]
  ↓ (calls tools if needed)
[answer_agent]
  ↓
[output_guardrail]
  ↓
END
```

### Research Agent

The **Research Agent** (`backend/app/agents/research_agent.py`):
1. Analyzes the user's intent.
2. Decides whether to invoke a tool (`calculator`, `weather`, or `web_search`) or finalize research findings.
3. Automatically iterates in a tool-calling feedback loop until sufficient evidence is gathered.
4. Enforces a strict upper bound of `MAX_TOOL_CALLS = 5` to prevent infinite loops or runaway API billing.
5. Captures and handles tool failures gracefully.
6. Returns accumulated research notes and exact tool call counts.

### Answer Agent

The **Answer Agent** (`backend/app/agents/answer_agent.py`):
1. Receives the user request alongside the factual research gathered by the Research Agent.
2. Synthesizes a direct, concise, and structured final answer.
3. **Does not invoke tools**; its role is strictly synthesis and verification against provided research.
4. If available research is insufficient, it explicitly communicates the limitation rather than hallucinating details.

### Deterministic Guardrails

The system employs zero-overhead deterministic guardrails before and after agent reasoning:

```
Input Guardrail
      ↓
Research Agent
      ↓
 Answer Agent
      ↓
Output Guardrail
```

- **Input Guardrail** (`backend/app/guardrails/input.py`):
  - Enforces non-empty input.
  - Rejects inputs exceeding `MAX_INPUT_LENGTH` (1,000 characters).
  - Deterministically rejects prompt-injection and instruction override attempts (e.g. "ignore previous instructions", "reveal system prompt", "developer mode").
- **Output Guardrail** (`backend/app/guardrails/output.py`):
  - Validates output is non-empty string.
  - Scrubs internal workflow markers and debug tags.
  - Bounds output length to `MAX_OUTPUT_LENGTH` (4,000 characters).
  - Enforces `MAX_TOOL_CALLS = 5` invariant.

### Observability & Request Tracing

- **Request ID Middleware**: Every inbound request receives a unique UUIDv4 `X-Request-ID` attached to response headers and request state.
- **Structured Non-Sensitive Logging**:
  - Request receipt, method, and route
  - Agent step lifecycle (Research Agent start, tool invocation, tool completion, Answer Agent start)
  - Latency and status codes
  - **Zero credential leaks**: API keys, auth tokens, and raw sensitive prompt text are strictly excluded from logs.

---

## Tech Stack

- **Backend Framework**: Python 3.13+, FastAPI, Pydantic v2
- **Agent Orchestration**: LangGraph, LangChain Core
- **LLM Gateway**: LiteLLM (multi-model fallback & abstraction)
- **Frontend**: Next.js (App Router), TypeScript, Tailwind CSS
- **Testing**: pytest, pytest-asyncio, HTTPX TestClient

---

## Project Structure

```
r-and-a-agent/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── chat.py
│   │   ├── agents/
│   │   │   ├── research_agent.py
│   │   │   └── answer_agent.py
│   │   ├── graph/
│   │   │   ├── state.py
│   │   │   └── workflow.py
│   │   ├── tools/
│   │   │   ├── calculator.py
│   │   │   ├── weather.py
│   │   │   └── web_search.py
│   │   ├── guardrails/
│   │   │   ├── input.py
│   │   │   └── output.py
│   │   ├── llm/
│   │   │   └── client.py
│   │   ├── config.py
│   │   └── main.py
│   └── tests/
│       ├── test_health.py
│       ├── test_api.py
│       ├── test_agents.py
│       ├── test_tools.py
│       ├── test_guardrails.py
│       └── test_workflow.py
├── frontend/
│   ├── app/
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── ChatInput.tsx
│   │   ├── WorkflowStatus.tsx
│   │   └── AnswerCard.tsx
│   ├── .env.local.example
│   └── package.json
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

| Variable | Description | Default / Example |
|---|---|---|
| `PORT` | Backend port | `8000` |
| `HOST` | Backend host | `0.0.0.0` |
| `MODEL_1` | Primary LLM model | `groq/llama-3.3-70b-versatile` |
| `MODEL_2` | Secondary LLM model | `gemini/gemini-1.5-flash` |
| `MODEL_3` | Fallback LLM model | `openai/gpt-4o-mini` |
| `GROQ_API_KEY` | API Key for Groq | Optional (based on model) |
| `GEMINI_API_KEY` | API Key for Gemini | Optional (based on model) |
| `OPENAI_API_KEY` | API Key for OpenAI | Optional (based on model) |
| `WEATHER_API_KEY`| API Key for weather data | Optional |
| `MAX_TOOL_CALLS` | Guardrail limit on tool iterations | `5` |

---

## How to Run the Backend

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --app-dir backend --reload --port 8000
   ```
3. Test health check:
   ```bash
   curl http://localhost:8000/health
   # Returns: {"status": "ok", "app": "R & A Agent"}
   ```

---

## API Reference

### 1. Health Check
`GET /health`

Response:
```json
{
  "status": "ok",
  "app": "R & A Agent"
}
```

### 2. Chat & Research Execution
`POST /api/v1/chat`

Request:
```json
{
  "message": "What is 15 * 24 + 180?"
}
```

Response:
```json
{
  "answer": "15 * 24 + 180 equals 540.",
  "tool_calls": 1
}
```

Example `curl` call:
```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather in Tokyo?"}'
```

---

## How to Run the Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
4. Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Running Tests

Execute pytest across the backend suite:
```bash
pytest backend/tests -v
```

---

## Development Phases

- **Phase 0**: Repository Foundation (Directory setup, FastAPI `/health`, `.gitignore`, `.env.example`, README)
- **Phase 1**: LiteLLM Layer (Configurable 3-model routing, Pydantic settings, mocked LLM client tests)
- **Phase 2**: Tools (Calculator, Weather, Web Search with strict types & zero raw eval)
- **Phase 3**: LangGraph State & Workflow Scaffold (Typed state and StateGraph compilation)
- **Phase 4**: Research Agent (Tool-calling loop with `MAX_TOOL_CALLS=5` bound)
- **Phase 5**: Answer Agent (Pure synthesis from gathered research)
- **Phase 6**: Guardrails (Deterministic input & output validation, prompt-injection defense)
- **Phase 7**: FastAPI API (`POST /api/v1/chat`, `GET /health`, request/response schemas)
- **Phase 8**: Next.js Professional Frontend (Workflow trace visualizer, chat UI)
- **Phase 9**: Observability & Developer Experience (Request IDs, structured non-sensitive logging)
- **Phase 10**: Testing & Verification (100% offline unit/mock test suite)
- **Phase 11**: Final Polish & Documentation
