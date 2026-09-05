import unittest
from dataclasses import replace

from instagram_content_intelligence.persian import comparison_key, contains_phrase
from instagram_content_intelligence.trends import score_trends
from instagram_content_intelligence.brand_voice import build_interview, build_voice_dna, score_voice_fit
from instagram_content_intelligence.insights import analyze_reel, analyze_account_distribution
from tests import test_trends
from tests.test_brand_voice import interview_fixture


class PersianIntegrityTests(unittest.TestCase):
    def setUp(self):
        fixture = test_trends.TrendTests()
        fixture.setUp()
        self.sources, self.profile = fixture.sources, fixture.profile
        self.observation = fixture.observation

    def score(self, observations, profile=None):
        return score_trends(observations, self.sources, profile or self.profile, test_trends.NOW)

    def test_locale_mismatch_is_filtered_at_observation_level(self):
        for language, region in (("en", "IR"), ("fa", "US"), ("en", "US")):
            with self.subTest(language=language, region=region):
                self.assertEqual(self.score([self.observation("topic", "search", 20, 10,
                                                            language=language, region=region)]), [])
        self.assertEqual(len(self.score([self.observation("topic", "search", 20, 10,
                                                         language="fa", region="IR")])), 1)

    def test_unknown_locale_is_explicit_and_can_be_excluded(self):
        rows = [self.observation("topic", "search", 20, 10)]
        self.assertEqual(self.score(rows)[0]["unknown_locale_observation_count"], 1)
        self.assertEqual(self.score(rows, replace(self.profile, allow_unknown_locale=False)), [])

    def test_persian_variants_share_topic_without_rewriting_evidence(self):
        rows = [self.observation("کسب‌وکار ۱۲", "search", 20, 10),
                self.observation("كسب وكار ١٢", "platform", 20, 10)]
        result = self.score(rows)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["topic"], rows[0].topic)
        self.assertEqual(result[0]["source_count"], 2)

    def test_duplicate_does_not_change_score_or_confidence(self):
        row = self.observation("کسب‌وکار", "search", 20, 10)
        original = self.score([row])
        self.assertEqual(original, self.score([row, row, row]))
        self.assertEqual(original, self.score([row, replace(row, topic="كسب وكار")]))

    def test_distinct_measurements_are_retained(self):
        row = self.observation("topic", "search", 20, 10)
        result = self.score([row, replace(row, observed_at="2026-08-29T11:00:00Z")])[0]
        self.assertEqual(result["observation_count"], 2)

    def test_forbidden_variants_and_word_boundaries(self):
        dna = {"lexical": {"forbidden": ["تضمینی", "تضميني"]}}
        self.assertEqual(len(score_voice_fit("کاملاً تضميني!", dna)["forbidden_hits"]), 1)
        self.assertTrue(contains_phrase("می رود", "می‌رود"))
        self.assertFalse(contains_phrase("کاربرد", "کار"))
        self.assertFalse(contains_phrase("anything", ""))

    def test_comparison_is_idempotent_and_preserves_diacritics(self):
        text = "  كِتاب ۱۲\nمي‌رود "
        key = comparison_key(text)
        self.assertEqual(key, "کِتاب 12 می رود")
        self.assertEqual(comparison_key(key), key)
        self.assertNotEqual(comparison_key("عَلَم"), comparison_key("علم"))

    def test_invalid_voice_dimensions_remain_gaps(self):
        for value in ("not numeric", "nan", "inf", -0.1, 1.1, True):
            with self.subTest(value=value):
                payload = interview_fixture()
                payload["answers"]["warmth"] = value
                dna = build_voice_dna(payload)
                self.assertEqual(dna["status"], "draft-with-gaps")
                self.assertIn("warmth", dna["gaps"])
                self.assertIsNone(dna["dimensions"]["warmth"])
                self.assertIn("warmth", {q["id"] for q in build_interview(payload)["questions"]})

    def test_persian_numeric_answers_and_lists(self):
        payload = interview_fixture()
        payload["answers"]["warmth"] = "۰٫۷"
        payload["answers"]["preferred_words"] = "شفاف، روشن"
        dna = build_voice_dna(payload)
        self.assertEqual(dna["dimensions"]["warmth"], 0.7)
        self.assertIn("شفاف", dna["lexical"]["preferred"])
        self.assertIn("روشن", dna["lexical"]["preferred"])

    def test_missing_evidence_keeps_interview_open(self):
        payload = interview_fixture()
        payload["positive_samples"] = []
        result = build_interview(payload)
        self.assertFalse(result["complete"])
        self.assertEqual(result["next_step"], "continue-interview")

    def test_missing_partial_and_zero_interactions_are_distinct(self):
        for metrics, status in (({"reach": 100}, "missing"),
                                ({"reach": 100, "shares": 0}, "partial")):
            result = analyze_reel(metrics)
            self.assertIsNone(result["ratios"]["interaction_per_reach"]["value"])
            self.assertEqual(result["interaction_coverage"]["status"], status)
        result = analyze_reel({"reach": 100, "shares": 0, "saves": 0, "likes": 0, "comments": 0})
        self.assertEqual(result["ratios"]["interaction_per_reach"]["value"], 0)
        self.assertEqual(result["interaction_coverage"]["status"], "complete")

    def test_incomplete_distribution_is_not_one_hundred_percent(self):
        result = analyze_account_distribution({"followers": 100})
        self.assertIsNone(result["follower_share"])
        self.assertIsNone(result["non_follower_share"])
