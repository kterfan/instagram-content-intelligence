import unittest

from instagram_content_intelligence.brand_voice import (
    build_blind_test,
    build_interview,
    build_voice_dna,
    detect_voice_drift,
    evaluate_blind_test,
    rank_candidates,
    score_voice_fit,
)


def interview_fixture():
    return {
        "answers": {
            "brand_promise": "clarity",
            "desired_feeling": "trust",
            "audience_relationship": "expert friend",
            "directness": 0.8,
            "warmth": 0.7,
            "humor": 0.2,
            "authority": 0.7,
            "emotional_intensity": 0.5,
            "formality": 0.3,
            "metaphor_density": 0.2,
            "code_switching": "minimal",
            "preferred_words": ["اصل ماجرا"],
            "forbidden_phrases": ["صددرصد تضمینی"],
            "emoji_policy": "minimal",
            "cta_style": "inviting",
            "claim_rules": "cite performance claims",
            "format_variants": {"reel": "short", "story": "conversational"},
        },
        "positive_samples": [
            "اصل ماجرا ساده است. اول داده را ببین.",
            "ببین، اینجا باید ادعا را از شاهد جدا کنیم.",
            "اصل ماجرا چیست؟ تصمیم روشن، بعد از دیدن داده.",
        ],
        "negative_samples": [
            "این راز صددرصد تضمینی است!",
            "در راستای تحقق اهداف اقدام فرمایید.",
        ],
        "format_samples": {"reel": ["x"], "story": ["y"]},
    }


class BrandVoiceTests(unittest.TestCase):
    def test_interview_asks_only_gaps(self):
        result = build_interview({"answers": {"brand_promise": "clarity"}})
        self.assertFalse(result["complete"])
        self.assertNotIn("brand_promise", {item["id"] for item in result["questions"]})

    def test_voice_dna_has_evidence_and_no_gaps_for_complete_fixture(self):
        dna = build_voice_dna(interview_fixture())
        self.assertEqual(dna["status"], "validated-input-ready")
        self.assertEqual(dna["gaps"], [])
        self.assertEqual(dna["evidence"]["positive_sample_count"], 3)
        self.assertIn("اصل ماجرا", dna["lexical"]["preferred"])

    def test_forbidden_language_reduces_fit(self):
        dna = build_voice_dna(interview_fixture())
        good = score_voice_fit("اصل ماجرا را با داده ببین.", dna)
        bad = score_voice_fit("این روش صددرصد تضمینی است!", dna)
        self.assertGreater(good["score"], bad["score"])

    def test_blind_test_is_deterministic_and_evaluable(self):
        candidates = [{"text": "A", "label": "authentic"}, {"text": "B", "label": "generic"}]
        pack = build_blind_test(candidates, seed=7)
        again = build_blind_test(candidates, seed=7)
        self.assertEqual(pack, again)
        result = evaluate_blind_test(pack, dict(pack["answer_key"]))
        self.assertEqual(result["accuracy"], 1.0)

    def test_rank_requires_owner_acceptance(self):
        dna = build_voice_dna(interview_fixture())
        result = rank_candidates([{"id": "a", "text": "اصل ماجرا"}, {"id": "b", "text": "صددرصد تضمینی"}], dna)
        self.assertEqual(result["ranked"][0]["id"], "a")
        self.assertTrue(result["acceptance_requires_owner_blind_test"])

    def test_drift_requires_owner_review(self):
        previous = build_voice_dna(interview_fixture())
        changed = interview_fixture()
        changed["version"] = "2"
        changed["answers"]["directness"] = 0.2
        current = build_voice_dna(changed)
        result = detect_voice_drift(previous, current)
        self.assertTrue(result["drift_detected"])
        self.assertTrue(result["requires_owner_review"])


if __name__ == "__main__":
    unittest.main()
