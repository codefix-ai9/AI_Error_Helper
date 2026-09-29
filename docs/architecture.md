# Architecture

The AI Error Helper is designed using a 7-layer pipeline architecture. This pipeline cleanly separates presentation concerns from business logic, analysis, and external integrations.

### The 7-Layer Pipeline

1. **Dashboard**: The frontend application built with React/Vite that provides the user interface for submitting errors and viewing analysis results.
2. **API**: The entry point to the backend (FastAPI), responsible for receiving raw payloads, defining endpoints (`/analyze`), and handling CORS and HTTP error formatting.
3. **Validation**: Enforces strict constraints on inputs before any processing occurs (e.g., verifying language support and maximum text payload bounds).
4. **Analysis**: The core static analysis engine. This layer coordinates AST parsing and tracebacks using the `RuleEngine` to match patterns and categorize the failure natively.
5. **AI Engine**: The abstraction for external LLMs (OpenAI, Gemini). Driven by the `AIEnginePort`, this allows context-aware generative analysis.
6. **Recommendation**: Fuses static analysis confidence with AI suggestions, applying strict deterministic correction logic and diff redaction constraints.
7. **Result**: Packages the final payload into the `AnalysisResult` DTO, logging it to the `HistoryPort` and returning it to the Dashboard.

### Frozen Domain Contracts
To ensure system boundaries are strictly maintained, the system relies on two frozen core interface contracts:
- `AIEnginePort`: Defines the expected contract for any AI generative adapter (currently fulfilled by `NullAIEngine`).
- `HistoryPort`: Defines the contract for long-term telemetry and historical dashboard storage (currently implemented via local SQLite).
