from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from instagram_content_intelligence.insights import analyze_story_sequence
from instagram_content_intelligence.brand_voice import build_voice_dna, score_voice_fit
from instagram_content_intelligence.cloud_reel import audit_cloud_result
from instagram_content_intelligence.matrix import ContentCandidate, MatrixConfig, select_portfolio
from instagram_content_intelligence.trends import SourceDescriptor, TrendObservation, TrendProfile, score_trends


def matrix_fixture():
    base = {
        "audience": "general",
        "job": "learn",
        "intent_stage": "see",
        "surface": "reel",
        "format": "explainer",
        "angle": "question",
        "evidence": "primary",
        "narrative": "promise-proof-payoff",
        "cta": "save",
        "lifecycle": "evergreen",
    }
    candidates = []
    for index, (pillar, objective) in enumerate((
        ("education", "reach"), ("education", "reach"), ("trust", "engage"),
        ("conversion", "convert"), ("community", "engage")
    )):
        scores = {key: 0.9 - index * 0.03 for key in MatrixConfig(1).score_weights}
        candidates.append(ContentCandidate(str(index), str(index), dict(base, pillar=pillar, objective=objective), scores, (index % 2, (index + 1) % 2)))
    return candidates


def main():
    matrix = select_portfolio(
        matrix_fixture(),
        MatrixConfig(4, max_per_dimension_value={"pillar": 2}, min_coverage={"pillar": 3, "objective": 3}),
    )
    trend = score_trends(
        [
            TrendObservation("topic", "a", "2026-08-29T10:00:00+00:00", 20, 10, categories=("general",)),
            TrendObservation("topic", "b", "2026-08-29T10:00:00+00:00", 200, 100, categories=("general",)),
        ],
        [SourceDescriptor("a", "search", 0.8), SourceDescriptor("b", "platform", 0.9)],
        TrendProfile("fa", "IR", ("general",)),
        datetime(2026, 8, 29, 12, tzinfo=timezone.utc),
    )[0]
    story = analyze_story_sequence([
        {"frame": 1, "reach": 1000}, {"frame": 2, "reach": 950},
        {"frame": 3, "reach": 900}, {"frame": 4, "reach": 500},
    ])
    voice = build_voice_dna({
        "answers": {
            "brand_promise": "clarity", "desired_feeling": "trust", "audience_relationship": "expert friend",
            "directness": 0.8, "warmth": 0.7, "humor": 0.2, "authority": 0.7, "emotional_intensity": 0.5,
            "preferred_words": ["اصل ماجرا"], "forbidden_phrases": ["تضمینی"], "emoji_policy": "minimal",
            "cta_style": "inviting", "claim_rules": "cite", "format_variants": {"reel": "short"},
        },
        "positive_samples": ["اصل ماجرا روشن است.", "اصل ماجرا را ببین.", "با داده تصمیم بگیر."],
        "negative_samples": ["راز تضمینی!", "اقدام مقتضی فرمایید."],
    })
    reel_audit = audit_cloud_result({
        "schema_version": "1.0",
        "metadata": {"provider": "gemini", "mode": "cloud-video-native", "video_duration_seconds": 8, "audio_interpreted": True, "coverage": {"start_seconds": 0, "end_seconds": 8}},
        "observations": [{"id": "o1", "start_seconds": 0, "end_seconds": 1, "kind": "speech", "evidence": "hook", "confidence": 0.9}],
        "interpretations": [{"claim": "gap", "evidence_ids": ["o1"], "confidence": 0.7, "alternative_explanations": ["topic", "creator"]}],
        "mechanisms": [{"name": "gap", "evidence_ids": ["o1"], "reusable_principle": "open gap", "must_change": ["words"]}],
        "adaptations": [{}, {}, {}],
        "uncertainties": ["sampling"],
    })
    checks = {
        "matrix_complete": matrix["complete"],
        "matrix_objective_coverage": len(matrix["coverage"]["objective"]) >= 3,
        "trend_convergence": trend["source_count"] == 2 and trend["confidence"] >= 0.7,
        "story_detects_injected_drop": bool(story["alerts"] and story["alerts"][0]["frame"] == 4),
        "brand_voice_rejects_forbidden_phrase": score_voice_fit("اصل ماجرا", voice)["score"] > score_voice_fit("کاملاً تضمینی", voice)["score"],
        "cloud_reel_audit_is_grounded_and_complete": reel_audit["valid"] and reel_audit["scores"]["coverage"] == 1.0,
    }
    report = {"schema_version": "1.0", "checks": checks, "passed": all(checks.values())}
    print(json.dumps(report, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
