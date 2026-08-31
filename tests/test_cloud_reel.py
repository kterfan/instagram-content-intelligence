import json
import tempfile
import unittest
from pathlib import Path

from instagram_content_intelligence.cloud_reel import (
    align_retention,
    audit_cloud_result,
    build_prompt_pack,
    compare_reports,
    verify_hybrid,
)


def valid_report(provider="gemini", mode="cloud-video-native"):
    return {
        "schema_version": "1.0",
        "metadata": {
            "provider": provider,
            "model_or_surface": None,
            "mode": mode,
            "video_duration_seconds": 10,
            "audio_interpreted": True,
            "coverage": {"start_seconds": 0, "end_seconds": 10},
            "limitations": ["sampling"],
        },
        "observations": [
            {"id": "o1", "start_seconds": 0, "end_seconds": 2, "kind": "speech", "evidence": "question hook", "confidence": 0.9},
            {"id": "o2", "start_seconds": 4, "end_seconds": 5, "kind": "edit", "evidence": "cut to proof", "confidence": 0.8},
        ],
        "interpretations": [
            {
                "claim": "The question opens a knowledge gap",
                "evidence_ids": ["o1"],
                "confidence": 0.7,
                "alternative_explanations": ["topic demand", "creator familiarity"],
                "requires_insights": True,
            }
        ],
        "mechanisms": [
            {"name": "question gap", "evidence_ids": ["o1"], "reusable_principle": "open a relevant gap", "must_change": ["wording", "example"]}
        ],
        "adaptations": [{"distance": "close"}, {"distance": "moderate"}, {"distance": "control"}],
        "uncertainties": ["sub-second edits may be missed"],
    }


class CloudReelTests(unittest.TestCase):
    def test_gemini_prompt_pack_is_installation_free(self):
        context = {"permission_basis": "owned", "objective": "find mechanisms", "language": "fa"}
        with tempfile.TemporaryDirectory() as folder:
            result = build_prompt_pack(context, "gemini", folder)
            prompt = (Path(folder) / "reel-analysis-prompt.md").read_text(encoding="utf-8")
            schema = json.loads((Path(folder) / "reel-analysis-schema.json").read_text(encoding="utf-8"))
        self.assertEqual(result["mode"], "cloud-video-native")
        self.assertIn("Separate OBSERVATION", prompt)
        self.assertIn("observations", schema["required"])

    def test_claude_routes_to_evidence_pack_and_rejects_native(self):
        context = {"permission_basis": "user_provided", "objective": "analyze", "language": "fa"}
        with tempfile.TemporaryDirectory() as folder:
            result = build_prompt_pack(context, "claude", folder)
        self.assertEqual(result["mode"], "cloud-evidence-pack")
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                build_prompt_pack(context, "claude", folder, mode="cloud-video-native")

    def test_audit_checks_coverage_and_grounding(self):
        report = valid_report()
        audit = audit_cloud_result(report)
        self.assertTrue(audit["valid"])
        self.assertEqual(audit["scores"]["coverage"], 1.0)
        report["interpretations"][0]["evidence_ids"] = ["missing"]
        self.assertFalse(audit_cloud_result(report)["valid"])

    def test_retention_alignment_is_correlation_only(self):
        result = align_retention(
            valid_report(),
            {"retention_points": [{"second": 0, "value": 1.0}, {"second": 4.5, "value": 0.75}]},
        )
        self.assertEqual(result["events"][0]["nearby_observation_ids"], ["o2"])
        self.assertIn("does not establish causality", result["warning"])

    def test_compare_reports_preserves_agreement_as_inference(self):
        second = valid_report("chatgpt")
        result = compare_reports([valid_report(), second])
        self.assertEqual(result["recurring_mechanisms"][0]["agreement"], 1.0)
        self.assertTrue(result["all_reports_valid"])

    def test_hybrid_verifies_measured_anchors(self):
        report = valid_report()
        report["observations"].append(
            {"id": "o3", "start_seconds": 0.3, "end_seconds": 1, "kind": "overlay", "evidence": "title", "confidence": 0.8}
        )
        measured = {"words": [{"start": 0.4}], "overlays": [{"start": 0.2, "text": "title"}]}
        result = verify_hybrid(report, measured)
        self.assertTrue(result["verified"])
        self.assertEqual(result["disagreements"], [])


if __name__ == "__main__":
    unittest.main()
