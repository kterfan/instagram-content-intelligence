from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_NAME = "instagram-content-intelligence"
CLAUDE_PLUGIN_KEYS = {"name", "description", "version", "author", "homepage", "license"}
MARKETPLACE_ROOT_KEYS = {"name", "owner", "plugins"}
MARKETPLACE_ENTRY_KEYS = {
    "name", "displayName", "source", "description", "version", "author",
    "repository", "license", "category", "keywords", "tags",
}


def _json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid or missing JSON: {path}: {exc}") from exc


def main() -> None:
    errors: list[str] = []
    try:
        codex = _json(ROOT / ".codex-plugin" / "plugin.json")
        claude = _json(ROOT / ".claude-plugin" / "plugin.json")
        marketplace = _json(ROOT / ".claude-plugin" / "marketplace.json")
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    project_section = re.search(r"(?ms)^\[project\]\s*(.*?)(?=^\[|\Z)", pyproject_text)
    python_version_match = re.search(
        r'^version\s*=\s*"([^"]+)"',
        project_section.group(1) if project_section else "",
        re.MULTILINE,
    )

    entries = marketplace.get("plugins", [])
    marketplace_version = entries[0].get("version") if entries else None
    package_init = (ROOT / "src" / "instagram_content_intelligence" / "__init__.py").read_text(encoding="utf-8")
    package_match = re.search(r'^__version__\s*=\s*"([^"]+)"', package_init, re.MULTILINE)
    versions = {
        "codex": codex.get("version"),
        "claude": claude.get("version"),
        "marketplace": marketplace_version,
        "python": python_version_match.group(1) if python_version_match else None,
        "package": package_match.group(1) if package_match else None,
    }
    if len(set(versions.values())) != 1 or None in versions.values():
        errors.append(f"Version mismatch: {versions}")

    if codex.get("name") != PROJECT_NAME:
        errors.append("Codex plugin name mismatch")
    if claude.get("name") != PROJECT_NAME:
        errors.append("Claude plugin name mismatch")
    unknown_claude = set(claude) - CLAUDE_PLUGIN_KEYS
    if unknown_claude:
        errors.append(f"Unsupported Claude plugin keys: {sorted(unknown_claude)}")
    unknown_root = set(marketplace) - MARKETPLACE_ROOT_KEYS
    if unknown_root:
        errors.append(f"Unsupported marketplace root keys: {sorted(unknown_root)}")
    if marketplace.get("name") != PROJECT_NAME:
        errors.append("Marketplace name mismatch")
    owner = marketplace.get("owner", {})
    if owner.get("name") != "Erfan (kterfan)" or owner.get("url") != "https://github.com/kterfan":
        errors.append("Marketplace owner mismatch")
    if len(entries) != 1:
        errors.append("Marketplace must contain exactly one plugin entry")
    else:
        entry = entries[0]
        unknown_entry = set(entry) - MARKETPLACE_ENTRY_KEYS
        if unknown_entry:
            errors.append(f"Unsupported marketplace entry keys: {sorted(unknown_entry)}")
        if entry.get("name") != PROJECT_NAME or entry.get("source") != ".":
            errors.append("Marketplace plugin identity/source mismatch")
        if entry.get("category") != "productivity" or not entry.get("keywords"):
            errors.append("Marketplace category/keywords missing")
        if "metadata" in entry or "categories" in entry:
            errors.append("Marketplace category metadata is in the wrong location")

    skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if len(skill_files) != 10:
        errors.append(f"Expected exactly ten Instagram skills, found {len(skill_files)}")
    for path in skill_files:
        content = path.read_text(encoding="utf-8")
        match = re.search(r"^name:\s*([^\s]+)\s*$", content, re.MULTILINE)
        if not match or match.group(1) != path.parent.name:
            errors.append(f"Skill name mismatch: {path}")
        if not content.startswith("---\n") or "\ndescription:" not in content.split("---", 2)[1]:
            errors.append(f"Invalid skill frontmatter: {path}")
        if re.search(r"(?<![/\w])ici\s+(trends|matrix|insights|story-plan|reel|visual)", content):
            errors.append(f"Skill uses installation-dependent bare ici command: {path}")
        if "scripts/ici.py" in content and "PLUGIN_ROOT" not in content:
            errors.append(f"Skill runner lacks plugin-root resolution: {path}")
    if any(path.name in {"youtube-thumbnail", "linkedin"} for path in (ROOT / "skills").iterdir()):
        errors.append("Out-of-scope platform skill found")
    if not (ROOT / "scripts" / "ici.py").is_file():
        errors.append("Installation-free plugin runner is missing")
    for required_schema in (
        "reel-cloud-context.schema.json",
        "reel-analysis-response.schema.json",
        "brand-voice-dna.schema.json",
    ):
        try:
            _json(ROOT / "schemas" / required_schema)
        except ValueError as exc:
            errors.append(str(exc))
    for required_module in ("cloud_reel.py", "brand_voice.py"):
        if not (ROOT / "src" / "instagram_content_intelligence" / required_module).is_file():
            errors.append(f"Missing implementation module: {required_module}")

    registry = _json(ROOT / "config" / "source-registry.json")
    for source in registry["sources"]:
        for required in ("id", "source_type", "evidence_quality", "languages", "regions", "categories", "auth_mode", "limitations"):
            if required not in source:
                errors.append(f"Source {source.get('id')} misses {required}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(
        f"Validated Codex + Claude packaging, version {versions['python']}, "
        f"{len(skill_files)} skills, installation-free runner, and {len(registry['sources'])} trend sources."
    )


if __name__ == "__main__":
    main()
