---
name: instagram-visual-generator
description: Art-direct Persian Instagram Stories with account-specific typography, semantic composition, photography and restrained accents. Deliver production prompts or rendered assets, preserving exact copy and reviewing sequence consistency internally without a contact sheet.
---

# Instagram Visual Generator

Use image models for art direction and deterministic rendering for exact text.

## Story art direction

**Sequence-wide Persian font lock:** resolve one family and exact asset/package
from the user's profile before designing the first slide. Carry that same lock to
every slide, heading, support line, emphasis, supplied CTA and revision. Never
reselect a family for mood, composition, text fit or reference appearance. Genuine
weights within the locked package may vary. Missing weights/assets require a
disclosed constraint, never silent substitution. Only an explicit user request
can replace the lock; then update and recheck the whole sequence consistently.
When a sequence continues across turns, retain its profile rather than choosing
again. Include the full family/source lock in every independent production prompt.
The user's explicitly named font always wins over a stored profile or bundled
default, regardless of family. If no font has been named or previously approved,
ask one concise font question before final typography; continue independent scene
planning meanwhile. Never assume Yekan Bakh, Peyda or Vazirmatn is compulsory.

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

## Layout-first execution contract

Read [references/layout-quality.md](references/layout-quality.md) for every Story
image-production request. Plan the image around the approved text before generating
artwork. Compare plausible layouts internally, then choose one. When tools support
it, measure actual shaped text with the requested font and inspect the resulting
image; mental judgment alone is not measured validation. Separate technical checks
from artistic judgment. Repair the failing region or layer while preserving approved
copy, identity and unaffected artwork. Never claim universal approval or perfection.
Do not expose internal candidates or produce a side-by-side sequence preview.

## Workflow

1. Load account visual tokens, surface, dimensions, safe zones, and accessibility constraints.
2. Resolve text bounds, hierarchy, subject placement and reserved areas first; use these constraints in the artwork prompt. Exclude generated lettering unless explicitly part of the requested scene.
3. Generate the base visual with a configured provider. The built-in OpenAI adapter reads `OPENAI_API_KEY` and optional `OPENAI_IMAGE_MODEL`; never store keys in the repository. Check that the generated scene actually preserves the planned text space.
4. Use a compatible compositor and the actual requested font asset to shape approved copy. Measure line fit and preserve Persian joining. The bundled generic renderer is suitable only when its font and layout meet the request; do not silently substitute it for a custom design.
5. Run available font/bounds checks, then inspect the actual individual image at phone display size for readability and artistic hierarchy. A structural plan check does not prove rendered quality.
6. Correct specific failures locally and recheck affected properties. Deliver the chosen final result with material unresolved limitations; no candidate gallery or sequence preview.

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
