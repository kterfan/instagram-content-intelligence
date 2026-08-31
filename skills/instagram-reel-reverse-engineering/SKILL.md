---
name: instagram-reel-reverse-engineering
description: Reverse engineer an owned, licensed, user-provided, or authorized reference Reel using measured transcript, timing, shots, OCR, audio, hook, payoff, and CTA structure. Use for Reel teardown, forensic analysis, viral-mechanism analysis, or adaptation without copying.
---

# Instagram Reel Reverse Engineering

Choose the lightest evidence route that fits the decision, separate observation from interpretation, and adapt mechanisms rather than protected expression.

## Runtime and execution modes

Resolve `PLUGIN_ROOT`: Claude Code provides `${CLAUDE_PLUGIN_ROOT}`; otherwise resolve the plugin root two directories above this `SKILL.md`. Use `python "${PLUGIN_ROOT}/scripts/ici.py"`; no package installation is required.

Select and disclose one mode:

- `cloud-video-native`: attach the authorized video and generated Prompt Pack. Prefer Gemini when native video understanding is available; ChatGPT is conditional on the active product surface and must disclose incomplete-video/audio risk.
- `cloud-evidence-pack`: use transcript, contact sheet/keyframes, metadata, and audio notes. This is the portable route for Claude unless its host supplies a documented video tool.
- `local-measured`: use ffprobe/FFmpeg, Whisper, PySceneDetect, and OCR for reproducible measurements.
- `hybrid-verified`: combine native cloud understanding with local verification of consequential timestamps, transcript, OCR, cuts, or audio. This is the highest-confidence route.

Cloud-native analysis is not degraded merely because local dependencies are absent. Conversely, confident model prose is not decoder-verified measurement.

## Intake and rights

Accept local media with an explicit permission basis: owned, licensed, user-provided, or public reference. Do not add a scraping/downloading shortcut. An optional acquisition adapter must document authorization, terms, and provenance.

## Cloud Prompt Pack

1. Prepare an account/task context using `${PLUGIN_ROOT}/examples/reel-cloud-context.json`; include Voice DNA, Matrix candidate, and Insights only when available.
2. Run `python "${PLUGIN_ROOT}/scripts/ici.py" reel prompt-pack --input <context.json> --provider gemini --output-dir <folder>`.
3. Attach the generated prompt and schema beside the authorized video or evidence pack in the selected model.
4. Save the returned JSON and run `python "${PLUGIN_ROOT}/scripts/ici.py" reel audit --input <response.json> --manifest <folder/reel-analysis-manifest.json>`.
5. Reject or re-run results with incomplete coverage, broken timestamps, ungrounded interpretation, missing alternatives, or undisclosed uncertainty.
6. When timestamped retention/skip data exists, run `reel align-retention`; describe aligned events as correlation, not causation.
7. To compare providers or multiple analyses, pass a JSON object with `reports` to `reel compare`.

## Optional local and hybrid verification

1. Run `doctor`, then create the local audit manifest.
2. When dependencies exist, run `reel pipeline`; its non-strict mode records unavailable stages and continues.
3. Verify only consequential or disputed moments when the cloud result is otherwise sufficient.
4. Run `reel hybrid-verify --input <cloud-response.json> --measured <measured_features.json>` to compare the first speech/overlay anchors; disclose all disagreements.
5. Never infer transcript, OCR, shot, or audio events for a local stage that did not run.

## Quality gate

- Transcript, shot, and OCR confidence or failure is visible.
- Every timestamp claim traces to measured data.
- Cloud reports declare provider, mode, inspected coverage, audio interpretation, limitations, and uncertainties.
- Observation IDs ground interpretations and reusable mechanisms; at least two alternative explanations accompany each interpretation.
- Performance claims use Insights data if available; content structure alone cannot prove causality.
- Adaptation returns close, moderate, and structurally different concepts plus a validation experiment.
