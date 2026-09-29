PART B — AI ENGINE + PLATFORM + DASHBOARD
AI-Based Programming Error Helper — 2-person split
> You are the lead engineer for \\\*\\\*Part B\\\*\\\*. A second engineer (\\\*\\\*Person A\\\*\\\*, separate agent session) builds \\\*\\\*Part A\\\*\\\* (analysis core) in parallel. This file is self-contained. Section numbers (§) match `docs/team/MASTER\\\_PROMPT\\\_v2.md` (read-only reference, present in the repo). \\\*\\\*Sections not included below belong to Part A — do not implement them.\\\*\\\*
---
B. Split Overrides (these beat the master wherever they differ)
Do NOT run Phase 0. Gate 0 is done once in Part A's session. Read `docs/plan.md` and `docs/decisions.md`. If they don't exist yet, you may only scaffold `frontend/` (B-M1) — then wait.
Milestones: use `B-M1 … B-M6` (§B4) instead of master §15.
Logs: your verification log is `docs/verification-log-part-b.md`. In `docs/requirements-traceability.md` fill only the rows under the heading "Part B".
Never edit Part A folders. If you need something from A, append a line to `docs/team/requests.md` (`For A: …`), keep working against fixtures/fakes, and carry on.
Contract changes (`models/`, `core/`, `application/ports.py`, `data/contract\\\_fixtures/`) → PR labelled `contract-change`, needs Person A's approval, bump `schema\\\_version`.
§7.6 (correction verification) and §7.7 (template-based fallback text) belong to Part A. Your UI still shows the §7.7 banner text verbatim whenever `ai\\\_status ∈ {disabled, unavailable, timeout, invalid\\\_response}`.
Commit prefix: `feat(b): …`, `test(b): …`, `docs(b): …`. Work on branch `feat/part-b-ai-ui`; merge to `main` in small PRs, tests green, rebase daily.
Shared append-only files (`requirements.txt`, `.env.example`, `scripts/tasks.py`, `package.json` scripts, `.gitignore`): edit only inside your own labelled block (`# --- Part B ---`).
---
B1. Ownership
You OWN	FROZEN after S0 (change only via `contract-change` PR)	Part A owns — do NOT edit
`backend/app/{api,ai,history,analytics}/` · `backend/app/main.py` (after S0) · `frontend/` · `README.md` · frontend `npm` scripts · tests for all of these · docs: `api.md`, `ai-pipeline.md`, `demo-script.md`, `viva-prep.md`, `verification-log-part-b.md`	`backend/app/models/` · `backend/app/core/` · `backend/app/application/ports.py` · `data/contract\\\_fixtures/`	`backend/app/{validation,preprocessing,collector,analysis,recommendations,application}/` · `data/sample\\\_errors.json` · docs: `architecture.md`, `data-model.md`, `evaluation.md`, `testing.md`
---
B2. Interfaces between A and B
```python
# backend/app/application/ports.py   (created by Person A at S0; frozen afterwards)
class AIEnginePort(Protocol):
    def explain(self, ctx: AIRequestContext) -> AIOutcome: ...    # NEVER raises; failures become AIOutcome.status
class HistoryPort(Protocol):
    def save(self, result: AnalysisResult) -> bool: ...           # False on storage failure; NEVER raises
class AnalysisServicePort(Protocol):
    def analyze(self, request: AnalyzeRequest) -> AnalysisResult: ...
```
You provide: a real `AIEnginePort` and `HistoryPort`, exposed only through two factories with fixed names: `ai.engine.build\\\_ai\\\_engine(settings)` and `history.repository.build\\\_history\\\_repository(settings)`. Person A creates stub versions at S0 — you replace their bodies (you own those folders).
You consume: `AnalysisServicePort` via `Depends(get\\\_analysis\\\_service)` from `application/container.py`. Your `/analyze` route is thin (validate envelope → call service → wrap response). Test routes with FastAPI `dependency\\\_overrides` and a fake service; never wait for Part A.
`AIRequestContext` is built by Part A (already redacted). You only consume it: build the prompt from it, call the provider, validate, and return an `AIOutcome`.
Layer rule (architecture test): `ai/` never imports `analysis/`; only `application/` wires things together.
---
B3. Until the contract is frozen (S0)
Only `frontend/` scaffolding (B-M1) is safe: Vite + React shell, layout, language select, inputs, client-side validation. Use a temporary local fixture shaped like §5.3. When tag `contracts-v1` lands, switch to `data/contract\\\_fixtures/\\\*.json` via `VITE\\\_USE\\\_FIXTURES=true` (UI works with no backend) and delete the temporary fixture.
---
B4. Milestones (each needs evidence in `verification-log-part-b.md`)
ID	Scope	Exit criteria
B-M1	Frontend shell + client validation + fixture mode (parallel with A-M1)	`npm run dev` works on this OS; validation tests green; UI renders all three result fixtures
B-M2	AI engine (after S0): `MockProvider` first, then `AnthropicProvider` / `OpenAICompatibleProvider`; versioned prompts; `AIExplanation` schema; validator with one repair attempt; timeouts + retry; injection-safe prompt; `build\\\_ai\\\_engine`	all AI tests green via mock/fake transport (valid, missing field, wrong type, invalid JSON, fenced JSON, truncated, timeout, 5xx, 429 retry, repair ok/fail, oversize `corrected\\\_code`, prompt injection); real-provider smoke test only if a key exists (else NOT VERIFIED) → Sync S2
B-M3	Platform: SQLite `HistoryRepository`, history + analytics services, every route in §5.5 (incl. thin `/analyze`, `/samples`, `/health`), envelope on all errors, CORS allow-list, rate limit, `request\\\_id`	API + repository tests green; responses match `contract\\\_fixtures`; no stack-trace leakage test
B-M4	Dashboard complete: every §10 section and state, before/after diff view, provenance labels, MOCK MODE badge, AI-unavailable banner, history page, analytics page, copy/export	manual walkthrough (one scenario per language) against fixtures, then against the real backend at S1/S2
B-M5	Test completeness: frontend tests (Vitest + RTL), API tests, coverage gate for your packages (≥ 90% on `ai/validator`)	all green
B-M6	Your docs, `README.md` assembly (request module notes from A via `requests.md`), demo script, viva prep, S3 cross-review + final audit (§18)	docs match reality
---
B5. Your test scope
AI provider/validator/repair/fallback-trigger tests · prompt-injection tests · API tests for every endpoint (happy + unhappy, envelope consistency, AI failure still `200` with `ai\\\_status`) · rate-limit test · history search/filter/pagination/delete · analytics counts and daily trend · storage-failure path (`history\\\_saved=false`) · frontend tests (validation messages, double-submit blocked, provenance labels, AI-unavailable banner, error states, history filter → API params, export content). Part A owns analysis, recommendation, orchestrator, eval.
---
B6. Sync points you participate in
S0 (A delivers contract; you review and approve) → S1 (A's A-M3 static-only backend; you run the UI against it, log results) → S2 (your AI engine + persistence + A's recommendation wiring; full hybrid in mock mode, one scenario per language) → S3 (cross-review, fresh-clone test, final audit).
At each sync, write the result (command, output summary, date) in your verification log.
---
> \\\*\\\*Reference sections below are copied verbatim from the master prompt (section numbers preserved).\\\*\\\* A missing number means that section belongs to the other part.

