# R & A Agent — Research & Answer Agent

A lightweight, two-agent AI system built with **FastAPI**, **LangGraph**, **LiteLLM**, and **Next.js**.

---

## Overview

The **R & A Agent** splits complex question answering into two distinct, explainable roles:
1. **Research Agent**: Analyzes user intent, checks whether external tools are needed, and queries tools (Calculator, Weather, Web Search) up to a bounded maximum limit (`MAX_TOOL_CALLS = 5`).
2. **Answer Agent**: Synthesizes the collected research findings into a concise, factual final response without hallucinating or calling tools.

By keeping the agent boundaries explicit and deterministic, the system remains easy to debug, test, and explain in technical interviews.

---

## Architecture

```
                    ┌─────────────────────┐
                    │     Next.js UI      │
                    │  Clean Chat + Trace │
                    └──────────┬──────────┘
                               │ HTTP POST /api/v1/chat
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
                    │  (Math/Weather/Web) │
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
         (Primary Fast)  (Research Heavy) (Fallback)
```

---

## Features

- **Two-Agent Pipeline**: Separation of concerns between information gathering and factual synthesis.
- **Explicit Workflow with LangGraph**: State machine orchestration providing predictable step transitions.
- **Provider-Agnostic with LiteLLM**: Swap between Groq, Gemini, OpenAI, Claude, or local LLMs using environment variables without modifying agent code.
- **Bounded Tool Calling**: Hard stop at `MAX_TOOL_CALLS = 5` to prevent infinite loops and runaway API costs.
- **Deterministic Guardrails**: Zero-overhead validation against prompt injections, oversized payloads, and internal prompt leakage without calling another LLM.
- **Interactive Web Interface**: Next.js + Tailwind UI showing real-time step visualization of the agent pipeline.
- **Structured Observability**: Unique `X-Request-ID` attached to every request, with sanitized logs that never leak API keys or user secrets.
- **100% Offline Test Suite**: 33 comprehensive unit and integration tests runnable without external API keys.

---

## Tech Stack

- **Backend**: Python 3.13+, FastAPI, Pydantic v2, Pydantic-Settings
- **Agent Orchestration**: LangGraph, LangChain Core
- **LLM Layer**: LiteLLM
- **Frontend**: Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Lucide Icons
- **Testing**: pytest, pytest-asyncio, HTTPX TestClient

---

## Workflow

```
User
  │
  ▼
[Input Guardrail]
  │  (validates format, length, checks prompt injection)
  ▼
[Research Agent] ◄──────┐
  │                     │
  ├─► [Tool Calling] ───┘ (Calculator / Weather / Web Search, max 5)
  ▼
[Answer Agent]
  │  (synthesizes grounded final answer)
  ▼
[Output Guardrail]
  │  (sanitizes text, enforces length limits, scrubs debug tokens)
  ▼
User Response
```

---

## Agents

### Research Agent (`backend/app/agents/research_agent.py`)
- Analyzes the incoming question.
- Determines whether calculation, live weather, or web search is required.
- Executes tool calls iteratively in an autonomous feedback loop.
- Automatically halts when sufficient evidence is collected or when `MAX_TOOL_CALLS = 5` is reached.
- Passes structured research notes to the LangGraph state.

### Answer Agent (`backend/app/agents/answer_agent.py`)
- Receives the original user request alongside the gathered research notes.
- Synthesizes a direct, concise, and structured final answer.
- **Strictly forbidden from calling tools** to maintain separation of concerns.
- If research is insufficient, explicitly communicates the limitation rather than hallucinating details.

---

## Tools

Three safe, typed tools are integrated using standard LangChain tool interfaces:

1. **Calculator** (`backend/app/tools/calculator.py`):
   - Safely parses and evaluates mathematical expressions using Python's Abstract Syntax Tree (`ast`).
   - Supports `+`, `-`, `*`, `/`, `//`, `%`, `**`, unary operators, and parentheses.
   - **Zero raw `eval()`**: completely prevents arbitrary code execution.
2. **Weather** (`backend/app/tools/weather.py`):
   - Resolves locations and queries current temperature and windspeed using Open-Meteo's geocoding and forecast APIs.
   - Requires no mandatory third-party API key.
3. **Web Search** (`backend/app/tools/web_search.py`):
   - Performs lightweight live web search queries via DuckDuckGo to obtain up-to-date documentation and snippets.

---

## Guardrails

Deterministic checks run before and after the agent workflow:

