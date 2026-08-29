---
name: instagram-story-sequence
description: Design measurable Instagram Story sequences and diagnose frame-level drop-off, exits, forwards, replies, and shares. Use for Persian Story sequences, Story retention, frame order, interaction placement, or Story funnel design.
---

# Instagram Story Sequence

Design a continuous promise-and-payoff sequence, then measure where the chain weakens.

## Runtime

Resolve `PLUGIN_ROOT`: Claude Code provides `${CLAUDE_PLUGIN_ROOT}`; otherwise resolve the plugin root two directories above this `SKILL.md`. Use `python "${PLUGIN_ROOT}/scripts/ici.py"`; no package installation is required. If execution is unavailable, build the frame table in-model and label anomaly detection as qualitative rather than deterministic.

## Design workflow

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

Return the frame table, continuation logic, interaction rationale, measurement fields, likely friction points, and A/B or switchback experiment.
