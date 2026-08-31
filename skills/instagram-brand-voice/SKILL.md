---
name: instagram-brand-voice
description: Discover, model, test, and maintain an Instagram brand voice through adaptive questions, approved and rejected samples, Voice DNA, blind tests, format variants, and drift checks. Use when a creator or account needs a distinctive voice rather than generic tone adjectives.
---

# Instagram Brand Voice

Build a testable voice model from owner intent and observed language. Do not declare a voice validated merely because a style guide sounds plausible.

## Runtime and paths

Resolve `PLUGIN_ROOT`: Claude Code provides `${CLAUDE_PLUGIN_ROOT}`; otherwise resolve the plugin root two directories above this `SKILL.md`. Use `python "${PLUGIN_ROOT}/scripts/ici.py"`; no package installation is required. The reusable input example is `${PLUGIN_ROOT}/examples/brand-voice-interview.json`, and the output contract is `${PLUGIN_ROOT}/schemas/brand-voice-dna.schema.json`.

## Workflow

1. Inspect existing captions, Reel transcripts, Story copy, comments, replies, brand documents, and prior account profile before asking duplicated questions.
2. Save confirmed owner answers and representative positive/negative samples in a private working file; never commit private account text to the public repository.
3. Run `python "${PLUGIN_ROOT}/scripts/ici.py" voice interview --input <interview.json>` and ask only the returned gaps. Forced-choice examples are preferred when an adjective is ambiguous.
4. Run `python "${PLUGIN_ROOT}/scripts/ici.py" voice dna --input <interview.json> --output <voice-dna.json>`.
5. Treat the DNA as a versioned hypothesis. Keep owner intent, observed corpus traits, performance observations, and unresolved gaps separate.
6. Generate at least one authentic-style candidate, one plausible generic candidate, and one contrast candidate. Build a blinded pack with `voice blind-test`; do not show the answer key during owner selection.
7. Use `voice score` or `voice rank` only as heuristic screening. Owner blind identification and concrete feedback are the acceptance gate.
8. Maintain separate variants for Reel, Story, Caption, and Comment when evidence supports a difference. After adding approved samples, build a new DNA and run `voice drift` with a payload containing `previous` and `current`; owner review decides whether to accept a new version.

Read [references/interview-and-validation.md](references/interview-and-validation.md) when designing interview rounds, blind tests, or acceptance criteria.

## Quality gate

- Voice DNA contains provenance, positive and negative evidence, format variants, forbidden language, and explicit gaps.
- Generic marketing clichés cannot pass merely by matching tone adjectives.
- Performance is not attributed to wording without an experiment.
- Reel adaptation follows Voice DNA but never overwrites measured facts from the reference Reel.