- **Input Guardrail** (`backend/app/guardrails/input.py`):
  - Rejects empty or whitespace-only inputs.
  - Enforces `MAX_INPUT_LENGTH = 1000` characters.
  - Rejects prompt injection and system instruction extraction attempts.
- **Output Guardrail** (`backend/app/guardrails/output.py`):
  - Ensures the response is a valid string.
  - Scrubs internal workflow markers, tags, or debug remnants.
  - Enforces `MAX_OUTPUT_LENGTH = 4000` characters.
  - Verifies the `MAX_TOOL_CALLS = 5` bound.

---

## LiteLLM Multi-Model Routing

All LLM completions are routed through `backend/app/llm/client.py`:

```
Agent Request ──► LiteLLM Client ──► MODEL_1 / MODEL_2 / MODEL_3
```

Configured in `.env`:
```env
MODEL_1=groq/llama-3.3-70b-versatile
MODEL_2=gemini/gemini-1.5-flash
MODEL_3=openai/gpt-4o-mini
```

---

## Project Structure

```
r-and-a-agent/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── chat.py         # POST /api/v1/chat endpoint
│   │   ├── agents/
│   │   │   ├── research_agent.py   # Research agent with tool-calling loop
│   │   │   └── answer_agent.py     # Answer synthesis agent
│   │   ├── graph/
│   │   │   ├── state.py            # AgentState TypedDict
│   │   │   └── workflow.py         # StateGraph pipeline definition
│   │   ├── tools/
│   │   │   ├── calculator.py       # Safe AST-based calculator
│   │   │   ├── weather.py          # Open-Meteo weather lookup
│   │   │   └── web_search.py       # DuckDuckGo web search
│   │   ├── guardrails/
│   │   │   ├── input.py            # Input validation & anti-injection
│   │   │   └── output.py           # Output validation & tag scrubbing
│   │   ├── llm/
│   │   │   └── client.py           # LiteLLM routing client
│   │   ├── config.py               # Pydantic Settings
│   │   └── main.py                 # FastAPI application & middleware
│   └── tests/
│       ├── test_health.py          # /health test
│       ├── test_api.py             # /api/v1/chat & validation tests
│       ├── test_agents.py          # Research & Answer agent unit tests
│       ├── test_tools.py           # Calculator, weather & search tests
│       ├── test_guardrails.py      # Input & output guardrail tests
│       ├── test_llm.py             # LiteLLM client tests
│       └── test_workflow.py        # LangGraph end-to-end workflow test
├── frontend/
│   ├── app/
│   │   ├── layout.tsx              # Root HTML & metadata
│   │   ├── page.tsx                # Main chat page & state manager
│   │   └── globals.css             # Tailwind base styles
│   ├── components/
│   │   ├── Header.tsx              # Brand header & online indicator
│   │   ├── ChatInput.tsx           # Query input & example chips
│   │   ├── WorkflowStatus.tsx      # Visual LangGraph step trace
│   │   └── AnswerCard.tsx          # Answer display & tool calls badge
│   ├── .env.local.example          # Frontend env sample
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── .env.example                    # Backend env sample
├── .gitignore                      # Git ignore file
├── README.md                       # Documentation
└── requirements.txt                # Python dependencies
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
| `MODEL_1` | Primary model | `groq/llama-3.3-70b-versatile` |
| `MODEL_2` | Secondary model | `gemini/gemini-1.5-flash` |
| `MODEL_3` | Fallback model | `openai/gpt-4o-mini` |
| `GROQ_API_KEY` | Groq API Key | (optional, depending on model) |
| `GEMINI_API_KEY` | Gemini API Key | (optional, depending on model) |
| `OPENAI_API_KEY` | OpenAI API Key | (optional, depending on model) |
| `MAX_TOOL_CALLS` | Max tool iterations per run | `5` |

---

## Local Setup

### 1. Backend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --app-dir backend --reload --port 8000
```

Verify backend health:
```bash
curl http://localhost:8000/health
# {"status":"ok","app":"R & A Agent"}
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## API Reference

### Health Check
```http
GET /health
```
Response:
```json
{
  "status": "ok",
  "app": "R & A Agent"
}
```

### Chat & Research Execution
```http
POST /api/v1/chat
Content-Type: application/json

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

---

## Testing

Run the full backend test suite:
```bash
pytest backend/tests -v
```

All 33 tests execute completely offline using mocks for external tools and LLMs.

---

