from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ProvenanceKind(str, Enum):
    META_API = "meta_api"
    INSTAGRAM_DASHBOARD = "instagram_dashboard"
    MANUAL_IMPORT = "manual_import"
    PUBLIC_SOURCE = "public_source"
    DERIVED = "derived"
    MODEL_INFERENCE = "model_inference"


@dataclass(frozen=True)
class Provenance:
    kind: ProvenanceKind
    source: str
    collected_at: str
    api_version: str | None = None
    scope: str | None = None
    estimated: bool = False
    in_development: bool = False
    notes: str | None = None

    @classmethod
    def now(cls, kind: ProvenanceKind, source: str, **kwargs: Any) -> "Provenance":
        return cls(
            kind=kind,
            source=source,
            collected_at=datetime.now(timezone.utc).isoformat(),
            **kwargs,
        )

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["kind"] = self.kind.value
        return data


@dataclass(frozen=True)
class MetricValue:
    name: str
    value: float | int | None
    provenance: Provenance
    numerator: str | None = None
    denominator: str | None = None
    unavailable_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["provenance"] = self.provenance.to_dict()
        return data

