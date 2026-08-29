from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterable


DEFAULT_SCORE_WEIGHTS = {
    "strategic_fit": 0.18,
    "audience_relevance": 0.18,
    "platform_fit": 0.10,
    "evidence_strength": 0.12,
    "novelty": 0.09,
    "trend_opportunity": 0.10,
    "historical_prior": 0.08,
    "feasibility": 0.07,
    "conversion_clarity": 0.08,
}


@dataclass(frozen=True)
class ContentCandidate:
    id: str
    title: str
    dimensions: dict[str, str]
    scores: dict[str, float]
    embedding: tuple[float, ...] = ()
    risk: float = 0.0
    saturation: float = 0.0
    required: bool = False


@dataclass(frozen=True)
class MatrixConfig:
    portfolio_size: int
    required_dimensions: tuple[str, ...] = (
        "audience",
        "job",
        "intent_stage",
        "pillar",
        "objective",
        "surface",
        "format",
        "angle",
        "evidence",
        "narrative",
        "cta",
        "lifecycle",
    )
    score_weights: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_SCORE_WEIGHTS))
    diversity_lambda: float = 0.72
    max_per_dimension_value: dict[str, int] = field(default_factory=dict)
    min_coverage: dict[str, int] = field(default_factory=dict)
    risk_penalty: float = 0.15
    saturation_penalty: float = 0.12


def _validate(candidate: ContentCandidate, config: MatrixConfig) -> None:
    missing = [name for name in config.required_dimensions if not candidate.dimensions.get(name)]
    if missing:
        raise ValueError(f"Candidate {candidate.id!r} misses dimensions: {', '.join(missing)}")


def _weighted_score(candidate: ContentCandidate, config: MatrixConfig) -> float:
    weights = {key: max(0.0, value) for key, value in config.score_weights.items()}
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("Matrix score weights must contain a positive value")
    positive = sum(
        (weights[key] / total) * max(0.0, min(1.0, candidate.scores.get(key, 0.0)))
        for key in weights
    )
    return max(
        0.0,
        min(
            1.0,
            positive
            - config.risk_penalty * max(0.0, min(1.0, candidate.risk))
            - config.saturation_penalty * max(0.0, min(1.0, candidate.saturation)),
        ),
    )


def _cosine(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    numerator = sum(a * b for a, b in zip(left, right))
    denominator = math.sqrt(sum(a * a for a in left)) * math.sqrt(sum(b * b for b in right))
    return numerator / denominator if denominator else 0.0


def _categorical_similarity(left: ContentCandidate, right: ContentCandidate) -> float:
    shared = set(left.dimensions) & set(right.dimensions)
    if not shared:
        return 0.0
    return sum(left.dimensions[key] == right.dimensions[key] for key in shared) / len(shared)


def _similarity(left: ContentCandidate, right: ContentCandidate) -> float:
    semantic = max(0.0, _cosine(left.embedding, right.embedding))
    categorical = _categorical_similarity(left, right)
    return 0.6 * semantic + 0.4 * categorical if left.embedding and right.embedding else categorical


def _over_cap(candidate: ContentCandidate, selected: list[ContentCandidate], config: MatrixConfig) -> bool:
    for dimension, cap in config.max_per_dimension_value.items():
        value = candidate.dimensions.get(dimension)
        count = sum(item.dimensions.get(dimension) == value for item in selected)
        if count >= cap:
            return True
    return False


def _coverage_bonus(candidate: ContentCandidate, selected: list[ContentCandidate], config: MatrixConfig) -> float:
    bonus = 0.0
    for dimension, target in config.min_coverage.items():
        current = {item.dimensions.get(dimension) for item in selected}
        value = candidate.dimensions.get(dimension)
        if len(current) < target and value not in current:
            bonus += 0.05
    return bonus


def select_portfolio(candidates: Iterable[ContentCandidate], config: MatrixConfig) -> dict:
    """Select a constrained, diverse portfolio instead of expanding a Cartesian grid."""

    pool = list(candidates)
    if config.portfolio_size < 1:
        raise ValueError("portfolio_size must be positive")
    for item in pool:
        _validate(item, config)

    selected: list[ContentCandidate] = []
    required = [item for item in pool if item.required]
    if len(required) > config.portfolio_size:
        raise ValueError("Required candidates exceed portfolio size")
    for item in required:
        if _over_cap(item, selected, config):
            raise ValueError(f"Required candidate {item.id!r} violates a cap")
        selected.append(item)

    remaining = [item for item in pool if item not in selected]
    audit: list[dict] = []
    while remaining and len(selected) < config.portfolio_size:
        ranked: list[tuple[float, ContentCandidate, float, float]] = []
        for item in remaining:
            if _over_cap(item, selected, config):
                continue
            relevance = _weighted_score(item, config)
            redundancy = max((_similarity(item, chosen) for chosen in selected), default=0.0)
            mmr = (
                config.diversity_lambda * relevance
                - (1 - config.diversity_lambda) * redundancy
                + _coverage_bonus(item, selected, config)
            )
            ranked.append((mmr, item, relevance, redundancy))
        if not ranked:
            break
        mmr, winner, relevance, redundancy = max(ranked, key=lambda row: (row[0], row[2], row[1].id))
        selected.append(winner)
        remaining.remove(winner)
        audit.append(
            {
                "id": winner.id,
                "mmr": round(mmr, 6),
                "relevance": round(relevance, 6),
                "redundancy": round(redundancy, 6),
            }
        )

    coverage = {
        dimension: sorted({item.dimensions.get(dimension, "") for item in selected})
        for dimension in config.required_dimensions
    }
    unmet = {
        dimension: target - len(coverage.get(dimension, []))
        for dimension, target in config.min_coverage.items()
        if len(coverage.get(dimension, [])) < target
    }
    return {
        "selected": [
            {
                "id": item.id,
                "title": item.title,
                "dimensions": item.dimensions,
                "base_score": round(_weighted_score(item, config), 6),
            }
            for item in selected
        ],
        "coverage": coverage,
        "unmet_coverage": unmet,
        "selection_audit": audit,
        "complete": len(selected) == config.portfolio_size and not unmet,
    }
