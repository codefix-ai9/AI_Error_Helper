A-M1 status = "Pending Part B approval" (not Complete). Before I tag:
1. List the exact files for ai/engine.py::build_ai_engine and history/repository.py::build_history_repository (stub bodies), and main.py if created. Show each file's path.
2. Add a negative architecture test: run the scanner on synthetic source (analysis importing ai; ai importing analysis; anything importing api; application importing ai other than the two factories in container.py) and assert violations are reported. Rerun tests and log the output.
3. Show practice_exercise/quiz_question in result_hybrid_ok.json and result_static_only.json (null), and note in docs/data-model.md that they are additive vs master §5.3.
4. Fix the log: Python is 3.14.6 (final), not alpha. List KNOWN LIMITATIONS honestly (mark unverified items NOT VERIFIED).
5. Commit on branch feat/part-a-analysis (show `git branch --show-current` first). No push to main.