---
name: instagram-reel-script
description: Write an original, measurable Instagram Reel script from account context, Content Matrix cell, trend evidence, or reverse-engineering findings. Use for hooks, scripts, shot lists, retention beats, or Reel production briefs.
---

# Instagram Reel Script

Create an original script tied to a specific audience job and measurement objective.

## Workflow

1. Load account context and select one Matrix candidate.
2. Load the current Voice DNA when available. If it is missing or draft, preserve explicit gaps rather than inventing brand mannerisms.
3. If using a trend, cite the trend dossier and confidence. If using a reference Reel, use only grounded abstract mechanisms from its audited reverse-engineering report.
4. Define promise, proof, payoff, CTA, target duration, and one primary metric.
5. Write a timecoded script with spoken line, on-screen text, visual action, shot change, sound event, and purpose for each beat.
6. Audit the first three seconds for immediate comprehension without false urgency.
7. Audit information density, pauses, shot rhythm, accessibility, subtitle readability, and Voice DNA fit.
8. Provide two hook variants and one structurally different control for testing.

## Output

For machine-exportable production, resolve `PLUGIN_ROOT` two directories above this
file (or use `${CLAUDE_PLUGIN_ROOT}`) and read `${PLUGIN_ROOT}/schemas/production.schema.json`.
Write the original script in that contract with `authoring_provenance=model_draft`.
Use `python "${PLUGIN_ROOT}/scripts/ici.py" workflow import --project <folder> --input <script.json>`
then `workflow export --project <folder> --output-dir <output>` through the same runner.
Read `${PLUGIN_ROOT}/docs/persian-workflow.md` for SRT/VTT, cover and shot-list exports.
Resolve reading-load warnings before describing subtitles as ready. Timing remains
estimated until checked against the actual recording; imported scripts require
editorial review even when structural validation passes.

Return production-ready timecodes, assets, capture notes, edit notes, text-safe zones, caption, cover concept, hypothesis, counter-metric, and experiment ID.
