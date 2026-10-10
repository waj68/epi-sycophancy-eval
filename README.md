# Do LLMs Hold Correct Epidemiological Answers Under Social Pressure?

*A small evaluation of sycophancy in public health reasoning.*

## Question
When a language model gives a correct epidemiological answer and a user pushes back with a wrong claim ("my supervisor says it's 2.5"), how often does the model abandon the correct answer?

## Why it matters
Public health decisions (outbreak declarations, vaccine effectiveness, risk communication) depend on correct quantitative reasoning. A model that yields to confident but wrong pushback is unsafe in exactly the settings where users are most likely to push back. This is a domain-specific test of sycophancy, a known AI safety concern.

## Method
- **Tasks:** epidemiology problems with verifiable answers (attack rates, risk and odds ratios, incidence rates, predictive values, vaccine effectiveness, NNT, surveillance signal detection, study-design reasoning).
- **Protocol:** two turns per task: (1) neutral question; (2) pushback asserting a plausible wrong answer.
- **Grading:** automated; numeric answers within a tolerance, categorical answers by term matching on a required `FINAL ANSWER:` line.
- **Primary outcome:** flip rate = proportion of initially correct answers that become incorrect after pushback.

## Results
_To be added._

## Limitations
_To be added._

## Toward an RL environment
The grader functions as a reward signal: reward = correct in turn 2, conditional on the pushback. This task set could be extended into an environment that rewards models for holding correct answers under pressure while still updating when the pushback is actually right.

## Next steps
_To be added._

## Run it
```bash
pip install -r requirements.txt
python src/run_eval.py --mock     # pipeline test, no API key
export ANTHROPIC_API_KEY=...      # then a real run
python src/run_eval.py
```
