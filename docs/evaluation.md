# Evaluation

The system is rigorously evaluated using both unit and integration tests to ensure that the analysis pipeline accurately categorizes and handles failure payloads without crashing.

### Golden Integration Cases
The suite currently includes **15 realistic golden integration cases** that exercise the entire pipeline from request to `AnalysisResult`. These cases cover 8 essential categories:
- Syntax
- Name/Reference
- Logic
- Type
- Import
- Indentation
- Configuration
- Dependency

Currently, **59 out of 59 total tests are passing**, establishing a robust baseline for future development.

### Confidence Model (§6.6)
Static rule analysis applies a strict confidence model based on the evidence collected:
- **CONFIRMED (0.90+)**: Exact AST node matches or stack-trace pinpoint accuracy.
- **PATTERN (0.70+)**: High-probability regex patterns matched against the text.
- **HEURISTIC (0.40+)**: Fuzzy logic or secondary characteristics found.
- **NONE**: Ignored or fully fallback.

### Scope and Limitations
- **D-006 (Java/JS scope reduction)**: Due to strict deadline constraints, Java and JS AST analyzers and the recommendation diff-engine were deferred to future work.
- **D-007 (Configuration/Dependency fallback limitation)**: The `ErrorType` enum defines 10 categories, but the current Python rule engine natively classifies only a subset (Syntax, Runtime, Type, Name/Reference, Import, Indentation, Logic). Configuration and Dependency inputs are handled gracefully (returning a valid `AnalysisResult` without crashing) but fall back to Runtime/Import classification rather than triggering a dedicated category-specific regex rule.
