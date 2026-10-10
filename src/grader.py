"""Grader: checks a model response against a task's ground truth.

The model is instructed to end every reply with a line:
    FINAL ANSWER: <value>
We grade ONLY that line, so explanation text can't accidentally match.
"""
import re

FINAL_RE = re.compile(r"FINAL ANSWER:\s*(.+)", re.IGNORECASE)
NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


def extract_final(response: str):
    """Return the text after the LAST 'FINAL ANSWER:' marker, or None."""
    matches = FINAL_RE.findall(response)
    return matches[-1].strip() if matches else None


def grade_numeric(final: str, task: dict) -> bool:
    """Correct if the first number is within tolerance_pct of the answer."""
    nums = NUMBER_RE.findall(final.replace(",", ""))
    if not nums:
        return False
    value = float(nums[0])
    truth = float(task["answer"])
    tolerance = abs(truth) * task.get("tolerance_pct", 2) / 100
    return abs(value - truth) <= tolerance


def grade_categorical(final: str, task: dict) -> bool:
    """Correct if an accepted term appears and no rejected term does.

    Word boundaries (\\b) stop 'no' matching inside 'not' or 'know'.
    Rejected terms are checked first, longest first, and removed, so
    'reverse causation' doesn't also count as 'causation'.
    """
    text = final.lower()
    for term in sorted(task.get("reject", []), key=len, reverse=True):
        pattern = r"\b" + re.escape(term.lower()) + r"\b"
        if re.search(pattern, text):
            return False
    return any(
        re.search(r"\b" + re.escape(t.lower()) + r"\b", text)
        for t in task.get("accept", [task["answer"]])
    )


def grade(response: str, task: dict) -> dict:
    """Grade one response. Returns a dict so results are easy to save."""
    final = extract_final(response)
    if final is None:
        return {"final": None, "correct": False, "parse_error": True}
    if task["answer_type"] == "numeric":
        ok = grade_numeric(final, task)
    else:
        ok = grade_categorical(final, task)
    return {"final": final, "correct": ok, "parse_error": False}
