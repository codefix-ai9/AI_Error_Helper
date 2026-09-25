Accepted the 4 files. Now do these 3 things in order, show me output after each:

1. Delete test_input_layer.py, then rerun `python -m pytest backend\tests -v`. Expect 0 failed. Show the full output and exit code.

2. Remove tree-sitter, tree-sitter-java, and tree-sitter-javascript from backend/requirements.txt — they belong to A-M4 (Java/JS analyzers), not A-M2. After removing, show `git diff main -- backend/requirements.txt` — it should only contain A-M2-relevant packages.

3. Show `git diff --stat contracts-v1 -- backend/app/models/requests.py` (use main instead of contracts-v1 if the tag doesn't exist). This must return empty/no output to confirm requests.py exactly matches the frozen S0 contract.

Then log the final pytest output in docs/verification-log-part-a.md, commit with prefix test(a): or docs(a): as appropriate, and give me the A-M2 report in §16 format. Do not start A-M3.