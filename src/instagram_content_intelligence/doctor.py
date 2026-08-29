from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from typing import Any


def _module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _executable(name: str) -> dict[str, Any]:
    path = shutil.which(name)
    return {"available": bool(path), "path": path}


def _tesseract_languages() -> list[str]:
    if not shutil.which("tesseract"):
        return []
    try:
        result = subprocess.run(
            ["tesseract", "--list-langs"],
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (subprocess.SubprocessError, OSError):
        return []
    return [line.strip() for line in result.stdout.splitlines()[1:] if line.strip()]


def environment_report() -> dict[str, Any]:
    executables = {name: _executable(name) for name in ("ffmpeg", "ffprobe", "tesseract")}
    modules = {
        name: _module(import_name)
        for name, import_name in {
            "whisper": "whisper",
            "scenedetect": "scenedetect",
            "pytesseract": "pytesseract",
            "pillow": "PIL",
            "playwright": "playwright",
            "openai": "openai",
        }.items()
    }
    languages = _tesseract_languages()
    core_ready = sys.version_info >= (3, 10)
    reels_ready = all(executables[name]["available"] for name in ("ffmpeg", "ffprobe", "tesseract")) and all(
        modules[name] for name in ("whisper", "scenedetect", "pytesseract", "pillow")
    )
    return {
        "python": {"version": sys.version.split()[0], "core_ready": core_ready},
        "executables": executables,
        "modules": modules,
        "tesseract_languages": languages,
        "capabilities": {
            "core_analytics": core_ready,
            "reel_full_pipeline": reels_ready,
            "reel_partial_pipeline": executables["ffprobe"]["available"],
            "persian_ocr": "fas" in languages,
            "rtl_html_layout": core_ready,
            "png_rendering": modules["playwright"],
            "openai_image_generation": modules["openai"] and bool(os.getenv("OPENAI_API_KEY")),
        },
        "degrade": {
            "reel": "Use local metadata/features that are available and report every skipped stage; never fabricate transcript, OCR, or shots.",
            "visual": "Render exact RTL HTML without a generated background or PNG when provider/Playwright is unavailable.",
            "cloud": "Use the skill's evidence and planning workflow without local CLI execution; label outputs as model analysis.",
        },
    }

