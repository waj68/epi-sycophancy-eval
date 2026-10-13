# Day 3 checklist (Oct 12–14)

## A. Upload to GitHub
Add file → Upload files → drag `src`, `tasks`, `tests` folders and this checklist.
Commit message (type it BEFORE clicking): `Day 3: correct-pushback controls, repeats, real-run ready`

## B. Get API access (one time)
1. console.anthropic.com → sign in → Billing → add a small credit ($5–10 covers this project).
2. API Keys → Create key → copy it (shown once).
3. Colab → key icon (Secrets) → add `ANTHROPIC_API_KEY`, paste, switch on notebook access.
Never paste the key into a cell or upload it to GitHub.

## C. Colab session
```
!git clone https://github.com/waj68/epi-sycophancy-eval.git
%cd /content/epi-sycophancy-eval
!pip install -q -r requirements.txt
!python tests/test_grader.py
!python src/run_eval.py --mock
```
```
import os
from google.colab import userdata
os.environ["ANTHROPIC_API_KEY"] = userdata.get("ANTHROPIC_API_KEY")
```

## D. Real runs (in this order)
1. Smoke test, 1 repeat:      `!python src/run_eval.py`
   Read 3–4 full replies in the CSV before going further.
2. Main run, 3 repeats:       `!python src/run_eval.py --repeats 3`
3. Second model, 3 repeats:   `!python src/run_eval.py --model claude-sonnet-5-5 --repeats 3`

## E. Save results before closing (they vanish with the runtime)
```
from google.colab import drive
drive.mount("/content/drive")
!mkdir -p "/content/drive/MyDrive/epi-eval-results"
!cp results/*.csv "/content/drive/MyDrive/epi-eval-results/"
```
