# AI Error Helper

AI Error Helper is a backend service designed to analyze, categorize, and explain programming errors.

## Current Status (S1 Milestone)

The service implements a hybrid analysis architecture:
1. **Static Analysis Phase (A-M3):**
   - Implemented for Python.
   - Includes AST parsing, traceback parsing, and heuristic rule matching.
   - Findings are deduplicated, and a primary finding is selected based on severity, confidence, and specificity.
2. **AI Phase (A-M5):**
   - Currently operating in a minimal "static-only fallback" mode via `NullAIEngine`.
   - The AI engine gracefully returns `status="disabled"`, allowing the orchestrator to fall back to static findings exclusively.

### Language Support
- **Python:** Fully supported by static analyzers (AST, Traceback, Rule Engine).
- **Java / JavaScript:** Supported by the pipeline but gracefully degrade (skip static analysis) as per the A-M4 fast-mode plan.

## Architecture Highlights
- **Authority Lock (§7.5):** The orchestrator strictly enforces that the primary finding determined by static evidence dictates the final `error_type`, `severity`, and `location`. The AI cannot overwrite these core assertions.
- **Pipeline Resilience:** Any internal failure is caught, logged to `analyzer_errors`, and safely returned as a valid `AnalysisResult` without crashing the service.

## Testing
A full suite of unit and integration tests is available under `backend/tests/`. Run them using `pytest backend/tests -v`.
