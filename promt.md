Confirm and fix for real this time:
1. git ls-files -s AI_Error_Helper (read-only — should show mode 160000)
2. git rm --cached AI_Error_Helper (exact command, no -r, no -f)
3. Check .gitignore already has "AI_Error_Helper/" — if not, add it under "# --- Part A ---"
4. git add .gitignore
5. git commit -m "chore(a): fully untrack nested AI_Error_Helper gitlink"
6. git push origin feat/part-a-analysis
7. git status — confirm AI_Error_Helper no longer appears at all.