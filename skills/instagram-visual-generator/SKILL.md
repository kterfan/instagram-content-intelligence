---
name: instagram-visual-generator
description: Generate Instagram visual assets internally through a provider adapter, then render exact Persian/RTL copy deterministically and run layout QA. Use for Story frames, covers, carousel panels, visual concepts, or image generation.
---

# Instagram Visual Generator

Use image models for art direction and deterministic rendering for exact text.

## Workflow

1. Load account visual tokens, surface, dimensions, safe zones, and accessibility constraints.
2. Create a visual prompt that excludes text unless text is intentionally part of the scene.
3. Generate the base visual with a configured provider. The built-in OpenAI adapter reads `OPENAI_API_KEY` and optional `OPENAI_IMAGE_MODEL`; never store keys in the repository.
4. Render Persian/RTL headline, body, CTA, or poll placeholders in HTML using the deterministic renderer.
5. Run Playwright screenshot QA. Reject horizontal, vertical, or safe-area overflow.
6. Inspect contrast, text hierarchy, crop safety, spelling, logo/identity risks, and consistency across a sequence.

## Commands

Create and optionally rasterize exact-text layouts with:

`ici visual --headline ... --body ... --html frame.html --png frame.png`

For full provider generation, call `generate_story_visual` from `instagram_content_intelligence.visual`.

## Output

Return the generation prompt, provider/model/version, seed if supported, background asset, exact copy, layout file, final PNG, and QA report.

