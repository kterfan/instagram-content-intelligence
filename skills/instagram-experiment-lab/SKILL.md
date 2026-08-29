---
name: instagram-experiment-lab
description: Design and evaluate reproducible Instagram content experiments and repository benchmarks. Use for A/B tests, Trial Reels, Story retention tests, hook comparisons, KPI definitions, benchmark runs, or quality validation.
---

# Instagram Experiment Lab

Turn recommendations into falsifiable, versioned tests.

## Workflow

1. Write one hypothesis, target population, unit, intervention, control, primary metric, counter-metrics, and stopping rule.
2. Choose a feasible design: randomized variant where available, Trial Reels, matched pairs, interrupted time series, or switchback. State validity threats.
3. Predeclare denominators and windows. Avoid changing objectives after seeing results.
4. Store input fixture, account/profile version, content version, publish context, metric provenance, and analysis code revision.
5. Run repository tests and benchmarks before claiming a workflow improvement:

   - `python -m unittest discover -s tests -v`
   - `python benchmarks/run_benchmarks.py`

6. Report uncertainty and practical effect, not only winner/loser language.

## Benchmark families

- Trend ranking invariance to raw source scale and sensitivity to convergence.
- Content Matrix coverage, cap compliance, and diversity.
- Insight denominator and scope correctness.
- Story anomaly detection on synthetic sequences.
- Persian/RTL layout overflow and visual goldens when browser dependencies exist.
- Reel feature extraction from annotated, redistributable fixtures.

