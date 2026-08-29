import unittest
from datetime import datetime, timezone

from instagram_content_intelligence.trends import (
    SourceDescriptor,
    TrendObservation,
    TrendProfile,
    score_trends,
)


NOW = datetime(2026, 8, 29, 12, tzinfo=timezone.utc)


class TrendTests(unittest.TestCase):
    def setUp(self):
        self.sources = [
            SourceDescriptor("search", "search_interest", 0.8),
            SourceDescriptor("platform", "platform_native", 0.9),
            SourceDescriptor("medical", "scholarly", 0.95, categories=("health",)),
        ]
        self.profile = TrendProfile("fa", "IR", ("education",), min_sources=2)

    def observation(self, topic, source, value, baseline, **kwargs):
        return TrendObservation(
            topic,
            source,
            "2026-08-29T10:00:00+00:00",
            value,
            baseline,
            categories=("education",),
            **kwargs,
        )

    def test_cross_source_convergence_increases_confidence(self):
        results = score_trends(
            [
                self.observation("Topic A", "search", 20, 10),
                self.observation("Topic A", "platform", 200, 100),
                self.observation("Topic B", "search", 20, 10),
            ],
            self.sources,
            self.profile,
            NOW,
        )
        indexed = {item["topic"]: item for item in results}
        self.assertGreater(indexed["Topic A"]["confidence"], indexed["Topic B"]["confidence"])

    def test_raw_scale_is_not_treated_as_cross_source_volume(self):
        first = score_trends(
            [self.observation("Topic", "search", 20, 10)], self.sources, self.profile, NOW
        )[0]["score"]
        second = score_trends(
            [self.observation("Topic", "search", 2000, 1000)], self.sources, self.profile, NOW
        )[0]["score"]
        self.assertAlmostEqual(first, second)

    def test_irrelevant_category_source_is_filtered(self):
        results = score_trends(
            [self.observation("Topic", "medical", 50, 10)], self.sources, self.profile, NOW
        )
        self.assertEqual(results, [])

    def test_saturation_and_risk_reduce_score(self):
        safe = score_trends(
            [self.observation("Safe", "search", 20, 10)], self.sources, self.profile, NOW
        )[0]
        risky = score_trends(
            [self.observation("Risky", "search", 20, 10, saturation=1, risk=1)],
            self.sources,
            self.profile,
            NOW,
        )[0]
        self.assertGreater(safe["score"], risky["score"])


if __name__ == "__main__":
    unittest.main()

