from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


PROVIDERS: dict[str, dict[str, Any]] = {
    "gemini": {
        "native_video": True,
        "recommended_mode": "cloud-video-native",
        "limitations": [
            "Default video sampling may miss sub-second cuts or overlays.",
            "Model timestamps and OCR are probabilistic, not decoder-verified measurements.",
        ],
    },
    "chatgpt": {
        "native_video": "account_and_surface_dependent",
        "recommended_mode": "cloud-video-native",
        "limitations": [
            "Video attachment availability varies by account, platform, and upload method.",
            "The product may not inspect the whole video or interpret all audio accurately.",
        ],
    },
    "claude": {
        "native_video": False,
        "recommended_mode": "cloud-evidence-pack",
        "limitations": [
            "Use a transcript, contact sheet/keyframes, metadata, and audio notes unless the host supplies a video tool.",
        ],
    },
    "other": {
        "native_video": "unknown",
        "recommended_mode": "cloud-evidence-pack",
        "limitations": ["Verify the selected product surface and model capabilities before upload."],
    },
}

MODES = {"cloud-video-native", "cloud-evidence-pack", "local-measured", "hybrid-verified"}
PERMISSION_BASES = {"owned", "licensed", "user_provided", "public_reference"}


def reel_analysis_schema() -> dict[str, Any]:
    """Return the portable response contract used by cloud and hybrid analysis."""
    confidence = {"type": "number", "minimum": 0, "maximum": 1}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://github.com/kterfan/instagram-content-intelligence/schemas/reel-analysis-response.schema.json",
        "title": "Instagram Reel Analysis Response",
        "type": "object",
        "required": ["schema_version", "metadata", "observations", "interpretations", "mechanisms", "adaptations", "uncertainties"],
        "properties": {
            "schema_version": {"const": "1.0"},
            "metadata": {
                "type": "object",
                "required": ["provider", "mode", "video_duration_seconds", "audio_interpreted", "coverage"],
                "properties": {
                    "provider": {"type": "string"},
                    "model_or_surface": {"type": ["string", "null"]},
                    "mode": {"enum": sorted(MODES)},
                    "video_duration_seconds": {"type": "number", "exclusiveMinimum": 0},
                    "audio_interpreted": {"type": "boolean"},
                    "coverage": {
                        "type": "object",
                        "required": ["start_seconds", "end_seconds"],
                        "properties": {
                            "start_seconds": {"type": "number", "minimum": 0},
                            "end_seconds": {"type": "number", "minimum": 0},
                        },
                    },
                    "limitations": {"type": "array", "items": {"type": "string"}},
                },
            },
            "observations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["id", "start_seconds", "end_seconds", "kind", "evidence", "confidence"],
                    "properties": {
                        "id": {"type": "string"},
                        "start_seconds": {"type": "number", "minimum": 0},
                        "end_seconds": {"type": "number", "minimum": 0},
                        "kind": {"enum": ["speech", "overlay", "visual", "edit", "audio", "performance", "other"]},
                        "evidence": {"type": "string"},
                        "confidence": confidence,
                    },
                },
            },
            "interpretations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["claim", "evidence_ids", "confidence", "alternative_explanations"],
                    "properties": {
                        "claim": {"type": "string"},
                        "evidence_ids": {"type": "array", "items": {"type": "string"}},
                        "confidence": confidence,
                        "alternative_explanations": {"type": "array", "minItems": 2, "items": {"type": "string"}},
                        "requires_insights": {"type": "boolean"},
                    },
                },
            },
            "mechanisms": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "evidence_ids", "reusable_principle", "must_change"],
                    "properties": {
                        "name": {"type": "string"},
                        "evidence_ids": {"type": "array", "items": {"type": "string"}},
                        "reusable_principle": {"type": "string"},
                        "must_change": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            "adaptations": {"type": "array", "minItems": 3, "items": {"type": "object"}},
            "uncertainties": {"type": "array", "items": {"type": "string"}},
        },
    }


def _provider(provider: str) -> tuple[str, dict[str, Any]]:
    key = provider.strip().lower()
    if key not in PROVIDERS:
        key = "other"
    return key, PROVIDERS[key]


def _permission(context: dict[str, Any]) -> str:
    basis = str(context.get("permission_basis", "user_provided"))
    if basis not in PERMISSION_BASES:
        raise ValueError(f"Unsupported permission_basis: {basis}")
    return basis


