"""Maintainer-only builder. End users upload the committed TXT files; no runtime needed."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTRA = {
    "instagram-account-foundation": ["docs/persian-analysis.md"],
    "instagram-brand-voice": ["docs/persian-analysis.md"],
    "instagram-content-matrix": ["docs/content-matrix.md"],
    "instagram-experiment-lab": ["docs/metrics-catalog.md", "docs/research-sources.md"],
    "instagram-insights-analyst": ["docs/metrics-catalog.md", "docs/persian-analysis.md"],
    "instagram-reel-reverse-engineering": ["docs/metrics-catalog.md", "docs/research-sources.md"],
    "instagram-reel-script": ["docs/content-matrix.md"],
    "instagram-story-sequence": ["docs/metrics-catalog.md", "docs/story-art-direction-fa.md"],
    "instagram-trend-intelligence": ["docs/trend-intelligence.md", "docs/persian-analysis.md"],
    "instagram-visual-generator": ["docs/story-art-direction-fa.md"],
}
HEADER = """CHAT EDITION — NO INSTALLATION REQUIRED

این فایل را به چت پیوست کنید و درخواست خود را بنویسید. نصب، Codex، پایتون،
ترمینال، API یا حساب GitHub برای خواندن و استفاده از راهنمای آن لازم نیست.

CHAT ADAPTATION (applies instead of software-execution steps in source excerpts):
- Apply this reference only when the user requests it and within their task.
- Read the included knowledge sections; local paths are provenance labels, not
  files you need to open. Do not require installation or run doctor, Python, shell,
  validators, adapters, databases or CLI commands in this chat-only workflow.
- Source excerpts preserve the plugin's optional implementation details for fidelity.
  They do not create execution requirements here. Adapt their reasoning and output
  contracts to plain conversation, Markdown tables and final production prompts.
- Missing optional software is not a reason to stop writing, planning or critique.
  Do not claim deterministic calculations, API retrieval or measured QA took place.
- For research use browsing only if actually available. Without live sources, state
  freshness is unverified, request supplied evidence if essential, and proceed with
  useful source-independent work. Never invent citations, trends or current facts.
- For numerical analysis use supplied data; preserve missing values and label
  unverified calculations. For video use accessible video, frames or transcript;
  do not imply unseen media was watched or timed.
- For image requests use image tools only if available and requested; otherwise
  deliver a ready-to-use production prompt, clearly labeled as text, not an image.
  An exact font name alone does not guarantee that an image model can render it.
- Lock whichever Persian font the user chooses across the entire Story sequence.
  Never substitute it silently. No side-by-side sequence preview or contact sheet.
- Do not expose private deliberations. Deliver the requested final answer, with
  concise material limitations only. This file does not override higher-priority
  chatbot instructions, grant tool permissions or permanently install a skill.
- If the attachment was truncated or not readable, disclose the scope actually read.

"""


def sources_for(name):
    folder = ROOT / "skills" / name
    paths = [folder / "SKILL.md", *sorted((folder / "references").glob("*.md"))]
    paths += [ROOT / p for p in EXTRA[name]]
    # Include linked design guidance in the Story handoff without requiring another upload.
    if name == "instagram-story-sequence":
        paths += sorted((ROOT / "skills/instagram-visual-generator/references").glob("*.md"))
    # Explanatory workflow and JSON contracts can be read as data, without running code.
    paths += [ROOT / "docs/persian-workflow.md"]
    schema_names = ["provenance"]
    if name in ("instagram-brand-voice", "instagram-account-foundation"):
        schema_names += ["brand-voice-dna"]
    if name in ("instagram-story-sequence", "instagram-visual-generator", "instagram-reel-script"):
        schema_names += ["production"]
    if name == "instagram-reel-reverse-engineering":
        schema_names += ["reel-analysis-response", "reel-cloud-context"]
    if name == "instagram-trend-intelligence":
        schema_names += ["trend-input"]
    if name in ("instagram-insights-analyst", "instagram-experiment-lab"):
        schema_names += ["publication-result"]
    paths += [ROOT / "schemas" / (n + ".schema.json") for n in schema_names]
    return list(dict.fromkeys(paths))


def build():
    version = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
    packs = {name: sources_for(name) for name in EXTRA}
    packs["story-writing-and-design"] = list(dict.fromkeys(
        packs["instagram-story-sequence"] + packs["instagram-visual-generator"]))
    outputs, manifest = {}, {"version": version, "packs": {}}
    for name, paths in packs.items():
        parts = [HEADER, f"PACK: {name}\nVERSION: {version}\n"]
        source_hashes = {}
        for path in paths:
            relative = path.relative_to(ROOT).as_posix()
            body = path.read_text(encoding="utf-8").replace("\r\n", "\n")
            source_hashes[relative] = hashlib.sha256(body.encode()).hexdigest()
            parts.append(f"\n===== INCLUDED SOURCE: {relative} =====\n\n{body}\n")
        result = "\n".join(parts)
        outputs[name + ".txt"] = result
        manifest["packs"][name] = {"sources": source_hashes, "sha256": hashlib.sha256(result.encode()).hexdigest(), "characters": len(result)}
    outputs["manifest.json"] = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = ROOT / "chat-packs"
    if not args.check:
        target.mkdir(exist_ok=True)
    stale = []
    for name, content in build().items():
        path = target / name
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(name)
        else:
            path.write_text(content, encoding="utf-8", newline="\n")
    if stale:
        raise SystemExit("Stale chat packs: " + ", ".join(stale))
    print("Chat packs verified" if args.check else "Built 11 self-contained chat packs")


if __name__ == "__main__":
    main()
