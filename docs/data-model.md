# Data Model & API Contracts (v1.0)

## Enumerations
- **Language**: `python`, `java`, `javascript`
- **ErrorType**: `Syntax`, `Runtime`, `Type`, `Logic`, `Name / Reference`, `Dependency`, `Configuration`, `Indentation`, `Import`, `Unknown / Requires Review`
- **Severity**: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`, `UNKNOWN`
- **EvidenceLevel**: `CONFIRMED`, `PATTERN`, `HEURISTIC`, `NONE`
- **AIStatus**: `ok`, `mock`, `disabled`, `unavailable`, `timeout`, `invalid_response`
- **Provenance**: `static`, `ai`, `derived`

## AnalyzeRequest
```json
{
  "language": "python",
  "source_code": "print(total)",
  "error_input": "NameError: name 'total' is not defined",
  "expected_behavior": "Should print the total value"
}
```

## AnalysisResult
Contains deterministic fields (static_findings), AI suggestions (explanation, debugging_steps, prevention_tip, practice_exercise, quiz_question), correction_diff, verification checks, and analysis_metadata.
*Note: `practice_exercise` and `quiz_question` are additive fields vs the master prompt §5.3 contract.*
See `data/contract_fixtures/result_hybrid_ok.json` for full JSON schema.

## Envelopes
All API responses use:
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```
Or:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "...",
    "details": [],
    "request_id": "uuid"
  }
}
```
