"""Installation-free entry point for Claude, Codex, Cowork, and local checkouts."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from instagram_content_intelligence.cli import main


if __name__ == "__main__":
    main()

