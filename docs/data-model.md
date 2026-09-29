# Data Model

The pipeline transforms raw incoming HTTP payloads strictly across domain-driven DTOs (Data Transfer Objects), ensuring robust type validation via Pydantic at every internal boundary.

### Pipeline Stage DTO Sequence
Data propagates through the backend using the following structured sequence:
1. **`AnalyzeRequest`**: The raw incoming payload (language, source code, error text).
2. **`ValidatedRequest`**: The payload after passing security and size constraints.
3. **`NormalizedInput`**: Preprocessed text (secrets redacted, line numbers preserved).
4. **`StaticAnalysisResult`**: The output of the static `RuleEngine` (AST and tracebacks).
5. **`AIRequestContext`**: The compiled context block forwarded to the external LLM provider.
6. **`AIOutcome`**: The unstructured or semi-structured raw response parsed from the LLM.
7. **`Recommendation`**: The synthesized diff or plain-text suggestion for fixing the error.
8. **`AnalysisResult`**: The final payload sent back to the API client, merging all context.

### The ErrorType Categories
To maintain a strict and deterministic frontend contract, errors are rigidly mapped into one of 10 defined enum `ErrorType` categories:
1. `Syntax`
2. `Runtime`
3. `Type`
4. `Logic`
5. `Name / Reference`
6. `Dependency`
7. `Configuration`
8. `Indentation`
9. `Import`
10. `Unknown / Requires Review`
