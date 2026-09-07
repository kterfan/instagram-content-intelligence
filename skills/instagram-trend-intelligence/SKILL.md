---
name: instagram-trend-intelligence
description: Research and score Instagram-relevant trends for any account using configurable language, geography, category, risk, and source adapters. Use for trend research, emerging topics, trend validation, saturation analysis, or deciding whether an account should join a trend.
---

# Instagram Trend Intelligence

Trend research must be source-aware, reproducible, and usable across all account types.

## Runtime

Resolve `PLUGIN_ROOT`: Claude Code provides `${CLAUDE_PLUGIN_ROOT}`; otherwise resolve the plugin root two directories above this `SKILL.md`. Use `python "${PLUGIN_ROOT}/scripts/ici.py"` so the Python package does not need installation. Run `doctor` when uncertain. If local execution is unavailable, produce the dossier manually, mark score/confidence as model-estimated, and preserve source URLs and limitations.

## Non-negotiable rules

- Never equate a Google Trends 0-100 value with search volume.
- Never call a single viral post a trend.
- Never compare raw counts across heterogeneous sources.
- Never use a source merely because it exists; it must match the account's language, region, category, horizon, and risk profile.
- Retain query, collection time, URL, source limitations, and transformations.

## Workflow

For Persian audiences, read
[references/persian-trend-lifecycle.md](references/persian-trend-lifecycle.md).
Use its source-verification, account-fit and lifecycle gates before recommending
participation. Fresh news alone is not evidence of an Instagram trend. Expiration
is a conditional editorial hypothesis, not a guaranteed platform deadline.

1. Load the account profile and `${PLUGIN_ROOT}/config/source-registry.json`.
2. Build a query set from audience vocabulary, adjacent problems, category entities, cultural moments, competitors, and exclusions.
3. Select applicable sources. Core choices include authorized Instagram hashtag results, official Google Trends exports, curated RSS/Atom feeds, and manual observations. Enable scholarly or community adapters only when relevant and authorized.
4. Collect at least one historical comparison window. Mark missing baselines as insufficient evidence.
5. Convert each source to the normalized observation contract. For official CSV and snapshot helpers use `instagram_content_intelligence.adapters`.
6. Score velocity, acceleration, recency, source convergence, relevance, and evidence quality; penalize saturation and risk:

   `python "${PLUGIN_ROOT}/scripts/ici.py" trends <input.json> --output <ranked.json>`

7. Report score and confidence separately. A high score with low confidence is a test candidate, not a recommendation.
8. Translate accepted trends into original account-relevant angles; do not copy a creator's wording, edit, or identity.

## Output

For every candidate provide: topic, why-now evidence with dates and original URLs,
independent source count, confidence, audience relevance with a concrete account
use case, saturation, risk, lifecycle stage, recheck_at with timezone, expiration
conditions, publish/test/watch/skip decision, original angles and a validation
experiment. Missing freshness or account-fit evidence means watch/test, not a
confident recommendation. See `${PLUGIN_ROOT}/docs/trend-intelligence.md`.
