---
name: instagram-content-matrix
description: Design a configurable, evidence-aware Instagram Content Matrix and select a strategically balanced portfolio. Use for content pillars, formats, campaign calendars, idea portfolios, coverage gaps, or general account strategy across any niche.
---

# Instagram Content Matrix

Build a multidimensional decision system, not a decorative two-axis grid and not a Cartesian explosion.

## Runtime

Resolve `PLUGIN_ROOT`: Claude Code provides `${CLAUDE_PLUGIN_ROOT}`; otherwise resolve the plugin root two directories above this `SKILL.md`. The installation-free command is `python "${PLUGIN_ROOT}/scripts/ici.py"`. Run `doctor` first when execution capability is uncertain. If Python execution is unavailable, apply the documented scoring and constraints in-model, label the result `degraded-model-analysis`, and do not claim that deterministic selection ran.

## Required dimensions

Start with audience, job/pain/gain, intent stage, pillar, objective, Instagram surface, format, angle, evidence type, narrative mechanism, CTA, lifecycle, effort, and risk. Add or remove dimensions only with an account-specific reason.

## Workflow

1. Read the account profile. If absent, run the account-foundation workflow.
2. Audit current content and known performance with provenance.
3. Generate candidates that each declare all required dimensions.
4. Score strategic fit, audience relevance, platform fit, evidence strength, novelty, trend opportunity, historical prior, feasibility, and conversion clarity. Treat initial weights as a declared design choice.
5. Add portfolio constraints: maximum concentration and minimum coverage by objective, intent stage, pillar, surface, or format.
6. Run the deterministic selector:

   `python "${PLUGIN_ROOT}/scripts/ici.py" matrix <input.json> --output <portfolio.json>`

7. Review `unmet_coverage` and `selection_audit`. Do not hide an infeasible portfolio.
8. Calibrate weights from account experiments; never claim one universal matrix is optimal for all niches.

## Output

Return the selected portfolio, rejected near-misses, coverage audit, score definitions, assumptions, and a measurement plan. Use `${PLUGIN_ROOT}/docs/content-matrix.md` for the evidence/design boundary.
