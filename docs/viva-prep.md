# Viva & Examination Preparation Guide

This guide compiles 20 likely examiner questions regarding the AI-Based Programming Error Helper, accompanied by concise answers grounded directly in the implementation.

---

### 1. What is the fundamental architecture of your system?
**Answer**: It is a 7-layer hybrid pipeline: Dashboard UI (React) → API / Envelope Layer (FastAPI) → Input Validation & Preprocessing → Static Analysis (AST, tracebacks, rule engine) → AI Engine (LLM abstraction) → Recommendation & Diff Engine (`difflib`) → Presentation / Persistence (SQLite).

### 2. Why use a hybrid approach instead of sending the code directly to an LLM like ChatGPT?
**Answer**: Pure LLMs suffer from hallucination (inventing non-existent compiler errors or lines), non-determinism, high token costs, and catastrophic failure when offline. Our hybrid pipeline uses deterministic static analysis to ground the facts (line number, category, severity), ensuring the AI only acts as a teacher and cannot contradict proven compiler/runtime facts.

### 3. What is the "Authority Lock" (§7.5)?
**Answer**: It is a strict architectural constraint where static compiler/parser evidence unconditionally dictates the `error_type`, `severity`, and `location`. If the LLM claims an error is on line 12 but the static AST confirms it is on line 4, the static line wins and an advisory warning is flagged.

### 4. How do you protect against prompt injection attacks?
**Answer**: User source code and error messages are untrusted data. We encapsulate them inside explicit delimiters (`<source_code>...</source_code>` and `<error_output>...</error_output>`) within `system_v1.txt`. The system prompt instructs the model that text inside these tags is purely data to analyze, never instructions to execute. We also have automated unit tests verifying that prompt injection attempts do not hijack the model output.

### 5. How do you validate the output received from the AI?
**Answer**: The output passes through `ai/validator.py`:
1. Code fence stripping (` ```json `).
2. Strict JSON parsing and Pydantic schema validation (`AIExplanation`).
3. Length caps and bounds checks.
4. Semantic verification: `affected_code` must exist in the original source, and `corrected_code` cannot exceed `2 * len(source) + 2048` chars.
5. If invalid, exactly one repair attempt is made with error feedback. If repair fails, the system safely falls back.

### 6. What happens if the AI provider goes down or times out?
**Answer**: The `/analyze` endpoint never crashes. It returns HTTP 200 with `ai_status` set to `unavailable` or `timeout`. The frontend displays the verbatim §7.7 banner (*"AI explanation unavailable. Showing deterministic static analysis and rule-based guidance only."*), while preserving all static analysis findings, rule tips, and line highlights.

### 7. How does the frontend differentiate between deterministic facts and AI suggestions?
**Answer**: Every section in the result panel displays explicit provenance badges:
- `STATIC FACT` (green) for compiler-verified facts.
- `AI ASSISTED` (purple) for LLM-generated explanations and suggestions.
- `DERIVED` (blue) for server-side diffs.
This guarantees the student knows exactly which parts are ground truth versus generative guidance.

### 8. Why did you choose SQLite for persistence instead of MongoDB or PostgreSQL?
**Answer**: The project is a local developer tool designed to run with zero external infrastructure setup. SQLite is included in Python's standard library, requires no separate daemon or configuration, and provides full ACID compliance with WAL mode and parameterized indexing for fast local queries.

### 9. How do you prevent SQL injection in history search?
**Answer**: We use parameterized queries exclusively in `history/repository.py` with the standard `sqlite3` driver. Search patterns are passed as parameters (`?`), never concatenated into raw SQL strings.

### 10. Does your application execute student code to verify it?
**Answer**: **Never.** Running untrusted student code is a major security hazard that would allow arbitrary code execution, filesystem tampering, and infinite loops. We only perform static parsing (AST, regex rules) and static re-parsing of corrected code (`ast.parse`).

### 11. How do you prevent sensitive data (like API keys) from leaking to LLMs?
**Answer**: Preprocessing includes a redaction filter (`redaction.py`) that scans for patterns matching API keys, passwords, and private key blocks, replacing them with `[REDACTED_API_KEY]` or `[REDACTED_SECRET]` before the prompt is forwarded to the provider.

### 12. How does the architectural layer test work?
**Answer**: In `tests/unit/test_architecture.py`, Python's `ast` module parses all project imports. It asserts that dependencies only point downward: `analysis` cannot import `ai`, `ai` cannot import `analysis`, and no business logic imports `api`.

### 13. What is the difference between `MockProvider`, `AnthropicProvider`, and `OpenAICompatibleProvider`?
**Answer**: All implement the `AIProvider` protocol. `MockProvider` returns deterministic canned responses per `ErrorType` without network calls. `AnthropicProvider` integrates Anthropic's Claude SDK. `OpenAICompatibleProvider` works with OpenAI models, Gemini's OpenAI-compatible endpoint, or local models via Ollama.

### 14. What rate limiting is in place?
**Answer**: An in-memory rate limiter protects the `/analyze` route (30 requests/minute per IP) to guard against accidental API quota exhaustion. When exceeded, it returns HTTP 429 with standard error envelope formatting.

### 15. How do you handle client-side timeouts?
**Answer**: In `frontend/src/App.jsx`, API requests use native `AbortController` with a 45-second timeout and an explicit **Cancel** button, allowing students to abort long-running requests without freezing the UI.

### 16. How is code diffing performed?
**Answer**: Rather than relying on client-side approximation, the server uses Python's standard `difflib` library to compute unified diffs and extract `changed_lines_before` and `changed_lines_after`. The frontend renders this in side-by-side or unified view.

### 17. How do you measure test coverage?
**Answer**: Using `pytest-cov` on backend packages and Vitest with v8 on the frontend. We enforce a coverage gate of ≥ 90% on `ai/validator` (currently 95%) and ≥ 80% on backend overall (currently 84%).

### 18. What are the key limitations of the current implementation?
**Answer**:
1. Single-user local application (no multi-tenant user authentication by design).
2. Rate limiter resets upon server restart (in-memory).
3. Logic error detection relies on static heuristics rather than dynamic execution traces.
4. Python static analysis is the most comprehensive; Java and JavaScript rely primarily on traceback and error message extraction.

### 19. If you had another 2 weeks, what would you implement next?
**Answer**:
1. Deep AST analysis for Java and JavaScript using Tree-Sitter grammars.
2. Isolated Docker/gVisor sandboxed execution for runtime assertion checking.
3. Interactive follow-up Q&A chat grounded specifically on the analyzed error.
4. IDE extension (VS Code extension) communicating with the local FastAPI daemon.

### 20. What is the response envelope design pattern and why is it used?
**Answer**: Every HTTP response uses `{ "success": boolean, "data": object | null, "error": object | null }`. This ensures uniform client handling across all endpoints, avoids unexpected unhandled exceptions in the frontend, and guarantees that every error payload carries a unique `request_id` for diagnostics without exposing backend stack traces.
