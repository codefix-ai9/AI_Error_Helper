# AI-Based Programming Error Helper

[![Tests](https://img.shields.io/badge/backend%20tests-101%20passed-brightgreen.svg)]()
[![Vitest](https://img.shields.io/badge/frontend%20tests-35%20passed-brightgreen.svg)]()
[![Coverage](https://img.shields.io/badge/ai%2Fvalidator%20coverage-95%25-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

> A robust, privacy-first local developer dashboard that diagnoses programming errors using a **hybrid analysis pipeline**: deterministic static analysis (AST, tracebacks, rule engine) first, AI-assisted pedagogical guidance second.

---

## Table of Contents
- [1. Overview & Problem Statement](#1-overview--problem-statement)
- [2. Objectives & Key Features](#2-objectives--key-features)
- [3. Architecture & Hybrid Pipeline](#3-architecture--hybrid-pipeline)
- [4. Technology Stack](#4-technology-stack)
- [5. Repository Structure](#5-repository-structure)
- [6. Quickstart (≤ 5 Commands)](#6-quickstart--5-commands)
- [7. Configuration & Environment Variables](#7-configuration--environment-variables)
- [8. Running Tests & Quality Gates](#8-running-tests--quality-gates)
- [9. Supported Languages & Error Taxonomies](#9-supported-languages--error-taxonomies)
- [10. API Overview & Envelope Standard](#10-api-overview--envelope-standard)
- [11. Privacy, Security & Prompt Injection Defense](#11-privacy-security--prompt-injection-defense)
- [12. Limitations & Known Boundaries](#12-limitations--known-boundaries)
- [13. Demonstration Walkthrough](#13-demonstration-walkthrough)
- [14. Future Work](#14-future-work)

---

## 1. Overview & Problem Statement

Beginner and intermediate programmers frequently struggle with compiler errors, unhandled runtime exceptions, and ambiguous stack traces. While commercial LLMs (e.g. ChatGPT, Claude) can assist with code debugging, relying on them exclusively in educational settings presents critical issues:
1. **Hallucination**: LLMs frequently invent non-existent compiler errors or report incorrect line numbers.
2. **Lack of Grounding**: Generative models cannot guarantee that a suggested fix preserves syntax validity.
3. **Catastrophic Failure**: When cloud APIs experience rate limits, latency spikes, or outages, pure AI tools break completely.
4. **Token Cost & Latency**: Sending code to third-party APIs for simple syntax errors is wasteful.

The **AI-Based Programming Error Helper** solves these challenges by combining **deterministic static analysis** with **generative AI teaching**. Static analysis grounds the facts (line number, category, severity, compiler evidence), while the AI engine explains concepts without being permitted to alter verified facts.

---

## 2. Objectives & Key Features

- **Hybrid Pipeline with Authority Lock (§7.5)**: Static compiler and AST evidence unconditionally decide the line number, severity, and category. The AI explains the concept but cannot contradict proven facts.
- **Graceful Degradation (§7.7)**: If the AI provider is disabled, times out, or fails, the application returns HTTP 200 with verified static findings and template-based guidance with a visible fallback banner.
- **Explicit Provenance Badging (§5.3, §10)**: Every piece of information displays clear badges: `STATIC FACT` (green), `AI ASSISTED` (purple), or `DERIVED` (blue).
- **Side-by-Side & Unified Diff View**: Server-side `difflib` generates clean line diffs showing before and after states.
- **Static Verification Re-Check (§5.3)**: Corrected code is statically re-parsed to confirm that the syntax issue is resolved before presenting it to the user.
- **Zero Arbitrary Execution (§11)**: User code is never executed. Only AST parsing, static regex rules, and traceback extraction are used.
- **Local SQLite History & Analytics (§9)**: Stored locally in SQLite with WAL mode, parameterized full-text search, filters, pagination, and visual metric trends.
- **Prompt Injection Defense (§7.2, §11)**: Untrusted code and error strings are strictly isolated inside delimited tags (`<source_code>`, `<error_output>`) with system prompt guardrails.

---

## 3. Architecture & Hybrid Pipeline

The system strictly enforces a **7-layer unidirectional pipeline**:

```text
USER / BROWSER
      ↓
DASHBOARD / PRESENTATION LAYER         (React + Vite, Vanilla CSS)
      ↓
API & APPLICATION SERVICE LAYER        (FastAPI routers, Dependency Container)
      ↓
INPUT VALIDATION & PREPROCESSING       (Size bounds, ANSI cleaning, Secret Redaction)
      ↓
STATIC ANALYSIS ENGINE                 (Python AST, Traceback Parser, Rule Engine)
      ↓
AI ANALYSIS ENGINE                     (Mock / Anthropic / OpenAI Providers + Validator)
      ↓
RESULT VALIDATION & RECOMMENDATION     (difflib, Static Verification, Authority Lock)
      ↓
RESULT DISPLAY & PERSISTENCE           (SQLite analyses table, Dashboard Views)
```

Layer boundaries are enforced by automated architectural tests (`backend/tests/unit/test_architecture.py`) using Python AST import analysis to ensure `ai/` never imports `analysis/` and presentation layers remain decoupled.

---

## 4. Technology Stack

- **Backend**:
  - Python 3.11+ / 3.13
  - FastAPI & Starlette (REST API with unified JSON envelope)
  - Pydantic v2 (DTOs and schema validation)
  - SQLite3 (stdlib with WAL mode & indexing)
  - `difflib` (deterministic unified diffs)
  - `pytest` & `pytest-cov` (unit & integration testing)
- **Frontend**:
  - React 18 & Vite
  - Plain CSS / Modern CSS Variables (responsive, dark-mode ready, glassmorphism, no Tailwind dependency)
  - Vitest & React Testing Library (frontend automated test suites)
- **AI Providers**:
  - `MockProvider` (deterministic, zero-cost, canned fixtures)
  - `AnthropicProvider` (Claude 3.5 Sonnet API)
  - `OpenAICompatibleProvider` (OpenAI / Gemini / Ollama endpoints)

---

## 5. Repository Structure

```text
ai-based-programming-error-helper/
├── README.md                           # Master documentation
├── .env.example                        # Template environment variables
├── data/
│   ├── app.db                          # Local SQLite database (git-ignored)
│   └── contract_fixtures/              # Contract-shaped JSON payloads
├── docs/                               # Architecture, API, and QA specifications
│   ├── architecture.md                 # 7-layer pipeline and module map
│   ├── api.md                          # Endpoint schemas and envelope examples
│   ├── ai-pipeline.md                  # Prompt engineering and validation pipeline
│   ├── data-model.md                   # DTO sequence and ErrorType taxonomy
│   ├── demo-script.md                  # 10-minute evaluator walkthrough
│   ├── viva-prep.md                    # 20 examiner Q&As
│   ├── requirements-traceability.md    # Requirements traceability matrix
│   └── verification-log-part-b.md      # Part B verification and audit log
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entrypoint, CORS, rate-limiter
│   │   ├── api/routers/                # Health, languages, analyze, history, analytics, samples
│   │   ├── application/                # Container and service orchestration
│   │   ├── validation/                 # Request validation against §5.6 rules
│   │   ├── preprocessing/              # Redaction, BOM and ANSI cleaning
│   │   ├── analysis/                   # AST analyzers, parsers, rule engines
│   │   ├── ai/                         # AI engine, providers, validator, prompts
│   │   ├── recommendations/            # Diff generation, verification re-checks
│   │   ├── history/                    # SQLite repository with parameterized queries
│   │   ├── models/                     # Pydantic schemas and enums
│   │   └── core/                       # App settings, logging, errors
│   ├── tests/
│   │   ├── unit/                       # Unit tests (AI, architecture, parsers)
│   │   └── integration/                # Integration tests (platform, API endpoints)
│   └── requirements.txt                # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/                 # UI components (ResultPanel, DiffView, History, etc.)
│   │   ├── services/api.js             # Client API integration
│   │   ├── utils/                      # Validation, clipboard, export
│   │   └── tests/                      # Vitest + RTL test suites
│   ├── package.json
│   └── vite.config.js
└── scripts/
    └── tasks.py                        # Cross-platform setup and test runner
```

---

## 6. Quickstart (≤ 5 Commands)

To run the full stack locally on a fresh clone:

```bash
# 1. Install backend dependencies
pip install -r backend/requirements.txt

# 2. Install frontend dependencies
npm --prefix frontend install

# 3. Create environment configuration
cp .env.example .env

# 4. Start backend API server (runs at http://127.0.0.1:8000)
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# 5. In a second terminal, start frontend dev server (runs at http://127.0.0.1:5173)
npm --prefix frontend run dev
```

Open your browser to `http://127.0.0.1:5173/` to use the dashboard.

---

## 7. Configuration & Environment Variables

Copy `.env.example` to `.env` to configure the system:

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `LLM_PROVIDER` | `mock` | Selected AI provider (`mock`, `anthropic`, `openai`, `disabled`) |
| `LLM_API_KEY` | *(blank)* | API key for Anthropic or OpenAI |
| `LLM_MODEL` | *(blank)* | Model name (e.g. `gpt-4o-mini`, `claude-3-5-sonnet-20241022`) |
| `AI_TIMEOUT_S` | `20` | Per-call timeout in seconds |
| `AI_TOTAL_TIMEOUT_S` | `30` | Total pipeline AI budget |
| `MAX_SOURCE_CHARS` | `20000` | Maximum source code length allowed |
| `MAX_ERROR_CHARS` | `10000` | Maximum error message length allowed |
| `LOG_AI_PAYLOADS` | `false` | Privacy: prevent logging code or prompts |
| `CORS_ORIGINS` | `http://localhost:5173` | Allowed frontend origins |
| `DB_PATH` | `sqlite:///./data/app.db` | SQLite database URI |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API base URL for frontend |

---

## 8. Running Tests & Quality Gates

Run all automated test suites across backend and frontend:

### Backend Test Suite (Pytest)
```bash
python -m pytest backend/tests/ -v --cov=backend/app --cov-report=term
```
- **101 tests passed**.
- **Coverage**: `ai/validator.py` achieves **95%** (gate: ≥ 90%); overall backend achieves **84%** (gate: ≥ 80%).

### Frontend Test Suite (Vitest)
```bash
npm --prefix frontend test -- --run
```
- **35 tests passed** across 5 test suites.

### Architecture Layer Rule Test
```bash
python -m pytest backend/tests/unit/test_architecture.py -v
```
- Enforces downward dependency rules via AST scanning.

---

## 9. Supported Languages & Error Taxonomies

### Languages Supported
1. **Python**: Full static AST parsing, traceback parsing, rule engine matching.
2. **JavaScript**: Stack trace parsing, runtime error classification.
3. **Java**: Compiler diagnostic and runtime exception extraction.

### ErrorType Taxonomy (§5.1)
All errors map strictly into one of 10 standard categories:
- `Syntax`
- `Runtime`
- `Type`
- `Logic`
- `Name / Reference`
- `Dependency`
- `Configuration`
- `Indentation`
- `Import`
- `Unknown / Requires Review`

---

## 10. API Overview & Envelope Standard

Every API response follows the unified envelope pattern:
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

Key Endpoints:
- `GET /api/v1/health`: Health, version, provider status, DB connectivity.
- `GET /api/v1/languages`: Supported languages.
- `POST /api/v1/analyze`: Core hybrid analysis pipeline.
- `GET /api/v1/history`: Stored analyses with search (`q`), filters (`language`, `error_type`, `severity`), and pagination.
- `GET /api/v1/history/{id}`: Single record detail.
- `DELETE /api/v1/history/{id}`: Record deletion.
- `GET /api/v1/analytics/summary`: Aggregate counts, error distributions, and daily trends.
- `GET /api/v1/samples`: Demonstration presets.

For complete API specifications and examples, refer to [docs/api.md](docs/api.md).

---

## 11. Privacy, Security & Prompt Injection Defense

1. **No Code Execution (§11)**: Untrusted code is never compiled, evaluated, or executed (`eval`, `exec`, `shell=True` are strictly forbidden).
2. **Secret Redaction (§7.8)**: Code is sanitized before being passed to external LLM providers. API keys, bearer tokens, and private keys are replaced with `[REDACTED_SECRET]`.
3. **Prompt Injection Guardrails (§7.2)**: User code is wrapped in explicit XML tags (`<source_code>`, `<error_output>`) with system instructions declaring that text inside tags is untrusted data to analyze, not instructions to follow.
4. **Rate Limiting (§11)**: In-memory sliding window rate limiter protects `/analyze` (30 requests/minute) to prevent accidental quota exhaustion.
5. **No Stack Trace Leaks (§5.6)**: Internal exceptions are trapped and returned as sanitized JSON error envelopes with diagnostic `request_id`s.

---

## 12. Limitations & Known Boundaries

- **Local Tool**: Designed for single-developer local usage without multi-tenant authentication.
- **In-Memory Rate Limiting**: The rate limiter counter resets upon application restart.
- **Static Logic Error Limits**: Logic bug detection relies on curated AST heuristics (e.g. constant conditions, loop variable shadows) rather than dynamic symbolic execution.
- **Java / JavaScript Parser Depth**: Python AST analysis is the deepest; Java and JavaScript rely primarily on traceback and error extraction.

---

## 13. Demonstration Walkthrough

Follow the structured 10-minute walkthrough in [docs/demo-script.md](docs/demo-script.md) covering:
1. Python NameError (Undefined Variable with Diff)
2. JavaScript TypeError (Null Dereference)
3. Java NullPointerException
4. Unknown / Ambiguous Error (Anti-Hallucination)
5. AI-Disabled Mode (Verbatim §7.7 Fallback Banner)
6. History Search, Filters, and Analytics Dashboards

---

## 14. Future Work

- Deep Tree-Sitter AST parsers for Java and JavaScript.
- Isolated gVisor/Docker sandbox execution for safe dynamic test execution.
- Interactive multi-turn educational chat grounded on the analyzed failure.
- Native VS Code and IntelliJ IDE extensions.
