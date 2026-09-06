---
name: instagram-account-foundation
description: Build or update a reusable Instagram account profile covering audience, jobs, positioning, voice, evidence rules, brand tokens, constraints, and measurement. Use before strategy work when account context is missing or stale.
---

# Instagram Account Foundation

Create a portable account profile; never embed one creator's niche into shared logic.

## Runtime and paths

Resolve `PLUGIN_ROOT` before opening templates: in Claude Code use `${CLAUDE_PLUGIN_ROOT}`; in other hosts resolve the plugin root two directories above this `SKILL.md`. Reference `${PLUGIN_ROOT}/config/profile.example.json`. If plugin files are unavailable in a cloud session, create the same fields in the current workspace and state that the template could not be loaded.

## Workflow

1. Inspect existing account material before asking for information already available.
2. Record language, region, audience segments, jobs/pains/gains, promise, differentiators, proof, prohibited claims, risk tolerance, content capabilities, brand tokens, conversion paths, and the path to a versioned Voice DNA.
3. Separate confirmed facts, owner preferences, observed performance, and hypotheses.
4. Define primary and counter-metrics for each business objective.
5. Save the result using `${PLUGIN_ROOT}/config/profile.example.json` as a structural reference. Do not put secrets or access tokens in the profile.
6. When voice is missing, generic, disputed, or stale, use `instagram-brand-voice`; Account Foundation must not invent a validated voice from a few adjectives.

## Quality gate

For a local Persian production project, use `workflow init --project <private-folder>`
through the resolved runner. Ask language, audience region and timezone separately;
never infer Iran from Persian. Reuse current answers with `--input` when known.
Read `${PLUGIN_ROOT}/docs/persian-workflow.md` for project persistence and the
Jalali calendar command. Load sourced occasions only when relevant to this account.

- The profile must work without mentioning a specific public figure, industry, or account.
- Every factual or performance claim has provenance.
- Missing facts remain explicit gaps.
- A later skill can select sources and matrix dimensions solely from this profile.
- The profile links to Voice DNA status and gaps without duplicating its evidence corpus.
