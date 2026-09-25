# Project Implementation Plan (Part A)

## Architecture & Technology Stack
- **Backend:** Python 3.11+, FastAPI, Pydantic v2
- **Static Analysis:** `ast`, `tokenize`, `tree-sitter` (Java, JS), `difflib`
- **Data Persistence:** Local SQLite (History & Analytics)
- **AI Integration:** LLM integration via `AIEnginePort` (stubbed by Part A, implemented by Part B). Default `mock`.

## Core Pipeline Flow
`AnalyzeRequest` → `ValidatedRequest` → `NormalizedInput` → `StaticAnalysisResult` → `AIRequestContext` → `AIOutcome` → `Recommendation` → `AnalysisResult`

## Milestones (Part A)
1. **A-M1 (S0 Contract Freeze):** Models, config, errors, ports, stubs, contract fixtures, architecture tests, and data-model docs.
2. **A-M2 (Input Layer):** Validation rules, preprocessor, secret redaction, language registry.
3. **A-M3 (Python Analyzer):** Python AST analyzer, rule engine, primary finding selection.
4. **A-M4 (Java & JS Analyzers):** Tree-sitter parsers, stack trace extractors, logic heuristics.
5. **A-M5 (Recommendation Engine):** difflib diff, static verification re-check, template fallback, fake AI engine tests.
6. **A-M6 (Evaluation):** Golden dataset, eval script, coverage gates, architecture test pass.
7. **A-M7 (Final Docs & Audit):** Finalize docs, cross-review, pass final audit.

## Open Questions & Risks Resolved
- The official contract is `docs/team/PART_A_ANALYSIS_CORE.md` (authoritative).
- Nested folder `AI_Error_Helper/AI_Error_Helper/` remains untouched. Initialization is only at workspace root.
- Python 3.14 pip wheels for `tree-sitter` and grammars are available and require no local compilation. Fallbacks to regex exist if wheels fail.