---
0. Project Parameters (fill before use)
Key	Value
`REPORT\\\_PATH`	`docs/report/<your-report-file>`
`LLM\\\_PROVIDER`	`mock` | `anthropic` | `openai` (default `mock` until a key is in `.env`)
`LLM\\\_MODEL`	read from `.env` (`LLM\\\_MODEL`) — never hard-code a model string in code
`TARGET\\\_OS`	Windows, macOS and Linux must all work
`APPROVAL\\\_MODE`	`plan-only` (default: stop for human approval only at Gate 0) | `every-milestone` (also stop after each milestone)
---
1. Mission and Success Criteria
Build a runnable, tested, documented local dashboard that helps students understand programming errors with a hybrid pipeline: deterministic analysis first, AI-assisted teaching second.
It is done only when an evaluator can, on a fresh clone:
Run setup + start in ≤ 5 commands (documented in README).
Analyze a sample error in each supported language and see detected facts visibly separated from AI content.
Switch AI off (or break it) and still get an educational, deterministic result.
Read tests, an eval report and a verification log that prove every claim made in the docs.
You are the lead engineer (architecture, backend, frontend, QA, docs). Optimize for correct, understandable, maintainable, demonstrable — not for maximum complexity.
---
2. Operating Rules
2.1 Precedence (highest wins)
Official project report (`REPORT\\\_PATH`) — the contract.
Security and truthfulness rules (§2.2, §11).
Architecture lock (§4).
Specifics in this prompt.
Your own judgment.
Conflicts: the report wins. Log every conflict and decision in `docs/decisions.md` (ID, context, decision, reason). Ask the human only if it changes architecture, scope, or a public contract.
2.2 Evidence protocol (anti-hallucination)
"Implemented" = the file exists and you opened it after writing.
"Passes" = you ran the command, saw exit code 0, and logged command + result in `docs/verification-log.md`.
"AI works" = a real provider call succeeded (provider + model recorded). Otherwise say "mock mode".
Never fabricate: test results, metrics, screenshots, DB rows, AI responses, benchmarks. Metrics come only from `python scripts/tasks.py eval`.
If you could not verify something, write "NOT VERIFIED" and why.
2.3 Autonomy
Ask only when blocked or materially ambiguous. Batch all questions in one message, each with a proposed default ("I will assume X unless you object").
Otherwise decide, log in `decisions.md`, keep moving.
Same failure after 3 distinct fix attempts → stop, report hypotheses and evidence.
2.4 Working discipline
Inspect before modifying. Never overwrite existing files without reviewing the diff.
Search the repo before writing new code; reuse or extend, never duplicate.
Fix at the responsible layer, smallest change. Never weaken validation, loosen a schema, or delete/skip a test to get green.
Small functions, typed interfaces, no hidden global state, no magic values (put in `core/config.py`), no dead code, no unused dependencies.
Pin dependency versions. Use `pathlib` and explicit UTF-8 everywhere (Windows-safe).
2.5 Skills and tools
At the start, list the skills/plugins/MCP tools available in this environment. Use those that reduce risk (planning, TDD, code review, debugging, doc generation). Do not invoke tools for show.
2.6 Scope discipline
Build what the report specifies. Report-stated future scope and any good extra idea go to `docs/future-work.md` — not into code. See non-goals in §17.
---
4. Architecture Lock
```text
USER
 ↓
DASHBOARD / PRESENTATION LAYER            (React)
 ↓
API / APPLICATION SERVICE LAYER           (FastAPI routes → services)
 ↓
INPUT VALIDATION + PREPROCESSING
 ↓
PROGRAMMING ANALYSIS LAYER  ↔  ERROR RULES / PARSERS / LINTERS
 ↓
AI ANALYSIS ENGINE          ↔  MODEL / AI SERVICE
 ↓
RESULT VALIDATION + RECOMMENDATION
 ↓
RESULT DISPLAY IN DASHBOARD
```
Do not redesign, merge layers, or move responsibilities between modules without explicit approval.
4.1 Module map
#	Module	Location	Responsibility (and what it must NOT do)
1	Dashboard / UI	`frontend/`	Layout, input, results, history, analytics, copy/export. No analysis logic.
2	Code Input	`frontend` CodeInput component + `CodeInput` DTO	Capture code with formatting preserved; send structured input. Never analyzes.
3	Error Collector	`frontend` ErrorInput + backend `collector`	Accept compiler/runtime/console/traceback/observed-problem text; classify the input kind and split into structured `ErrorRecord`s.
4	Preprocessor	`backend/app/preprocessing`	Text hygiene only: line endings, BOM, ANSI codes, tabs, trailing noise; preserves source line numbers; makes a redacted copy for AI. Never changes source semantics.
5	Static / Error Analyzer	`backend/app/analysis`	Deterministic findings. Must not import `ai`.
6	AI Analysis Engine	`backend/app/ai`	Explain findings. Receives DTOs only, must not import `analysis` internals.
7	Recommendation Engine	`backend/app/recommendations`	Merge facts + AI, produce final result with provenance.
8	Validation & Error Handling	`backend/app/validation`, `core/errors.py`	Request/AI/schema validation, error envelope, graceful degradation.
4.2 Layer rules (enforced by a test)
Dependencies point downward only: `api → application → {validation, preprocessing, analysis, ai, recommendations, history, analytics} → models/core`. Add `tests/unit/test\\\_architecture.py` that scans imports with `ast` and fails on: `analysis` importing `ai`, `ai` importing `analysis`, anything importing `api`, `frontend` logic duplicating backend rules.
4.3 Pipeline stage contracts (typed Pydantic models / dataclasses)
```text
AnalyzeRequest
 → ValidatedRequest
 → NormalizedInput      {language, source\\\_code (line-preserving), error\\\_records\\\[], error\\\_text\\\_clean, redaction\\\_report}
 → StaticAnalysisResult {findings\\\[], primary\\\_finding, error\\\_type, severity, location, evidence\\\_level,
                         corroborated, analyzers\\\_run\\\[], analyzer\\\_errors\\\[]}
 → AIRequestContext     (built from the above; redacted)
 → AIOutcome            {status, payload|None, provider, model, latency\\\_ms, repair\\\_attempts, warnings\\\[]}
 → Recommendation       (merged fields + provenance)
 → AnalysisResult       (public contract §5.3) → persisted → returned
```
Each stage: one class or pure function, typed in/out, unit-testable in isolation. The orchestrator lives only in `application/services/analysis\\\_service.py`.
---
5. Contracts (define BEFORE integrating frontend and backend)
5.1 Enums
`Language`: `python`, `java`, `javascript` (registry-driven; report may override the list)
`ErrorType`: `Syntax`, `Runtime`, `Type`, `Logic`, `Name / Reference`, `Dependency`, `Configuration`, `Indentation`, `Import`, `Unknown / Requires Review`
Dependency = third-party package/module not installed or version problem. Import = wrong import statement, circular import, bad relative path.
`Severity`: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, `UNKNOWN`
`EvidenceLevel`: `CONFIRMED` (parser/compiler-proven), `PATTERN` (AST/rule match), `HEURISTIC`, `NONE`
`AIStatus`: `ok`, `mock`, `disabled`, `unavailable`, `timeout`, `invalid\\\_response`
`Provenance`: `static`, `ai`, `derived`
5.2 Request — `POST /api/v1/analyze`
```json
{
  "language": "python",
  "source\\\_code": "...",
  "error\\\_input": "...",
  "expected\\\_behavior": "optional free text (+ additive)"
}
```
`error\\\_input` = compiler/runtime error, traceback, console output, wrong-output description or observed problem (one field, as the original spec).
5.3 Result (`data`) — original fields kept; (+) = additive
```json
{
  "schema\\\_version": "1.0",                       // (+)
  "analysis\\\_id": "uuid4",
  "created\\\_at": "2026-01-01T10:00:00Z",          // (+) UTC
  "language": "python",
  "error\\\_type": "Name / Reference",
  "severity": "HIGH",
  "location": {"line": 8, "column": null, "end\\\_line": null},
  "summary": "One line, <=120 chars, deterministic",   // (+) used by history
  "explanation": "...",
  "probable\\\_cause": "...",
  "affected\\\_code": "...",
  "corrected\\\_code": "...",
  "correction\\\_diff": {"changed\\\_lines\\\_before": \\\[], "changed\\\_lines\\\_after": \\\[], "unified": "..."},  // (+) server-side difflib
  "debugging\\\_steps": \\\[],
  "prevention\\\_tip": "...",
  "key\\\_concept": "e.g. variable scope",          // (+)
  "confidence": 0.75,
  "confidence\\\_basis": \\\["parser-confirmed", "error text agrees with source"],   // (+)
  "uncertainty\\\_note": "...",
  "static\\\_findings": \\\[ { "rule\\\_id": "PY-NAME-001", "category": "Name / Reference", "evidence\\\_level": "PATTERN",
                         "source": "rule", "message": "Name 'total' is used on line 8 but never defined.",
                         "location": {"line": 8, "column": 12}, "snippet": "print(total)", "concept": "variable scope" } ],
  "ai\\\_suggestions": \\\[ { "kind": "explanation|correction|debug\\\_step|prevention|suggested\\\_category", "text": "...", "provenance": "ai" } ],
  "verification": {                              // (+) static checks only, never execution
    "corrected\\\_code\\\_parses": true,
    "original\\\_finding\\\_resolved": true,
    "note": "Passes syntax/static re-check. This is NOT proof of correct behavior."
  },
  "provenance": {"error\\\_type": "static", "severity": "static", "location": "static",
                 "explanation": "ai", "corrected\\\_code": "ai", "debugging\\\_steps": "ai", "prevention\\\_tip": "ai"},  // (+)
  "ai\\\_status": "ok",                             // (+)
  "analysis\\\_metadata": {"analysis\\\_mode": "hybrid|static\\\_only", "pipeline\\\_version": "", "prompt\\\_version": "",
                        "provider": "", "model": "", "ai\\\_latency\\\_ms": 0, "analyzers\\\_run": \\\[],
                        "analyzer\\\_errors": \\\[], "warnings": \\\[], "history\\\_saved": true}
}
```
Rules: unavailable field → explicit `null`, `\\\[]`, or documented state. Never invent. Contract changes require a `schema\\\_version` bump + `docs/data-model.md` update.
5.4 Envelope (every response, every endpoint)
```json
{"success": true, "data": {}, "error": null}
{"success": false, "data": null, "error": {"code": "VALIDATION\\\_ERROR", "message": "Please provide the source code before analysis.", "details": \\\[{"field": "source\\\_code", "message": "..."}], "request\\\_id": "..."}}
```
Override FastAPI's default validation handler so all errors use this envelope. AI failure is not an HTTP error: return `200` with `ai\\\_status` ≠ `ok` and a static-only result.
5.5 Endpoints (no others)
Method	Path	Purpose
GET	`/api/v1/health`	status, version, `ai\\\_provider`, `ai\\\_configured`, `db\\\_ok`
GET	`/api/v1/languages`	supported languages from registry
POST	`/api/v1/analyze`	run pipeline
GET	`/api/v1/history`	list; query: `q`, `language`, `error\\\_type`, `severity`, `limit`, `offset`
GET	`/api/v1/history/{id}`	full stored result
DELETE	`/api/v1/history/{id}`	delete one record
GET	`/api/v1/analytics/summary`	counts + trends (§9)
GET	`/api/v1/samples`	demo helper serving `data/sample\\\_errors.json` (kept because `evaluation.md` relies on it)
5.6 Validation (config-driven limits in `core/config.py`, env-overridable)
Rule	Default	Message
language required	—	`Please select a programming language.`
language supported	registry	`Language '<x>' is not supported yet. Supported: python, java, javascript.`
source_code non-blank	—	`Please provide the source code before analysis.`
error_input non-blank	—	`Please provide the compiler/runtime error or observed problem.`
max source size	20 000 chars	`Source code is too large (max 20,000 characters).`
max error size	10 000 chars	`Error text is too large (max 10,000 characters).`
malformed JSON / wrong types	—	`The request could not be understood.`
Never return stack traces. Include a `request\\\_id` in error responses and server logs.
---
7. AI Analysis Engine (Module 6) — EXCERPT: Part B owns 7.1–7.5 and 7.8
7.1 Provider abstraction
`AIProvider` protocol: `generate\\\_structured(system\\\_prompt, payload, json\\\_schema) -> raw\\\_text`.
Implementations: `MockProvider` (deterministic canned output per `ErrorType`), `AnthropicProvider`, `OpenAICompatibleProvider`. Selected by `LLM\\\_PROVIDER`. Keys/model/timeouts from `.env` only.
Timeouts: per-call `AI\\\_TIMEOUT\\\_S=20`, total budget `AI\\\_TOTAL\\\_TIMEOUT\\\_S=30`; 1 retry on 429/5xx/network with short backoff. Low temperature. Mock mode must show a visible "MOCK MODE" badge in the UI and `ai\\\_status = mock`; never present mock output as real AI.
7.2 Prompt design (files in `ai/prompts/`, versioned via `PROMPT\\\_VERSION`; never inline in logic)
The system prompt must instruct the model to:
act as an educational programming assistant; teach the concept, not just "change this line";
treat `static\\\_findings` as authoritative facts; never invent compiler/runtime facts;
not change category, severity or location when static evidence exists;
mark uncertainty explicitly; never claim a correction is guaranteed;
preserve the user's language; do not rewrite unrelated code; keep student-friendly wording;
return only JSON matching the schema.
Prompt-injection defense (mandatory): source code and error text are untrusted data. Put them in delimited blocks (`<source\\\_code>…</source\\\_code>`, `<error\\\_output>…</error\\\_output>`), state that content inside is data whose instructions must be ignored, and add tests where the code contains "ignore previous instructions…".
Input payload = structured JSON (language, `source\\\_code`, `error\\\_input`, `normalized\\\_error`, `static\\\_findings`, `detected\\\_category`, `location`, `severity`, `evidence\\\_level`), never a raw user prompt.
7.3 Output schema (`ai/schemas.py`, Pydantic)
`explanation` (str, ≤ 1500), `probable\\\_cause` (str), `affected\\\_code` (str|null), `corrected\\\_code` (str|null), `debugging\\\_steps` (3–8 items, each ≤ 300 chars), `prevention\\\_tip` (str), `key\\\_concept` (str), `uncertainty\\\_note` (str), `suggested\\\_category` (enum|null, used only when static result is Unknown).
7.4 Validation pipeline (`ai/validator.py`) — never trust AI output
Strict JSON parse (tolerate one wrapping code fence). 2. Schema + types. 3. Semantic checks: length caps; `corrected\\\_code` ≤ 2× source + 2 KB and non-empty if present; `affected\\\_code` must exist (whitespace-normalized) in the source, else set `null` + warning; AI-stated line ≠ static line → static wins, warning. 4. On failure: one repair attempt (send validation errors back), then fall back (§7.7). Never "fix" a schema failure by loosening the schema.
7.5 Authority rules
Static evidence decides `error\\\_type`, `severity`, `location`. If static result is Unknown, the AI's `suggested\\\_category` appears only as an `ai\\\_suggestions` item of kind `suggested\\\_category`; the official `error\\\_type` stays `Unknown / Requires Review`.
7.8 Privacy
Redact obvious secrets (API-key-like strings, `password=`/`token=` values, private-key blocks) from the AI copy and record `redaction\\\_report`. Disclose in README and UI footnote that code is sent to the configured LLM provider. Do not log code, error text or prompts by default (log sizes, hashes, latency); `LOG\\\_AI\\\_PAYLOADS=false`.
---
9. Persistence, History, Analytics
SQLite via stdlib `sqlite3` behind a `HistoryRepository` interface (file `data/app.db`, git-ignored). Parameterized queries only.
Table `analyses`: `id` PK, `created\\\_at` (UTC ISO-8601), `language`, `error\\\_type`, `severity`, `line`, `summary`, `ai\\\_status`, `result\\\_json`. Indexes on `created\\\_at`, `language`, `error\\\_type`.
Search `q` matches `summary`, `error\\\_type`, `language` (`LIKE`, parameterized). Filters: language, error_type, severity. Pagination.
Storage failure is non-fatal: return the result with `history\\\_saved=false` + warning.
Never store API keys or `.env` content.
`GET /analytics/summary` returns: `total`; `by\\\_error\\\_type`; `by\\\_language`; `by\\\_severity`; `by\\\_ai\\\_status`; `daily\\\_counts` (last 30 days, UTC); `recent` (last 10). Derived from stored records only. Basic — no enterprise analytics.
---
10. Dashboard (Module 1)
Stack: React + JavaScript (JSX) + HTML/CSS via Vite (plain CSS or CSS Modules; use JSDoc typedefs in `types/` unless the report requires TypeScript). Code area: textarea with line numbers, or CodeMirror 6 if it stays light. Config via `VITE\\\_API\\\_BASE\\\_URL`. No global state library unless clearly needed.
Layout: header + language select → two panes (Code | Error/Console; stacked below 1024 px) → Analyze button → result panel → History and Analytics pages.
Result panel, in order: category · severity · location · confidence chips → Detected by Static Analysis (facts) → AI-Assisted Explanation → probable cause → affected code (detected line highlighted) → AI-Assisted Suggested Correction with side-by-side before/after diff and the `verification` note → debugging steps → prevention tip + key concept → uncertainty/confidence explanation.
Behavior and states: idle · client validation (same messages as §5.6) · loading (disable button, spinner, `AbortController`, 45 s client timeout, cancel) · success · partial (AI unavailable banner) · error (network / backend down / timeout / invalid response, with Retry). Prevent duplicate submits. "Load example" from `/samples`. MOCK MODE badge. Copy result (Clipboard API + fallback) and export (JSON and plain text).
Rules: no analysis logic in the UI; never `dangerouslySetInnerHTML` (render AI text as plain text, code in `<pre>`); labels never rely on color alone; keyboard-navigable, labelled inputs, `aria-live` for status; History: table, debounced search (300 ms), language/type/severity filters, open, delete-with-confirm; Analytics: cards + simple SVG/CSS bars (no heavy chart library).
---
11. Security and Privacy
Secrets only in `.env` (git-ignored); commit `.env.example`. Never print secrets.
Never execute submitted code. No `exec`, `eval`, `pickle`, `importlib` of user code, no `shell=True`, no user-controlled command strings.
Bind to `127.0.0.1` by default; CORS allow-list = dev frontend origin from env only. No auth (local tool) — document this as a limitation.
Size limits (§5.6); simple in-memory rate limit on `/analyze` (e.g. 30/min) to protect API spend.
Safe errors with `request\\\_id`; structured logs without code contents.
Run `pip-audit` / `npm audit` once (if network allows) and record the result in the verification log.
---
12. Testing and Evaluation
12.1 Test matrix (backend `pytest` + `TestClient`; frontend Vitest + React Testing Library)
Area	Minimum cases
Syntax / Indentation	missing colon, unclosed bracket/quote, bad indent, invalid syntax — per language
Runtime	ZeroDivisionError, FileNotFoundError, IndexError/KeyError, NPE, ArrayIndexOutOfBounds
Type	invalid operand types, wrong argument type, `x is not a function`
Name / Reference	undefined variable, undefined function, misspelled name
Import / Dependency	missing module, wrong import path, missing npm package
Logic	each curated heuristic fires; negatives don't fire on correct code
Unknown	ambiguous error → `Unknown / Requires Review`, `confidence=null`
Validation	empty code/error/language, unsupported language, oversize, invalid JSON, wrong types
AI (mock + fake transport)	valid; missing field; wrong type; invalid JSON; fenced JSON; truncated; timeout; 5xx; 429 retry; repair succeeds; repair fails → fallback; oversize `corrected\\\_code`; AI line ≠ static line; prompt-injection in source code
API	every endpoint happy + unhappy path; envelope consistent; no stack trace leakage; AI failure still returns 200 with static result
History / Analytics	save, search, filters, pagination, delete, counts, storage-failure path
Architecture	import-layer test (§4.2)
Frontend	validation messages, double-submit blocked, provenance labels rendered, AI-unavailable banner, error states, history filter → API params, export content
Coverage gate (`pytest-cov`): backend ≥ 80% overall, ≥ 90% for `validation`, `ai/validator`, rule engine.
---
13. Documentation Deliverables
File	Content
`README.md`	Overview, problem, objectives, features, architecture, modules, stack, folder tree, install, `.env`, run (≤ 5 commands), tests, languages, hybrid pipeline, AI architecture, API overview, error handling, privacy note, limitations, evaluation method, future work, demo instructions
`docs/architecture.md`	Layers, module map, data flow, static/AI/validation/recommendation, dashboard comms + Mermaid diagrams (architecture, sequence of `/analyze`, use-case, ER/data model, analyzer-registry class diagram — usable directly in the college report)
`docs/api.md`	Every endpoint: request/response schemas, validation errors, examples (captured from real runs)
`docs/data-model.md`	Result schema, enums, DB schema, versioning
`docs/ai-pipeline.md`	Input → Preprocess → Static → Classify → Structured prompt → LLM → Validate → Recommend → Dashboard; why hybrid (grounding, determinism, cost, graceful failure, evaluability)
`docs/testing.md`	How to run, what each suite covers, manual QA checklist
`docs/evaluation.md`	Evaluator walkthrough for: syntax, runtime, type, name/reference, dependency, logic, invalid input, unsupported language, AI failure, history, analytics — each with input, expected output
`docs/requirements-traceability.md`	`REQ-ID
`docs/decisions.md`, `docs/future-work.md`, `docs/verification-log.md`	Decisions; out-of-scope ideas; real command outputs
`docs/demo-script.md`	10-minute demo: 6 scenarios (3 languages, unknown case, AI-off case, history/analytics) with expected screens
`docs/viva-prep.md`	~20 likely examiner questions with short answers based on the actual implementation
---
14. Repository Layout
```text
ai-programming-error-helper/
├── README.md  .gitignore  .env.example  LICENSE
├── docs/            (files in §13, plus report/ and diagrams/)
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/{routes,dependencies}/
│   │   ├── application/services/
│   │   ├── validation/  preprocessing/  collector/
│   │   ├── analysis/{base.py,registry.py,rules/,parsers/,languages/{python,java,javascript}/}
│   │   ├── ai/{client.py,providers/,prompts/,schemas.py,validator.py}
│   │   ├── recommendations/  history/  analytics/  models/
│   │   └── core/{config.py,errors.py,logging.py}
│   ├── tests/{unit,integration,fixtures}/
│   └── requirements.txt
├── frontend/
│   ├── src/{components,pages,services,hooks,utils,types,styles}/
│   ├── tests/  package.json  vite.config.js
├── data/{sample\\\_errors.json,development/}     (app.db git-ignored)
└── scripts/tasks.py     (cross-platform: setup | test | run | eval | verify)
```
Filenames may adapt; responsibilities may not. `.env.example` keys: `LLM\\\_PROVIDER`, `LLM\\\_API\\\_KEY`, `LLM\\\_MODEL`, `AI\\\_TIMEOUT\\\_S`, `AI\\\_TOTAL\\\_TIMEOUT\\\_S`, `MAX\\\_SOURCE\\\_CHARS`, `MAX\\\_ERROR\\\_CHARS`, `ENABLE\\\_TOOLCHAIN\\\_CHECKS`, `LOG\\\_AI\\\_PAYLOADS`, `CORS\\\_ORIGINS`, `DB\\\_PATH`, `VITE\\\_API\\\_BASE\\\_URL`.
---
16. Reporting and Failure Protocol
After each milestone, reply concisely:
```text
MILESTONE: <id + name>            STATUS: Complete | Blocked | Needs Clarification
IMPLEMENTED: ...
FILES CREATED / MODIFIED: ...
EVIDENCE: <commands run + results, as logged>
ARCHITECTURE CHECK: PASS/FAIL     REPORT FIDELITY: PASS/FAIL
DEVIATIONS / DECISIONS: ...
KNOWN LIMITATIONS: ...
NEXT: ...
```
When something breaks: reproduce → read the error → find root cause → identify responsible layer → smallest fix → targeted test → full regression → architecture test. Do not rewrite the project; do not patch the frontend for a backend bug; do not weaken a schema for an AI bug; do not delete a test.
---
17. Non-Goals (never build unless the report explicitly requires it)
Microservices, Docker/Kubernetes, queues, Redis, GraphQL, cloud infra, user accounts/auth, payments, social/community features, gamification, chatbots unrelated to error analysis, code-generation platform, IDE features, running user code, additional languages beyond the report, ML model training. Report-listed future scope → `docs/future-work.md` only.
---
18. Final Audit (all must be true, each backed by evidence)
[ ] Architecture test passes; layers respected (§4.2).
[ ] Every REQ in the register is Complete / FUTURE / Deferred-with-reason, with implementation + test links.
[ ] `/analyze` returns the §5.3 contract; facts, template guidance and AI text carry correct provenance.
[ ] With `LLM\\\_PROVIDER=disabled` (or a killed provider) the app returns an educational static-only result and the verbatim banner.
[ ] Mock mode is labelled everywhere; no mock output is described as real AI.
[ ] Prompt-injection, oversize, malformed-JSON and timeout tests pass.
[ ] Coverage gate met; `tasks.py eval` produced `docs/evaluation-results.md` from a real run.
[ ] No secrets in repo or git history; `.env.example` complete.
[ ] Docs match the code; API examples came from real responses; fresh-clone test passed.
[ ] Limitations documented honestly (local tool, no auth, small dataset, heuristic logic detection, AI may be wrong).
---
FIRST ACTION (Part B)
Check that `docs/plan.md` and `docs/decisions.md` exist and that Gate 0 was approved. If not: start B-M1 frontend scaffolding only, then wait — do not write backend code.
Reply first with a short Part B plan (≤ 30 lines): frontend structure, AI provider/prompt structure, persistence approach, first 3 tasks, and any question for Person A (batched, with proposed defaults).
Then proceed with B-M1 and continue per §B4 without waiting for approval, unless blocked.