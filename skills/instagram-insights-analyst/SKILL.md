---
name: instagram-insights-analyst
description: Analyze Instagram account, Reel, post, and Story Insights with explicit API/dashboard/manual provenance. Use for retention, reach, share/reach, save/reach, profile conversion, follower distribution, or performance diagnosis.
---

# Instagram Insights Analyst

Analyze what the supplied data supports; do not invent missing Instagram metrics.

## Runtime

Resolve `PLUGIN_ROOT`: Claude Code provides `${CLAUDE_PLUGIN_ROOT}`; otherwise resolve the plugin root two directories above this `SKILL.md`. Use the installation-free runner `python "${PLUGIN_ROOT}/scripts/ici.py"`. If Python cannot run, calculate only transparent ratios, show each numerator/denominator, and label the output `degraded-model-analysis`.

## Provenance boundary

Label every field as Meta API, Instagram Dashboard, manual import, derived, or model inference. Preserve API version, collection time, scope, estimated status, and availability errors.

Current platform caveats are documented in `${PLUGIN_ROOT}/docs/metrics-catalog.md`. In particular, account-level follower/non-follower breakdown is not automatically a per-Reel breakdown, and current media API documentation does not list Reel-level profile activity or follows even though some Dashboard surfaces expose additional metrics.

## Workflow

1. Validate scope, date range, media type, collection delay, and missing-value semantics.
2. Run:

   - `python "${PLUGIN_ROOT}/scripts/ici.py" insights reel <metrics.json> --duration <seconds>`
   - `python "${PLUGIN_ROOT}/scripts/ici.py" insights story <frames.json>`
   - `python "${PLUGIN_ROOT}/scripts/ici.py" insights account <metrics.json>`

3. Compare like with like: same surface, duration band, objective, audience state, and publish window where possible.
4. Use robust account baselines, not generic industry numbers, unless a benchmark has transparent sampling.
5. Distinguish observation, diagnosis, and experiment. Correlation does not prove why a Reel or frame lost viewers.

## Output

To retain results by content revision, read `${PLUGIN_ROOT}/docs/persian-workflow.md`
and `${PLUGIN_ROOT}/schemas/publication-result.schema.json`. Use `results record`
or `results import-csv` with a private SQLite path via the resolved runner. Bind a
project revision explicitly when an older version was published. Transcribed
screenshots need field review; unresolved OCR values must not be marked reviewed.
Use `results compare` only within its matching strata; retain insufficient-data
status and inspect audience/timing changes that the recorded strata cannot capture.

Return metric definitions, provenance gaps, ratios with denominators, cohort/baseline choice, anomalies, competing explanations, and the smallest discriminating experiment.
