# API Documentation

The AI-Based Programming Error Helper backend exposes a REST API powered by FastAPI. Every response is wrapped in a consistent JSON envelope (§5.4).

Base URL: `http://127.0.0.1:8000` (configurable via `VITE_API_BASE_URL` on the frontend).

---

## 1. Response Envelope

All endpoints return an envelope containing `success`, `data`, and `error`:

### Success Envelope
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### Error Envelope
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Please provide the source code before analysis.",
    "details": [
      {
        "field": "source_code",
        "message": "Please provide the source code before analysis."
      }
    ],
    "request_id": "req-9b876fc1-34a2"
  }
}
```

Standard error codes:
- `VALIDATION_ERROR` (HTTP 422): Malformed input, missing fields, or size violations.
- `NOT_FOUND` (HTTP 404): Resource does not exist (e.g. unknown analysis ID).
- `RATE_LIMIT_EXCEEDED` (HTTP 429): Rate limit on `/analyze` exceeded (30 requests/minute).
- `INTERNAL_ERROR` (HTTP 500): Unhandled server exceptions (no stack traces leaked).

---

## 2. Endpoints Overview

| Method | Path | Purpose |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health, version, configured AI provider, DB status |
| `GET` | `/api/v1/languages` | Supported programming languages |
| `POST` | `/api/v1/analyze` | Run hybrid error analysis pipeline |
| `GET` | `/api/v1/history` | List stored analyses with query, filters, and pagination |
| `GET` | `/api/v1/history/{id}` | Retrieve single full analysis record |
| `DELETE` | `/api/v1/history/{id}` | Delete single analysis record |
| `GET` | `/api/v1/analytics/summary` | Analytics aggregates and daily trend counts |
| `GET` | `/api/v1/samples` | Curated sample errors for demo/testing |

---

## 3. Endpoint Specifications

### 3.1 Health Check
**`GET /api/v1/health`**

Returns service health, version, AI configuration status, and database connectivity.

**Response (HTTP 200)**:
```json
{
  "success": true,
  "data": {
    "status": "ok",
    "version": "1.0",
    "ai_provider": "mock",
    "ai_configured": true,
    "db_ok": true
  },
  "error": null
}
```

---

### 3.2 Supported Languages
**`GET /api/v1/languages`**

Returns the list of languages supported by the registry.

**Response (HTTP 200)**:
```json
{
  "success": true,
  "data": ["python", "java", "javascript"],
  "error": null
}
```

---

### 3.3 Run Analysis
**`POST /api/v1/analyze`**

Executes the analysis pipeline: Input Validation → Redaction → Static Analysis → AI Engine → Recommendation & Diff → Storage in SQLite.

**Request Body**:
```json
{
  "language": "python",
  "source_code": "total = 0\nfor x in items:\n    total += x\nprint(tottal)\n",
  "error_input": "NameError: name 'tottal' is not defined on line 4",
  "expected_behavior": "Calculate and print the sum of items"
}
```

**Field Constraints**:
- `language`: Required. Must be in `["python", "java", "javascript"]`.
- `source_code`: Required, non-empty, max 20,000 characters.
- `error_input`: Required, non-empty, max 10,000 characters.
- `expected_behavior`: Optional string.

**Response (HTTP 200)**:
```json
{
  "success": true,
  "data": {
    "schema_version": "1.0",
    "analysis_id": "c1f725a3-05ec-4467-93cf-6adab1b83d73",
    "created_at": "2026-09-30T14:20:00Z",
    "language": "python",
    "error_type": "Name / Reference",
    "severity": "HIGH",
    "location": {
      "line": 4,
      "column": 7,
      "end_line": null
    },
    "summary": "Name 'tottal' is used on line 4 but never defined.",
    "explanation": "The script attempts to access 'tottal', which is misspelled and does not exist in the current scope. Variable 'total' was initialized on line 1.",
    "probable_cause": "Typographical error in variable name.",
    "affected_code": "print(tottal)",
    "corrected_code": "total = 0\nfor x in items:\n    total += x\nprint(total)\n",
    "correction_diff": {
      "changed_lines_before": ["print(tottal)"],
      "changed_lines_after": ["print(total)"],
      "unified": "@@ -4,1 +4,1 @@\n-print(tottal)\n+print(total)\n"
    },
    "debugging_steps": [
      "Check the spelling of 'tottal' on line 4.",
      "Compare with the variable declared on line 1 ('total').",
      "Correct the identifier to match the declared name."
    ],
    "prevention_tip": "Enable an IDE linter or spell checker to catch misspelled identifiers before execution.",
    "key_concept": "Variable Scope and Identifier Binding",
    "confidence": 0.85,
    "confidence_basis": [
      "parser-confirmed",
      "traceback agrees with source AST"
    ],
    "uncertainty_note": "Deterministic pattern match from AST static analyzer.",
    "static_findings": [
      {
        "rule_id": "PY-NAME-001",
        "category": "Name / Reference",
        "evidence_level": "PATTERN",
        "source": "rule",
        "message": "Name 'tottal' is used on line 4 but never defined.",
        "location": { "line": 4, "column": 7 },
        "snippet": "print(tottal)",
        "concept": "variable scope"
      }
    ],
    "ai_suggestions": [
      {
        "kind": "explanation",
        "text": "NameError occurs because 'tottal' is not defined in local or global namespaces.",
        "provenance": "ai"
      }
    ],
    "verification": {
      "corrected_code_parses": true,
      "original_finding_resolved": true,
      "note": "Passes syntax/static re-check. This is NOT proof of correct behavior."
    },
    "provenance": {
      "error_type": "static",
      "severity": "static",
      "location": "static",
      "explanation": "ai",
      "corrected_code": "ai",
      "debugging_steps": "ai",
      "prevention_tip": "ai"
    },
    "ai_status": "mock",
    "analysis_metadata": {
      "analysis_mode": "hybrid",
      "pipeline_version": "1.0",
      "prompt_version": "v1",
      "provider": "mock",
      "model": "canned",
      "ai_latency_ms": 15,
      "analyzers_run": ["python_ast", "traceback_parser", "rule_engine"],
      "analyzer_errors": [],
      "warnings": [],
      "history_saved": true
    }
  },
  "error": null
}
```

*Note*: If the AI provider fails, times out, or is disabled, `/analyze` still returns HTTP 200 with `ai_status` set to `unavailable`, `timeout`, or `disabled`, accompanied by deterministic static results.

---

### 3.4 History List
**`GET /api/v1/history`**

Lists stored analysis records with query search, filters, and pagination.

**Query Parameters**:
- `q`: Search string matching `summary`, `error_type`, or `language` (case-insensitive `LIKE`).
- `language`: Filter by language (`python`, `java`, `javascript`).
- `error_type`: Filter by `ErrorType` enum value.
- `severity`: Filter by `Severity` enum value (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, `UNKNOWN`).
- `limit`: Integer (default 20, max 100).
- `offset`: Integer (default 0).

**Response (HTTP 200)**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "analysis_id": "c1f725a3-05ec-4467-93cf-6adab1b83d73",
        "created_at": "2026-09-30T14:20:00Z",
        "language": "python",
        "error_type": "Name / Reference",
        "severity": "HIGH",
        "line": 4,
        "summary": "Name 'tottal' is used on line 4 but never defined.",
        "ai_status": "mock"
      }
    ],
    "total": 1,
    "limit": 20,
    "offset": 0
  },
  "error": null
}
```

