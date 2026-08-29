from __future__ import annotations

import csv
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .trends import TrendObservation


def google_trends_csv(
    path: str | Path,
    topic: str,
    source_id: str = "google_trends_export",
    language: str = "*",
    region: str = "*",
    categories: tuple[str, ...] = (),
) -> TrendObservation:
    """Read an official Google Trends CSV export without treating 0-100 as volume."""

    rows: list[tuple[str, float]] = []
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        for row in reader:
            if len(row) < 2:
                continue
            try:
                rows.append((row[0], float(row[1].replace("<1", "0.5"))))
            except ValueError:
                continue
    if len(rows) < 2:
        raise ValueError("Google Trends export needs at least two numeric observations")
    historical = [value for _, value in rows[:-1]]
    baseline = statistics.median(historical)
    previous = rows[-2][1]
    current = rows[-1][1]
    observed_at = _coerce_period(rows[-1][0])
    return TrendObservation(
        topic=topic,
        source_id=source_id,
        observed_at=observed_at,
        value=current,
        baseline=baseline,
        acceleration=(current - previous) - (previous - historical[-2] if len(historical) > 1 else 0),
        language=language,
        region=region,
        categories=categories,
        evidence_url="https://trends.google.com/trends/",
    )


def event_count_observation(
    topic: str,
    source_id: str,
    observed_at: str,
    current_count: int,
    baseline_counts: Iterable[int],
    *,
    categories: tuple[str, ...] = (),
    language: str = "*",
    region: str = "*",
    evidence_url: str | None = None,
) -> TrendObservation:
    """Normalize RSS, scholarly, news, community, or API event counts to one contract."""

    history = [max(0, int(value)) for value in baseline_counts]
    if not history:
        raise ValueError("At least one historical comparison window is required")
    baseline = statistics.median(history)
    previous = history[-1]
    prior = history[-2] if len(history) > 1 else previous
    return TrendObservation(
        topic=topic,
        source_id=source_id,
        observed_at=observed_at,
        value=max(0, current_count),
        baseline=baseline,
        acceleration=(current_count - previous) - (previous - prior),
        categories=categories,
        language=language,
        region=region,
        evidence_url=evidence_url,
    )


def meta_hashtag_snapshot(path: str | Path, topic: str, observed_at: str) -> TrendObservation:
    """Convert stored, authorized IG Hashtag recent/top media responses into an event count."""

    payload: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
    current = len(payload.get("current", {}).get("data", []))
    history = [len(item.get("data", [])) for item in payload.get("history", [])]
    return event_count_observation(
        topic,
        "instagram_hashtag_api",
        observed_at,
        current,
        history,
        evidence_url="https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-hashtag/",
    )


def _coerce_period(value: str) -> str:
    cleaned = value.strip()
    for format_string in ("%Y-%m-%d", "%Y-%m", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            parsed = datetime.strptime(cleaned, format_string)
            return parsed.replace(tzinfo=parsed.tzinfo or timezone.utc).isoformat()
        except ValueError:
            pass
    raise ValueError(f"Unsupported period in Google Trends export: {value!r}")

