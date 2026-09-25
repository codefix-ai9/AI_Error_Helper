Fast-mode sanity check before A-M4:
1. Confirm the AI handoff calls NullAIEngine.explain(ctx: AIRequestContext) — not any other method name — and that AnalysisResult still returns a valid result when NullAIEngine returns status="disabled".
2. Confirm no A-M3 code touched models/, core/, application/ports.py, or data/contract_fixtures/ — run `git diff --stat contracts-v1..HEAD -- backend/app/models backend/app/core backend/app/application/ports.py data/contract_fixtures` (or main if tag missing). Should be empty.

Then commit everything with prefix feat(a): implement A-M3 python analyzer + orchestrator (S1 milestone). Move to A-M4: Java/JS analyzers — skip per our fast-mode plan, just register Python-only in the registry with a documented graceful-degrade note for Java/JS. Then A-M5 minimal (static-only fallback, no diff/verification yet). Then A-M6 (5 sample cases). Then minimal docs. Report back with one final full pytest run at the end of ALL of it.
