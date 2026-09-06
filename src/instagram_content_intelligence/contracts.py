"""Shared validation and durable local JSON writes for production workflows."""
from __future__ import annotations

import json
import math
import os
import tempfile
from pathlib import Path

from .persian import comparison_key


def text_field(data: dict, name: str) -> str:
    value = data.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name}: متن غیرخالی لازم است")
    return value.strip()


def number(value, name: str, *, minimum=0.0, maximum=None) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name}: عدد معتبر لازم است")
    try:
        result = float(comparison_key(str(value)).replace("٫", ".").replace("٬", ""))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name}: عدد معتبر لازم است") from exc
    if not math.isfinite(result) or result < minimum or (maximum is not None and result > maximum):
        raise ValueError(f"{name}: مقدار خارج از محدوده است")
    return result


def read_json(path: str | Path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path: str | Path, payload, *, overwrite: bool = True) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if not overwrite:
        with target.open("x", encoding="utf-8") as handle:
            handle.write(serialized)
        return target
    fd, temporary = tempfile.mkstemp(dir=target.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return target