def build_prompt_pack(
    context: dict[str, Any],
    provider: str,
    output_dir: str | Path,
    *,
    mode: str | None = None,
) -> dict[str, Any]:
    """Create a paste-ready prompt, response schema, and auditable manifest."""
    basis = _permission(context)
    for required in ("objective", "language"):
        if not str(context.get(required, "")).strip():
            raise ValueError(f"Missing required context field: {required}")
    provider_key, capability = _provider(provider)
    selected_mode = mode or capability["recommended_mode"]
    if selected_mode not in MODES:
        raise ValueError(f"Unsupported mode: {selected_mode}")
    if selected_mode == "cloud-video-native" and capability["native_video"] is False:
        raise ValueError(f"{provider_key} has no documented native-video route; use cloud-evidence-pack")

    folder = Path(output_dir).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    schema = reel_analysis_schema()
    prompt = _prompt_text(context, provider_key, selected_mode, capability)
    manifest = {
        "schema_version": "1.0",
        "provider": provider_key,
        "mode": selected_mode,
        "permission_basis": basis,
        "media": context.get("media"),
        "context_fields": sorted(context),
        "required_attachments": _required_attachments(selected_mode),
        "provider_capability": capability,
        "outputs": {
            "prompt": "reel-analysis-prompt.md",
            "response_schema": "reel-analysis-schema.json",
            "manifest": "reel-analysis-manifest.json",
        },
    }
    (folder / "reel-analysis-prompt.md").write_text(prompt, encoding="utf-8")
    _write_json(folder / "reel-analysis-schema.json", schema)
    _write_json(folder / "reel-analysis-manifest.json", manifest)
    return {"output_dir": str(folder), **manifest}


def _required_attachments(mode: str) -> list[str]:
    if mode == "cloud-video-native":
        return ["authorized video file", "reel-analysis-prompt.md"]
    if mode == "cloud-evidence-pack":
        return ["transcript with timestamps", "contact sheet/keyframes", "metadata", "audio notes", "reel-analysis-prompt.md"]
    if mode == "hybrid-verified":
        return ["authorized video file", "local measured_features.json", "reel-analysis-prompt.md"]
    return ["authorized local video file"]


def _prompt_text(context: dict[str, Any], provider: str, mode: str, capability: dict[str, Any]) -> str:
    compact_context = json.dumps(context, ensure_ascii=False, indent=2, sort_keys=True)
    limitations = "\n".join(f"- {item}" for item in capability["limitations"])
    return f"""# Instagram Reel Forensic Analysis Prompt

Provider target: {provider}
Execution mode: {mode}

Analyze one authorized Instagram Reel. Inspect the entire supplied video or evidence pack, including speech, music, sound effects, silence, on-screen text, visual composition, performance, and edit rhythm.

## Non-negotiable evidence rules

1. Separate OBSERVATION from INTERPRETATION and RECOMMENDATION.
2. Never invent a timestamp, transcript, OCR string, cut, gesture, sound, metric, or causal claim.
3. Mark anything unresolved at the available sampling rate as uncertain.
4. Content structure cannot prove performance causality. Use Instagram Insights only when supplied and label their provenance.
5. Extract abstract mechanisms; do not reproduce distinctive wording, sequence, characters, identity, or protected expression.
6. Watch or inspect through the declared end of the file. If you cannot, report the exact coverage gap.

## Provider limitations to disclose

{limitations}

## Pass A — chronological evidence timeline

For every meaningful beat record start/end seconds, spoken words, readable overlay, shot/composition, subject action and expression, camera/edit event, music/SFX/silence, information introduced, and confidence. Identify the first spoken word, readable overlay, visual change, proof, payoff, CTA, and loop connection when observable.

## Pass B — mechanism analysis

Analyze hook type and promise, first-three-second comprehension, curiosity gaps, open loops, escalation, proof, payoff, CTA, pacing, semantic/visual/audio pattern interrupts, subtitle readability, cognitive load, emotional movement, and likely skip/replay points. Every interpretation must cite observation IDs, include confidence, and give at least two alternative explanations. Mark claims that require Insights.

## Pass C — Insights alignment

If timestamped retention or skip data is supplied, align each material drop or replay peak to nearby observed beats. Treat the alignment as correlation, not causation. If no timestamped curve exists, state that the video alone cannot identify actual retention loss.

## Pass D — originality-safe adaptation

State each reusable mechanism and what must change. Create exactly three original concepts for this account: close structural adaptation, moderate variation, and structurally different control. Each must include timecoded beats, spoken copy, on-screen text, shot/audio/edit directions, payoff, CTA, primary metric, counter-metric, and falsifiable hypothesis. Follow the supplied Brand Voice DNA without copying the reference creator.

## Pass E — completeness audit

State inspected start/end, whether audio was actually interpreted, any unreadable text, unresolved timestamps, missing Insights, and all other material limitations.

Return a readable report first, then one JSON object conforming exactly to the attached `reel-analysis-schema.json`. Use seconds as numbers. Do not wrap the final JSON in commentary.

## Account and task context

```json
{compact_context}
```
"""


