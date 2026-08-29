from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    errors = []
    manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
    if manifest.get("name") != "instagram-content-intelligence":
        errors.append("Plugin name mismatch")
    skill_files = sorted((ROOT / "skills").glob("*/SKILL.md"))
    if len(skill_files) < 9:
        errors.append("Expected at least nine Instagram skills")
    for path in skill_files:
        content = path.read_text(encoding="utf-8")
        match = re.search(r"^name:\s*([^\s]+)\s*$", content, re.MULTILINE)
        if not match or match.group(1) != path.parent.name:
            errors.append(f"Skill name mismatch: {path}")
        if not content.startswith("---\n") or "\ndescription:" not in content.split("---", 2)[1]:
            errors.append(f"Invalid skill frontmatter: {path}")
    if any(path.name in {"youtube-thumbnail", "linkedin"} for path in (ROOT / "skills").iterdir()):
        errors.append("Out-of-scope platform skill found")
    registry = json.loads((ROOT / "config" / "source-registry.json").read_text(encoding="utf-8"))
    for source in registry["sources"]:
        for required in ("id", "source_type", "evidence_quality", "languages", "regions", "categories", "auth_mode", "limitations"):
            if required not in source:
                errors.append(f"Source {source.get('id')} misses {required}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Validated {len(skill_files)} skills, plugin manifest, and {len(registry['sources'])} trend sources.")


if __name__ == "__main__":
    main()

