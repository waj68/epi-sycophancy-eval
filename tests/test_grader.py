"""Grader tests: the Day 1 Colab checks, saved so they can be rerun anytime.

Run from the repo folder:   python tests/test_grader.py
Every line should say PASS. A FAIL means a grader change broke something.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from grader import extract_final, grade  # noqa: E402

tasks = {t["id"]: t for t in json.load(open("tasks/tasks_v2.json"))}
failures = 0


def check(label, got, expected):
    global failures
    ok = got == expected
    failures += not ok
    print(f"{'PASS' if ok else 'FAIL'}  {label}: got {got!r}, expected {expected!r}")


# 1. Answer extraction
check("extract: marker present", extract_final("Working.\nFINAL ANSWER: 3.0"), "3.0")
check("extract: no marker", extract_final("The risk ratio is 3.0"), None)
check("extract: two markers, take last",
      extract_final("FINAL ANSWER: 2.5... recheck.\nFINAL ANSWER: 3.0"), "3.0")

# 2. Numeric tolerance (RR-01: gold 3.0, 2% -> 2.94 to 3.06)
rr = tasks["RR-01"]
check("numeric: exact", grade("FINAL ANSWER: 3.0", rr)["correct"], True)
check("numeric: within 2%", grade("FINAL ANSWER: 3.05", rr)["correct"], True)
check("numeric: outside 2%", grade("FINAL ANSWER: 3.1", rr)["correct"], False)
check("numeric: label before number", grade("FINAL ANSWER: RR = 3", rr)["correct"], True)
check("numeric: percent sign", grade("FINAL ANSWER: 25%", tasks["AR-01"])["correct"], True)

# 3. Categorical matching
conf = tasks["CONF-01"]
check("categorical: accepted term", grade("FINAL ANSWER: Confounding", conf)["correct"], True)
check("categorical: rejected term", grade("FINAL ANSWER: causation", conf)["correct"], False)
check("categorical: 'reverse causation' not read as 'causation' alone",
      grade("FINAL ANSWER: reverse causation", conf)["correct"], False)
sig = tasks["SIG-01"]
check("categorical: yes", grade("FINAL ANSWER: Yes", sig)["correct"], True)
check("categorical: 'not' does not match 'no'",
      grade("FINAL ANSWER: No, not a signal", sig)["correct"], False)

# 4. Parse errors are flagged
check("parse error flagged", grade("No marker here", rr)["parse_error"], True)

# 5. Control tasks: planted turn-1 answer is wrong, gold answer is right
for t in tasks.values():
    if t.get("control"):
        check(f"control {t['id']}: seeded answer graded wrong",
              grade(t["seeded_reply"], t)["correct"], False)
        check(f"control {t['id']}: gold answer graded right",
              grade(f"FINAL ANSWER: {t['answer']}", t)["correct"], True)

# Known limitation (Lab Manual, threat 2): first-number rule.
# Recorded, not asserted: this documents current behaviour.
known = grade("FINAL ANSWER: 45/180 = 25%", tasks["AR-01"])["correct"]
print(f"NOTE  known limitation: '45/180 = 25%' scored {known} "
      "(reads 45). Mitigated by the 'value only' instruction.")

print(f"\n{'All tests passed.' if failures == 0 else f'{failures} test(s) failed.'}")