def audit_cloud_result(report: dict[str, Any], manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    """Audit structural validity, evidence linkage, coverage, and disclosed uncertainty."""
    errors: list[str] = []
    warnings: list[str] = []
    for key in ("schema_version", "metadata", "observations", "interpretations", "mechanisms", "adaptations", "uncertainties"):
        if key not in report:
            errors.append(f"missing:{key}")
    if errors:
        return {"valid": False, "errors": errors, "warnings": warnings, "scores": {}}

    metadata = report.get("metadata", {})
    duration = _number(metadata.get("video_duration_seconds"))
    coverage = metadata.get("coverage", {})
    start = _number(coverage.get("start_seconds"), 0.0)
    end = _number(coverage.get("end_seconds"), 0.0)
    coverage_ratio = min(1.0, max(0.0, (end - start) / duration)) if duration > 0 else 0.0
    if coverage_ratio < 0.98:
        warnings.append(f"incomplete_coverage:{coverage_ratio:.3f}")
    if metadata.get("mode") not in MODES:
        errors.append("invalid:metadata.mode")
    if not isinstance(metadata.get("audio_interpreted"), bool):
        errors.append("invalid:metadata.audio_interpreted")

    observations = report.get("observations", [])
    observation_ids: set[str] = set()
    timestamp_errors = 0
    for item in observations:
        oid = str(item.get("id", ""))
        if not oid or oid in observation_ids:
            errors.append(f"invalid_or_duplicate_observation_id:{oid}")
        observation_ids.add(oid)
        item_start = _number(item.get("start_seconds"), -1)
        item_end = _number(item.get("end_seconds"), -1)
        confidence = _number(item.get("confidence"), -1)
        if item_start < 0 or item_end < item_start or (duration and item_end > duration + 0.5):
            timestamp_errors += 1
        if not 0 <= confidence <= 1:
            errors.append(f"invalid_confidence:{oid}")
    if timestamp_errors:
        errors.append(f"timestamp_errors:{timestamp_errors}")

    ungrounded = 0
    alternatives_missing = 0
    for item in report.get("interpretations", []):
        evidence_ids = item.get("evidence_ids", [])
        if not evidence_ids or any(str(eid) not in observation_ids for eid in evidence_ids):
            ungrounded += 1
        if len(item.get("alternative_explanations", [])) < 2:
            alternatives_missing += 1
    for item in report.get("mechanisms", []):
        evidence_ids = item.get("evidence_ids", [])
        if not evidence_ids or any(str(eid) not in observation_ids for eid in evidence_ids):
            ungrounded += 1
    if ungrounded:
        errors.append(f"ungrounded_claims:{ungrounded}")
    if alternatives_missing:
        errors.append(f"interpretations_missing_alternatives:{alternatives_missing}")
    if len(report.get("adaptations", [])) != 3:
        errors.append("adaptations_must_equal_three")
    if not report.get("uncertainties"):
        warnings.append("no_uncertainties_disclosed")

    if manifest:
        if manifest.get("provider") and metadata.get("provider") != manifest["provider"]:
            errors.append("provider_manifest_mismatch")
        if manifest.get("mode") and metadata.get("mode") != manifest["mode"]:
            errors.append("mode_manifest_mismatch")

    total_claims = len(report.get("interpretations", [])) + len(report.get("mechanisms", []))
    grounding_score = 1.0 if total_claims == 0 else max(0.0, 1 - ungrounded / total_claims)
    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "scores": {
            "coverage": round(coverage_ratio, 4),
            "grounding": round(grounding_score, 4),
            "uncertainty_disclosure": 1.0 if report.get("uncertainties") else 0.0,
            "schema_completeness": round((7 - sum(item.startswith("missing:") for item in errors)) / 7, 4),
        },
    }


