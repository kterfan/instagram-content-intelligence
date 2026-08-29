import unittest

from instagram_content_intelligence.insights import (
    analyze_account_distribution,
    analyze_reel,
    analyze_story_sequence,
    safe_rate,
)


class InsightsTests(unittest.TestCase):
    def test_zero_denominator_is_unavailable(self):
        self.assertIsNone(safe_rate(5, 0))

    def test_reel_ratios_use_reach(self):
        result = analyze_reel({"reach": 1000, "views": 1500, "shares": 50, "saved": 100})
        self.assertEqual(result["ratios"]["share_per_reach"]["value"], 0.05)
        self.assertEqual(result["ratios"]["save_per_reach"]["value"], 0.1)

    def test_reel_api_scope_warning(self):
        result = analyze_reel(
            {
                "reach": 100,
                "follows": 10,
                "_provenance": {"follows": {"kind": "meta_api", "scope": "single_media"}},
            }
        )
        self.assertTrue(any("not documented" in warning for warning in result["scope_warnings"]))

    def test_story_abnormal_drop_is_flagged(self):
        frames = [
            {"frame": 1, "reach": 1000},
            {"frame": 2, "reach": 950},
            {"frame": 3, "reach": 900},
            {"frame": 4, "reach": 500},
        ]
        result = analyze_story_sequence(frames)
        self.assertEqual(result["alerts"][0]["frame"], 4)

    def test_account_nonfollower_scope(self):
        result = analyze_account_distribution({"followers": 600, "non_followers": 400})
        self.assertEqual(result["non_follower_share"], 0.4)
        self.assertEqual(result["scope"], "account_interval")


if __name__ == "__main__":
    unittest.main()

