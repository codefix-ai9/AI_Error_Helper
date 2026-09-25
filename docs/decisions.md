# Architecture and Design Decisions

| ID    | Context | Decision | Reason | Impact |
| :--- | :--- | :--- | :--- | :--- |
| **D-001** | History & Analytics | Implemented as local SQLite without user auth. | Keeps the core prototype single-purpose, avoiding complex registration flows while providing dashboard-ready functionality as a documented enhancement. | Analytics API endpoints and history queries work locally but are not multi-tenant. |
| **D-002** | Language Scope | Python, Java, JavaScript | The prompt explicitly requires all three, expanding on the detailed report's suggestion of "one or two languages such as Python and Java". | Parsers and analyzers will be built for all three languages. |
| **D-003** | ErrorType Mapping | Strict 10-category enum (`Syntax`, `Runtime`, `Type`, `Logic`, `Name / Reference`, `Dependency`, `Configuration`, `Indentation`, `Import`, `Unknown / Requires Review`) | Reconciles the detailed report's general classification (syntax, semantic, runtime, logic, config) with the exact contract specified in the prompt. | Ensures deterministic mapping on the backend and predictable frontend rendering. |
| **D-004** | Code Execution vs Sandboxing | Strictly forbidden (static-only) | Security rules in prompt §11 strictly override report §6 (which lists execution as future scope). | Analyzers will rely exclusively on AST parsing (`tree-sitter`, `ast`) and regex rules without evaluating untrusted input. |

D-006: A-M4/A-M5 scope reduced under deadline constraint; Java/JS analyzers and recommendation diff-engine deferred to future work, documented here as an intentional decision, not a defect.