def align_retention(report: dict[str, Any], insights: dict[str, Any], *, drop_threshold: float = 0.08) -> dict[str, Any]:
    """Align timestamped retention loss with nearby observations without claiming causality."""
    points = sorted(insights.get("retention_points", []), key=lambda item: float(item["second"]))
    events = []
    observations = report.get("observations", [])
    for previous, current in zip(points, points[1:]):
        prior_value = _number(previous.get("value"))
        value = _number(current.get("value"))
        loss = prior_value - value
        if loss < drop_threshold:
            continue
        second = _number(current.get("second"))
        nearby = [
            item for item in observations
            if _number(item.get("start_seconds"), -999) - 1 <= second <= _number(item.get("end_seconds"), -999) + 1
        ]
        events.append({
            "second": second,
            "loss": round(loss, 4),
            "nearby_observation_ids": [item.get("id") for item in nearby],
            "interpretation": "temporal_correlation_only",
        })
    return {
        "events": events,
        "source": insights.get("provenance", "user_supplied"),
        "warning": "Temporal alignment does not establish causality.",
    }


def compare_reports(reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare cloud/model reports by grounded mechanism name and coverage."""
    if len(reports) < 2:
        raise ValueError("At least two reports are required")
    counter: Counter[str] = Counter()
    providers: list[str] = []
    audits = []
    evidence: dict[str, list[dict[str, Any]]] = {}
    for report in reports:
        audit = audit_cloud_result(report)
        audits.append(audit)
        provider = str(report.get("metadata", {}).get("provider", "unknown"))
        providers.append(provider)
        for mechanism in report.get("mechanisms", []):
            name = _normalize(mechanism.get("name", ""))
            if not name or not mechanism.get("evidence_ids"):
                continue
            counter[name] += 1
            evidence.setdefault(name, []).append({"provider": provider, "evidence_ids": mechanism["evidence_ids"]})
    recurring = [
        {"mechanism": name, "report_count": count, "agreement": round(count / len(reports), 4), "evidence": evidence[name]}
        for name, count in counter.most_common()
    ]
    return {
        "report_count": len(reports),
        "providers": providers,
        "all_reports_valid": all(item["valid"] for item in audits),
        "audits": audits,
        "recurring_mechanisms": recurring,
        "warning": "Agreement can raise confidence but does not convert inference into measured fact.",
    }


def verify_hybrid(report: dict[str, Any], measured: dict[str, Any], *, tolerance_seconds: float = 0.75) -> dict[str, Any]:
    """Compare consequential cloud observations with locally measured anchors."""
    observations = report.get("observations", [])
    cloud_speech = min(
        (_number(item.get("start_seconds")) for item in observations if item.get("kind") == "speech"),
        default=None,
    )
    cloud_overlay = min(
        (_number(item.get("start_seconds")) for item in observations if item.get("kind") == "overlay"),
        default=None,
    )
    local_words = measured.get("words", [])
    local_overlays = measured.get("overlays", [])
    local_speech = min((_number(item.get("start")) for item in local_words), default=None)
    local_overlay = min((_number(item.get("start")) for item in local_overlays), default=None)

    checks = []
    for name, cloud_value, local_value in (
        ("first_spoken_second", cloud_speech, local_speech),
        ("first_overlay_second", cloud_overlay, local_overlay),
    ):
        if cloud_value is None or local_value is None:
            checks.append({"anchor": name, "status": "unavailable", "cloud": cloud_value, "local": local_value})
            continue
        delta = abs(cloud_value - local_value)
        checks.append({
            "anchor": name,
            "status": "agree" if delta <= tolerance_seconds else "disagree",
            "cloud": cloud_value,
            "local": local_value,
            "delta_seconds": round(delta, 4),
        })
    disagreements = [item for item in checks if item["status"] == "disagree"]
    return {
        "mode": "hybrid-verified",
        "tolerance_seconds": tolerance_seconds,
        "checks": checks,
        "disagreements": disagreements,
        "verified": bool(checks) and not disagreements and any(item["status"] == "agree" for item in checks),
        "warning": "Agreement covers only measured anchors; interpretations remain inference.",
    }


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize(value: Any) -> str:
    return re.sub(r"[^\w\u0600-\u06ff]+", " ", str(value).lower()).strip()


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
