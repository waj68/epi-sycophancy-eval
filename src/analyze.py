"""Summarize result CSVs: rates with 95% confidence intervals, escalation by
round, breakdowns, a hand-check sample, and a plot.

Usage (in Colab, after mounting Drive):
    python src/analyze.py <csv> <csv> ...
Example:
    python src/analyze.py "/content/drive/MyDrive/epi-eval-results/claude-haiku-5-5_20261014_1851.csv" ...

Outputs (in results/analysis/):
    summary.md          tables ready to paste into the README
    handcheck.csv       20 random replies to grade by hand (grader validation)
    caving_by_round.png cumulative caving by escalation round
"""
import math
import os
import sys

import pandas as pd

OUT = "results/analysis"


def wilson(k, n, z=1.96):
    """95% Wilson interval for k events in n trials (good for small n)."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    return (max(0, c - h), min(1, c + h))


def rate(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {k / n:.0%} (95% CI {lo:.0%}–{hi:.0%})" if n else "n/a"


def load(paths):
    frames = []
    for p in paths:
        d = pd.read_csv(p)
        d["source_file"] = os.path.basename(p)
        if "flip_round" not in d:          # files made before escalation existed
            d["flip_round"] = d["flipped"].astype(int)   # a flip there = round 1
        esc = "rounds_run" in d and d.loc[~d["control"], "rounds_run"].max() > 1
        d["condition"] = "escalation (3 rounds)" if esc else "single round"
        frames.append(d)
    return pd.concat(frames, ignore_index=True)


def main(paths):
    os.makedirs(OUT, exist_ok=True)
    df = load(paths)
    lines = ["# Results summary", ""]

    # 1. Main table: one row per model x condition
    lines += ["## Main results", "",
              "| Model | Condition | Runs | Turn-1 accuracy | Flip rate (wrong pushback) | Update rate (correct pushback) | Parse errors |",
              "|---|---|---|---|---|---|---|"]
    for (model, cond), g in df.groupby(["model", "condition"]):
        main_ = g[~g["control"]]
        ctl = g[g["control"]]
        at_risk = main_[main_["correct_turn1"] & ~main_["parse_error_turn2"]]
        flips = int((at_risk["flip_round"] > 0).sum())
        ctl_ok = ctl[~ctl["parse_error_turn2"]]
        parse = int((g["parse_error_turn1"] | g["parse_error_turn2"]).sum())
        lines.append(
            f"| {model} | {cond} | {len(g)} | {main_['correct_turn1'].mean():.0%} | "
            f"{rate(flips, len(at_risk))} | {rate(int(ctl_ok['updated'].sum()), len(ctl_ok))} | {parse} |")
    lines += ["", "Confidence intervals are Wilson 95% intervals treating runs as "
              "independent; repeats of the same task are correlated, so true "
              "uncertainty is somewhat wider.", ""]

    # 2. Escalation: cumulative caving by round
    esc = df[(df["condition"].str.startswith("escalation")) & ~df["control"]]
    if len(esc):
        lines += ["## Escalation: cumulative share caved by round", "",
                  "| Model | Round 1 | Round 2 | Round 3 |", "|---|---|---|---|"]
        curves = {}
        for model, g in esc.groupby("model"):
            at_risk = g[g["correct_turn1"] & ~g["parse_error_turn2"]]
            n = len(at_risk)
            cum = [int(((at_risk["flip_round"] > 0) & (at_risk["flip_round"] <= k)).sum())
                   for k in (1, 2, 3)]
            curves[model] = [c / n for c in cum]
            lines.append(f"| {model} | " + " | ".join(f"{c}/{n}" for c in cum) + " |")
        lines.append("")
        try:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(6, 4))
            for model, ys in curves.items():
                ax.step([0, 1, 2, 3], [0] + ys, where="post", label=model)
            ax.set_xlabel("Pushback round")
            ax.set_ylabel("Cumulative share caved")
            ax.set_xticks([1, 2, 3])
            ax.set_ylim(0, max(0.1, max(max(v) for v in curves.values()) * 1.2))
            ax.set_title("Caving under escalating pressure")
            ax.legend()
            fig.tight_layout()
            fig.savefig(f"{OUT}/caving_by_round.png", dpi=150)
        except ImportError:
            pass

    # 3. Breakdown by pushback type (main tasks, all conditions)
    main_all = df[~df["control"]]
    if "pushback_type" in main_all:
        lines += ["## Flips by pushback type (main tasks, all runs)", "",
                  "| Model | Pushback type | Flips |", "|---|---|---|"]
        for (model, pt), g in main_all.groupby(["model", "pushback_type"]):
            at_risk = g[g["correct_turn1"] & ~g["parse_error_turn2"]]
            k = int((at_risk["flip_round"] > 0).sum())
            lines.append(f"| {model} | {pt} | {rate(k, len(at_risk))} |")
        lines.append("")

    # 4. Hand-check sample for grader validation
    sample = df.sample(n=min(20, len(df)), random_state=1)
    cols = ["source_file", "model", "id", "control", "answer",
            "final_turn2", "correct_turn2", "reply_turn2"]
    hc = sample[cols].copy()
    hc["my_verdict_correct"] = ""   # fill in by hand: TRUE / FALSE
    hc.to_csv(f"{OUT}/handcheck.csv", index=False)

    with open(f"{OUT}/summary.md", "w") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))
    print(f"\nSaved: {OUT}/summary.md, {OUT}/handcheck.csv"
          + (f", {OUT}/caving_by_round.png" if len(esc) else ""))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Give one or more result CSV paths.")
    main(sys.argv[1:])
