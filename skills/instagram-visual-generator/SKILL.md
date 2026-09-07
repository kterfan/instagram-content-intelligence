---
name: instagram-visual-generator
description: Art-direct Persian Instagram Stories with account-specific typography, semantic composition, photography and restrained accents. Deliver production prompts or rendered assets, preserving exact copy and reviewing sequence consistency internally without a contact sheet.
---

# Instagram Visual Generator

Use image models for art direction and deterministic rendering for exact text.

## Story art direction

For Story design, read [references/art-direction.md](references/art-direction.md)
before choosing composition. This is the primary design workflow. Interpret the
whole sequence internally; do not create or show a side-by-side preview, contact
sheet or candidate gallery. Deliver only the selected individual final prompts or
slides in the user's requested mode. A prompt-only request must not invoke image
tools or require a rendering dependency check.

Use [references/design-contract.md](references/design-contract.md) when compiling
or validating a model-authored plan. The helper checks exact copy and geometric
constraints; it does not choose the design or claim a visual test passed.
Keep brand profiles and licensed font assets private and portable across accounts.
Never downgrade a requested exact font to the bundled renderer's font silently.

## Runtime and graceful degradation

Resolve `PLUGIN_ROOT`: Claude Code provides `${CLAUDE_PLUGIN_ROOT}`; otherwise resolve the plugin root two directories above this `SKILL.md`. Use `python "${PLUGIN_ROOT}/scripts/ici.py"`; no package installation is required. For rendering, run `doctor` first. If an image provider is unavailable, return a production prompt or an explicitly limited HTML layout when it satisfies the requested font. If Playwright/Chromium is unavailable, return HTML instead of PNG and report the missing rendering capability. Never claim an image or PNG was generated when its stage did not run.

## Workflow

1. Load account visual tokens, surface, dimensions, safe zones, and accessibility constraints.
2. Create a visual prompt that excludes text unless text is intentionally part of the scene.
3. Generate the base visual with a configured provider. The built-in OpenAI adapter reads `OPENAI_API_KEY` and optional `OPENAI_IMAGE_MODEL`; never store keys in the repository.
4. Render Persian/RTL headline, body, CTA, or poll placeholders in HTML using the deterministic renderer.
5. Run Playwright screenshot QA. Reject horizontal, vertical, or safe-area overflow.
6. Inspect contrast, text hierarchy, crop safety, spelling, logo/identity risks, and consistency across a sequence.

## Commands

Create and optionally rasterize exact-text layouts with:

`python "${PLUGIN_ROOT}/scripts/ici.py" visual --headline ... --body ... --html frame.html --png frame.png`

For full provider generation, call `generate_story_visual` from `instagram_content_intelligence.visual`.

## Output

The renderer bundles licensed Vazirmatn and embeds it locally. Use `--surface carousel`
or `--surface cover` for the 1080×1350 preset, and `story`/`reel` for 1080×1920.
Presets and safe areas are design defaults, not permanent Instagram UI guarantees.
For all frames of a versioned project use `workflow export --project <folder>
--output-dir <folder> --png` via the same runner; see `${PLUGIN_ROOT}/docs/persian-workflow.md`.
Inspect the produced images after automated font/overflow checks. Do not silently
truncate dense text or treat HTML-only success as PNG success.

Return the generation prompt, provider/model/version, seed if supported, background asset, exact copy, layout file, final PNG, and QA report.
