from __future__ import annotations

import math
import statistics
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Iterable


@dataclass(frozen=True)
class SourceDescriptor:
    id: str
    source_type: str
    evidence_quality: float
    languages: tuple[str, ...] = ("*",)
    regions: tuple[str, ...] = ("*",)
    categories: tuple[str, ...] = ("*",)
    latency_hours: float = 0.0
    auth_mode: str = "none"
    terms_url: str | None = None
    enabled: bool = True

    def supports(self, language: str, region: str, categories: set[str]) -> bool:
        language_ok = "*" in self.languages or language in self.languages
        region_ok = "*" in self.regions or region in self.regions
        category_ok = "*" in self.categories or bool(categories.intersection(self.categories))
        return self.enabled and language_ok and region_ok and category_ok


@dataclass(frozen=True)
class TrendObservation:
    topic: str
    source_id: str
    observed_at: str
    value: float
    baseline: float
    acceleration: float = 0.0
    saturation: float = 0.0
    risk: float = 0.0
    language: str = "*"
    region: str = "*"
    categories: tuple[str, ...] = ()
    evidence_url: str | None = None


DEFAULT_WEIGHTS = {
    "velocity": 0.22,
    "acceleration": 0.14,
    "recency": 0.14,
    "convergence": 0.16,
    "relevance": 0.18,
    "evidence": 0.16,
}


@dataclass(frozen=True)
class TrendProfile:
    language: str
    region: str
    categories: tuple[str, ...]
    horizon_hours: float = 168.0
    min_sources: int = 2
    risk_tolerance: float = 0.5
    saturation_penalty: float = 0.18
    risk_penalty: float = 0.22
    weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_WEIGHTS))


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _robust_scale(values: list[float]) -> list[float]:
    if not values:
        return []
    median = statistics.median(values)
    deviations = [abs(v - median) for v in values]
    mad = statistics.median(deviations)
    if mad == 0:
        spread = max(max(values) - min(values), 1.0)
        return [_clamp(0.5 + (v - median) / (2 * spread)) for v in values]
    return [_clamp(0.5 + 0.15 * ((v - median) / mad)) for v in values]


def _weight_map(profile: TrendProfile) -> dict[str, float]:
    weights = {key: max(0.0, float(value)) for key, value in profile.weights.items()}
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("Trend weights must contain at least one positive value")
    return {key: value / total for key, value in weights.items()}


def score_trends(
    observations: Iterable[TrendObservation],
    sources: Iterable[SourceDescriptor],
    profile: TrendProfile,
    now: datetime | None = None,
) -> list[dict]:
    """Score topics across heterogeneous sources without assuming a universal niche.

    Raw values are never compared across sources. Each observation is first expressed
    as a relative change from its own baseline, then robustly scaled within the batch.
    """

    current = now or datetime.now(timezone.utc)
    source_map = {source.id: source for source in sources}
    categories = set(profile.categories)
    usable: list[TrendObservation] = []
    for observation in observations:
        source = source_map.get(observation.source_id)
        if not source:
            continue
        if not source.supports(profile.language, profile.region, categories):
            continue
        age = (current - _parse_time(observation.observed_at)).total_seconds() / 3600
        if age <= profile.horizon_hours and age >= 0:
            usable.append(observation)

    velocities = [
        (item.value - item.baseline) / max(abs(item.baseline), 1e-9) for item in usable
    ]
    scaled_velocity = _robust_scale(velocities)
    scaled_acceleration = _robust_scale([item.acceleration for item in usable])

    grouped: dict[str, list[tuple[TrendObservation, float, float]]] = {}
    for item, velocity, acceleration in zip(usable, scaled_velocity, scaled_acceleration):
        grouped.setdefault(item.topic.strip().casefold(), []).append((item, velocity, acceleration))

    weights = _weight_map(profile)
    total_enabled_sources = max(1, len({item.source_id for item in usable}))
    results: list[dict] = []
    for topic_key, rows in grouped.items():
        distinct_sources = {row[0].source_id for row in rows}
        mean_velocity = statistics.fmean(row[1] for row in rows)
        mean_acceleration = statistics.fmean(row[2] for row in rows)
        recencies = []
        evidence_values = []
        relevance_values = []
        saturation_values = []
        risk_values = []
        for item, _, _ in rows:
            age = (current - _parse_time(item.observed_at)).total_seconds() / 3600
            recencies.append(math.exp(-math.log(2) * age / max(profile.horizon_hours / 3, 1)))
            evidence_values.append(_clamp(source_map[item.source_id].evidence_quality))
            item_categories = set(item.categories)
            relevance_values.append(
                1.0 if not categories else len(categories & item_categories) / max(1, len(categories))
            )
            saturation_values.append(_clamp(item.saturation))
            risk_values.append(_clamp(item.risk))

        convergence = _clamp(len(distinct_sources) / max(profile.min_sources, 1))
        components = {
            "velocity": mean_velocity,
            "acceleration": mean_acceleration,
            "recency": statistics.fmean(recencies),
            "convergence": convergence,
            "relevance": statistics.fmean(relevance_values),
            "evidence": statistics.fmean(evidence_values),
        }
        positive = sum(weights.get(name, 0.0) * value for name, value in components.items())
        saturation = statistics.fmean(saturation_values)
        risk = statistics.fmean(risk_values)
        risk_over_tolerance = max(0.0, risk - profile.risk_tolerance)
        score = _clamp(
            positive
            - profile.saturation_penalty * saturation
            - profile.risk_penalty * risk_over_tolerance
        )
        confidence = _clamp(
            0.45 * convergence
            + 0.35 * components["evidence"]
            + 0.20 * min(1.0, len(rows) / 3)
        )
        results.append(
            {
                "topic": rows[0][0].topic,
                "score": round(score, 6),
                "confidence": round(confidence, 6),
                "source_count": len(distinct_sources),
                "observation_count": len(rows),
                "components": {key: round(value, 6) for key, value in components.items()},
                "penalties": {
                    "saturation": round(saturation, 6),
                    "risk_over_tolerance": round(risk_over_tolerance, 6),
                },
                "evidence_urls": sorted({row[0].evidence_url for row in rows if row[0].evidence_url}),
                "profile": asdict(profile),
            }
        )
    return sorted(results, key=lambda item: (-item["score"], -item["confidence"], item["topic"]))

