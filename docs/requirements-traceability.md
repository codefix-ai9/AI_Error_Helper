# Requirements Traceability Matrix

This document maps all architectural, functional, and security requirements to their corresponding implementation files and automated test suites.

---

## Part A Requirements (Analysis Core)

| REQ-ID | Requirement | Module | Implemented In | Tested In | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-005** | Preprocessing, ANSI strip, BOM removal, secret redaction | `preprocessing` | `backend/app/preprocessing/preprocessor.py`, `redaction.py` | `backend/tests/unit/test_preprocessor.py`, `test_redaction.py` | **Complete** |
| **REQ-006** | 10-category ErrorType taxonomy | `models` | `backend/app/models/enums.py` | `backend/tests/unit/test_fixtures_match_contract.py` | **Complete** |
| **REQ-007** | Python AST & Traceback Static Analysis | `analysis` | `backend/app/analysis/` | `backend/tests/unit/test_python_parser.py`, `test_rule_engine.py` | **Complete** |
| **REQ-010** | Authority Lock (Static evidence dictates category/severity/line) | `recommendations` | `backend/app/recommendations/engine.py` | `backend/tests/unit/test_recommendation.py` | **Complete** |
| **REQ-014** | Server-side difflib diff generation | `recommendations` | `backend/app/recommendations/diff_engine.py` | `backend/tests/unit/test_recommendation.py` | **Complete** |

---

## Part B Requirements (AI Engine, Platform, Dashboard)

| REQ-ID | Requirement | Module | Implemented In | Tested In | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-001** | Modern Web UI Dashboard with §10 layout & responsive panels | `frontend` | `frontend/src/App.jsx`, `frontend/src/components/` | `frontend/src/tests/App.test.jsx`, `ResultPanel.test.jsx` | **Complete** |
| **REQ-002** | Language selection & multi-language input | `frontend` / `api` | `frontend/src/components/CodeInput.jsx`, `backend/app/api/routers/languages.py` | `backend/tests/integration/test_platform.py`, `frontend/src/tests/validation.test.js` | **Complete** |
| **REQ-003** | Client-side input validation matching §5.6 rules | `frontend` | `frontend/src/utils/validation.js` | `frontend/src/tests/validation.test.js` | **Complete** |
| **REQ-004** | Consistent JSON response envelope (`success`, `data`, `error`) | `backend/api` | `backend/app/models/envelope.py`, `backend/app/main.py` | `backend/tests/integration/test_platform.py` | **Complete** |
| **REQ-008** | AI Engine with Provider abstraction (Mock, Anthropic, OpenAI) | `backend/ai` | `backend/app/ai/providers/`, `backend/app/ai/engine.py` | `backend/tests/unit/test_ai_engine.py` | **Complete** |
| **REQ-009** | Strict AI JSON validation & 1 repair attempt (§7.4) | `backend/ai` | `backend/app/ai/validator.py`, `backend/app/ai/schemas.py` | `backend/tests/unit/test_ai_engine.py` | **Complete** |
| **REQ-011** | Prompt-injection defense using delimited tags (`<source_code>`) | `backend/ai` | `backend/app/ai/prompts/system_v1.txt`, `backend/app/ai/engine.py` | `backend/tests/unit/test_ai_engine.py` | **Complete** |
| **REQ-012** | Graceful degradation on AI failure (verbatim §7.7 banner) | `frontend` / `backend` | `frontend/src/components/AIUnavailableBanner.jsx`, `backend/app/ai/engine.py` | `frontend/src/tests/ResultPanel.test.jsx`, `test_platform.py` | **Complete** |
| **REQ-013** | Explicit provenance badges (`STATIC FACT`, `AI ASSISTED`, `DERIVED`) | `frontend` | `frontend/src/components/ProvenanceBadge.jsx`, `ResultPanel.jsx` | `frontend/src/tests/ResultPanel.test.jsx` | **Complete** |
| **REQ-015** | SQLite History persistence, parameterized search, pagination & delete | `backend/history` | `backend/app/history/repository.py`, `backend/app/api/routers/history.py` | `backend/tests/integration/test_platform.py`, `frontend/src/tests/HistoryView.test.jsx` | **Complete** |
| **REQ-016** | Analytics summary counts, error distributions & daily trends | `backend/analytics` | `backend/app/api/routers/analytics.py`, `frontend/src/components/AnalyticsView.jsx` | `backend/tests/integration/test_platform.py` | **Complete** |
| **REQ-017** | Absolute security against executing untrusted code | `backend/core` | Code execution strictly forbidden across entire codebase | `backend/tests/unit/test_architecture.py` | **Complete** |
| **REQ-018** | In-memory rate limiting (30 req/min on `/analyze`) | `backend/main` | `backend/app/main.py` | `backend/tests/integration/test_platform.py` | **Complete** |
| **REQ-019** | Layer architecture enforcement & test coverage gates | `backend/tests` | `backend/tests/unit/test_architecture.py` | Pytest architecture test suite | **Complete** |
| **REQ-020** | Copy to clipboard & export results as JSON / plain text | `frontend` | `frontend/src/utils/clipboard.js`, `frontend/src/utils/export.js` | `frontend/src/tests/ResultPanel.test.jsx` | **Complete** |
