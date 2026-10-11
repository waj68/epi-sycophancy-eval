# Day 2 checklist (Oct 12–13)

## A. Upload the changes to GitHub
1. Repo page → Add file → Upload files.
2. Drag in: `src/run_eval.py` (replaces old), `tasks/tasks_v1.json` (new), `tests/test_grader.py` (new), `DAY2_CHECKLIST.md`.
   Drag the `src`, `tasks`, `tests` FOLDERS so files land in the right place.
3. Commit message: `Day 2: 30 tasks, parse-error handling, value-only answers, grader tests`

## B. Run in Colab (new session: clone first)
- `!python tests/test_grader.py`  → every line PASS
- `!python src/run_eval.py --mock` → 30 tasks, new summary with parse errors

## C. Review the 30 tasks as an epidemiologist (most important)
For each task check: question unambiguous? gold answer right? pushback a realistic, common error?
Note any change by task ID and send it.
