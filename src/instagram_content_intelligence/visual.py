from __future__ import annotations

import base64
import html
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class ImageProvider(Protocol):
    def generate(self, prompt: str, output: Path, *, size: str, quality: str) -> Path: ...


class OpenAIImageProvider:
    """Optional first-party adapter; importing the core package does not require the SDK."""

    def __init__(self, model: str | None = None) -> None:
        # Model selection is configurable because image-model aliases and access evolve.
        self.model = model or os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2")

    def generate(self, prompt: str, output: Path, *, size: str = "1024x1536", quality: str = "high") -> Path:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("The optional 'visual' dependency group is required") from exc
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required for the OpenAI image adapter")
        result = OpenAI().images.generate(
            model=self.model,
            prompt=prompt,
            size=size,
            quality=quality,
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        image_bytes = base64.b64decode(result.data[0].b64_json, validate=True)
        if not image_bytes.startswith((b"\x89PNG\r\n\x1a\n", b"\xff\xd8\xff", b"RIFF")):
            raise ValueError("Image provider returned an unsupported or invalid binary format")
        output.write_bytes(image_bytes)
        return output


@dataclass(frozen=True)
class VisualSpec:
    width: int = 1080
    height: int = 1920
    safe_top: int = 250
    safe_bottom: int = 330
    safe_side: int = 90
    background: str = "#101114"
    foreground: str = "#ffffff"
    accent: str = "#f6c453"
    font_family: str = "Vazirmatn, sans-serif"


def render_rtl_html(
    headline: str,
    body: str,
    output: str | Path,
    spec: VisualSpec = VisualSpec(),
    background_image: str | Path | None = None,
    kicker: str | None = None,
) -> Path:
    """Create an exact-text RTL layout; Playwright can render it to PNG."""

    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    background_css = spec.background
    if background_image:
        uri = Path(background_image).resolve().as_uri()
        background_css = f"linear-gradient(#0007,#0009), url('{uri}') center/cover"
    document = f"""<!doctype html>
<html lang="fa" dir="rtl"><head><meta charset="utf-8">
<style>
@page {{ size: {spec.width}px {spec.height}px; margin: 0; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; width: {spec.width}px; height: {spec.height}px; overflow: hidden; }}
body {{ background: {background_css}; color: {spec.foreground}; font-family: {spec.font_family}; }}
.safe {{ position:absolute; top:{spec.safe_top}px; bottom:{spec.safe_bottom}px; right:{spec.safe_side}px; left:{spec.safe_side}px; display:flex; flex-direction:column; justify-content:center; gap:42px; }}
.kicker {{ color:{spec.accent}; font-size:42px; font-weight:700; }}
h1 {{ margin:0; font-size:92px; line-height:1.35; text-wrap:balance; overflow-wrap:anywhere; }}
p {{ margin:0; max-width:850px; font-size:48px; line-height:1.7; white-space:pre-wrap; overflow-wrap:anywhere; }}
.brand {{ position:absolute; right:{spec.safe_side}px; bottom:120px; font-size:28px; opacity:.75; }}
</style></head><body>
<main class="safe">
{f'<div class="kicker">{html.escape(kicker)}</div>' if kicker else ''}
<h1>{html.escape(headline)}</h1><p>{html.escape(body)}</p>
</main><div class="brand">Instagram Content Intelligence</div>
</body></html>"""
    target.write_text(document, encoding="utf-8")
    return target


def screenshot_html(source: str | Path, output: str | Path, spec: VisualSpec = VisualSpec()) -> Path:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright and its Chromium browser are required for PNG rendering") from exc
    source_path = Path(source).resolve()
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": spec.width, "height": spec.height}, device_scale_factor=1)
        page.goto(source_path.as_uri())
        page.screenshot(path=str(target), full_page=False)
        overflow = page.evaluate(
            """() => ({
              horizontal: document.documentElement.scrollWidth > document.documentElement.clientWidth,
              vertical: document.documentElement.scrollHeight > document.documentElement.clientHeight,
              safeOverflow: [...document.querySelectorAll('.safe *')].some(el => {
                const p=el.getBoundingClientRect(), s=document.querySelector('.safe').getBoundingClientRect();
                return p.left<s.left || p.right>s.right || p.top<s.top || p.bottom>s.bottom;
              })
            })"""
        )
        browser.close()
    if any(overflow.values()):
        target.unlink(missing_ok=True)
        raise ValueError(f"Visual QA failed: {overflow}")
    return target


def generate_story_visual(
    prompt: str,
    headline: str,
    body: str,
    output_dir: str | Path,
    provider: ImageProvider,
    spec: VisualSpec = VisualSpec(),
) -> dict[str, str]:
    folder = Path(output_dir)
    background = provider.generate(prompt, folder / "background.png", size="1024x1536", quality="high")
    html_path = render_rtl_html(headline, body, folder / "layout.html", spec, background)
    image_path = screenshot_html(html_path, folder / "story.png", spec)
    return {"background": str(background), "layout": str(html_path), "image": str(image_path)}
