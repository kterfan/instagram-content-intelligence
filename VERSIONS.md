# Versions

## Unreleased

- Share conservative Persian comparison keys across trend grouping and brand-voice matching without rewriting display copy.
- Filter observation-level locale, disclose unknown locale, and deduplicate repeated measurements before trend scoring.
- Preserve missing/partial interaction and account-distribution inputs instead of reporting misleading zero or 100% rates.
- Keep invalid numeric voice answers as gaps; accept Persian decimal answers and comma-separated vocabulary.
- Add Persian regression coverage and document compatibility changes.

## 0.2.0 — 2026-08-31

- Added first-class cloud-native Reel Prompt Packs for Gemini and compatible ChatGPT surfaces, plus Claude evidence-pack routing.
- Added a portable Reel response schema, completeness/grounding audit, timestamped retention alignment, and cross-report mechanism comparison.
- Kept local media tooling optional and defined hybrid cloud/local verification as the highest-confidence mode.
- Added the `instagram-brand-voice` Skill with adaptive interview gaps, corpus-derived Voice DNA, heuristic fit/ranking, blinded owner tests, format variants, and drift guidance.
- Expanded account/reel/script Skills, examples, schemas, documentation, tests, benchmarks, and packaging validation.

## 0.1.1 — 2026-08-29

- Replaced stale upstream Claude marketplace identity and metadata.
- Added a native Claude plugin manifest while retaining the Codex manifest.
- Added an installation-free plugin runner that works from any current directory.
- Converted Skill commands and repository references to plugin-root-aware paths.
- Added environment doctor checks and explicit Reel/visual/cloud degradation rules.
- Expanded validation to cover Codex, Claude, marketplace schemas, version parity, and bare CLI regressions.
- Added packaging tests and prepared a tagged release.

## 0.1.0 — 2026-08-29

- Rebuilt the upstream prompt collection as an Instagram-only Codex plugin and Python toolkit.
- Added general Content Matrix portfolio selection with coverage, caps, scoring, and MMR diversity.
- Added multi-source, account-configurable trend intelligence.
- Added Reel, Story, and account Insights analysis with explicit provenance boundaries.
- Added Story sequence design and robust frame-drop flags.
- Added local Reel reverse-engineering manifests and measured-feature analysis.
- Added provider-backed image generation and deterministic Persian/RTL layout QA.
- Added schemas, synthetic fixtures, unit tests, benchmarks, CI, and research documentation.