---

### 3.5 Single History Item
**`GET /api/v1/history/{id}`**

Retrieves the complete `AnalysisResult` JSON previously stored.

**Response (HTTP 200)**: Returns `AnalysisResult` data envelope.
**Response (HTTP 404)**: If ID is not found:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "NOT_FOUND",
    "message": "Analysis record 'invalid-id' not found.",
    "details": [],
    "request_id": "req-abc123"
  }
}
```

---

### 3.6 Delete History Item
**`DELETE /api/v1/history/{id}`**

Deletes an analysis record from SQLite.

**Response (HTTP 200)**:
```json
{
  "success": true,
  "data": { "deleted": true, "analysis_id": "c1f725a3-05ec-4467-93cf-6adab1b83d73" },
  "error": null
}
```

---

### 3.7 Analytics Summary
**`GET /api/v1/analytics/summary`**

Provides aggregate counts and daily activity trends derived from the SQLite analyses table.

**Response (HTTP 200)**:
```json
{
  "success": true,
  "data": {
    "total": 42,
    "by_error_type": {
      "Name / Reference": 18,
      "Syntax": 12,
      "Type": 8,
      "Runtime": 4
    },
    "by_language": {
      "python": 30,
      "javascript": 8,
      "java": 4
    },
    "by_severity": {
      "HIGH": 20,
      "MEDIUM": 14,
      "LOW": 8
    },
    "by_ai_status": {
      "ok": 32,
      "mock": 8,
      "unavailable": 2
    },
    "daily_counts": [
      { "date": "2026-09-28", "count": 12 },
      { "date": "2026-09-29", "count": 15 },
      { "date": "2026-09-30", "count": 15 }
    ],
    "recent": [
      {
        "analysis_id": "c1f725a3-05ec-4467-93cf-6adab1b83d73",
        "created_at": "2026-09-30T14:20:00Z",
        "language": "python",
        "error_type": "Name / Reference",
        "severity": "HIGH",
        "summary": "Name 'tottal' is used on line 4 but never defined."
      }
    ]
  },
  "error": null
}
```

---

### 3.8 Sample Errors
**`GET /api/v1/samples`**

Returns curated demonstration samples for quick frontend scenario loading.

**Response (HTTP 200)**:
```json
{
  "success": true,
  "data": [
    {
      "id": "py-sample-1",
      "title": "Python: Undefined Variable (NameError)",
      "language": "python",
      "source_code": "def calculate_average(numbers):\n    total = sum(numbers)\n    return tottal / len(numbers)\n",
      "error_input": "NameError: name 'tottal' is not defined"
    }
  ],
  "error": null
}
```
