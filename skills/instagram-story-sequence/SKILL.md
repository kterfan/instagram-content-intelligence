---
name: instagram-story-sequence
description: Design measurable Instagram Story sequences and diagnose frame-level drop-off, exits, forwards, replies, and shares. Use for Persian Story sequences, Story retention, frame order, interaction placement, or Story funnel design.
---

# Instagram Story Sequence

Design a continuous promise-and-payoff sequence, then measure where the chain weakens.

## Runtime

Resolve `PLUGIN_ROOT`: Claude Code provides `${CLAUDE_PLUGIN_ROOT}`; otherwise resolve the plugin root two directories above this `SKILL.md`. Use `python "${PLUGIN_ROOT}/scripts/ici.py"`; no package installation is required. If execution is unavailable, build the frame table in-model and label anomaly detection as qualitative rather than deterministic.

## Design workflow

Read [references/scenario-to-production.md](references/scenario-to-production.md)
for new scenarios, critique and production handoff. Read
[references/sources-and-ranking.md](references/sources-and-ranking.md) when advice
depends on ranking, current platform features, metrics or an algorithm claim.
Do not browse just to decorate an already approved design with citations.

For new writing, choose the narrative structure from the actual audience job:
teaching needs an actionable demonstration, a personal narrative needs a concrete
event and change, comparison needs matched alternatives, and a sales sequence needs
a real offer and supported evidence. Compare openings internally and choose one
truthful promise. Each frame must add information or advance the narrative; remove
filler, repeated hooks and empty suspense. Do not force seven frames or a fixed
role order. Re-read the final copy to verify that the ending actually fulfills the
opening promise. These are editorial checks, not evidence of predicted performance.

When handing off to design, pass the same sequence-wide Persian font profile to
every frame. Variations in color, composition and genuine weight must never change
the font family or asset package. Preserve that lock across later revisions.

1. Declare one audience job and one sequence objective.
2. Write a truthful opening promise and the payoff that closes it.
3. Assign each frame a narrative role: interrupt, recognition, tension, value, proof, interaction, resolution, or CTA.
4. Ensure each frame either pays off the promise or creates a specific reason to continue.
5. Vary composition, scale, crop, motion, or information form without breaking brand continuity.
6. Place interaction stickers only when they advance the narrative or collect decision-useful evidence.
7. Create a skeleton with:

   `python "${PLUGIN_ROOT}/scripts/ici.py" story-plan --objective ... --audience-job ... --promise ... --frames 7`

## Measurement workflow

1. Collect Story insights before their availability window expires.
2. Run `python "${PLUGIN_ROOT}/scripts/ici.py" insights story <frames.json>`.
3. Inspect abnormal-drop flags, exit/forward/next-story/back rates, replies, shares, and the reach completion proxy.
4. Never treat a flagged frame as the proven cause. Test one change at a time across comparable sequences.

## Output

For visual art direction, read the adjacent
`${PLUGIN_ROOT}/skills/instagram-visual-generator/references/art-direction.md`.
Plan rhythm and continuity internally. Do not create a contact sheet or side-by-side
sequence preview. When the user supplies approved copy and asks only for design,
preserve that copy rather than running the writing workflow or adding a CTA.

For authored Persian frame exports, use the `workflow` commands and contract in
`${PLUGIN_ROOT}/docs/persian-workflow.md` and `${PLUGIN_ROOT}/schemas/production.schema.json`.
Choose surface `story`; declare a continuation for every non-final frame and finish
with `role=payoff`. The validator checks structure, so separately verify that the
final copy actually answers the opening promise. Carousel production uses the same
contract with `surface=carousel` and its own aspect ratio. Do not present the
English `story-plan` skeleton as finished Persian copy.

Return the frame table, continuation logic, interaction rationale, measurement fields, likely friction points, and A/B or switchback experiment.
