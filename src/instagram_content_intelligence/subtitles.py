"""Exact-copy SRT/VTT exports with deterministic timing and reading-load QA."""
from __future__ import annotations

import textwrap

from .contracts import number, text_field


def subtitle_pack(cues: list[dict], *, max_chars=32, max_lines=2, max_cps=20.0) -> dict:
    if max_chars < 1 or max_lines < 1:
        raise ValueError("Subtitle line limits must be positive")
    number(max_cps, "max_cps", minimum=0.1)
    prepared, warnings, previous_end = [], [], 0
    for index, cue in enumerate(cues, 1):
        start = round(number(cue.get("start"), "start") * 1000)
        end = round(number(cue.get("end"), "end") * 1000)
        text = text_field(cue, "text")
        if end <= start or start < previous_end:
            raise ValueError(f"cue {index}: زمان نامعتبر یا همپوشانی")
        if "-->" in text or any(ord(c) < 32 and c not in "\n\t" for c in text):
            raise ValueError("متن زیرنویس دارای نشانه کنترلی نامعتبر است")
        lines = []
        for paragraph in text.splitlines():
            lines.extend(textwrap.wrap(paragraph, width=max_chars, break_long_words=False, break_on_hyphens=False))
        cps = len(text.replace("\n", "")) / ((end - start) / 1000)
        if len(lines) > max_lines or any(len(line) > max_chars for line in lines) or cps > max_cps:
            warnings.append({"cue": index, "type": "reading_load", "lines": len(lines), "characters_per_second": round(cps, 2)})
        prepared.append((start, end, "\n".join(lines)))
        previous_end = end

    def stamp(ms, sep):
        seconds, milli = divmod(ms, 1000)
        minutes, second = divmod(seconds, 60)
        hours, minute = divmod(minutes, 60)
        return f"{hours:02}:{minute:02}:{second:02}{sep}{milli:03}"

    srt, vtt = [], ["WEBVTT\n"]
    for index, (start, end, text) in enumerate(prepared, 1):
        srt.append(f"{index}\n{stamp(start, ',')} --> {stamp(end, ',')}\n{text}\n")
        # VTT parses markup; escape copy rather than allowing embedded tags.
        escaped = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        vtt.append(f"{index}\n{stamp(start, '.')} --> {stamp(end, '.')}\n{escaped}\n")
    return {"srt": "\n".join(srt), "vtt": "\n".join(vtt), "warnings": warnings,
            "timing_provenance": "user_or_model_supplied_not_forced_alignment",
            "thresholds": {"max_chars": max_chars, "max_lines": max_lines, "max_cps": max_cps}}
