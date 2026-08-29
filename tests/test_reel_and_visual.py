import tempfile
import unittest
from pathlib import Path

from instagram_content_intelligence.reel_reverse import analyze_measured_features, build_analysis_manifest
from instagram_content_intelligence.visual import render_rtl_html


class ReelVisualTests(unittest.TestCase):
    def test_measured_reel_features(self):
        result = analyze_measured_features(
            {
                "duration_seconds": 30,
                "words": [{"start": 0.5}] * 60,
                "shots": [{"start": 0, "end": 5}, {"start": 5, "end": 30}],
                "overlays": [{"start": 0.2, "text": "هوک"}],
            }
        )
        self.assertEqual(result["speech"]["words_per_minute"], 120)
        self.assertEqual(result["editing"]["shot_count"], 2)

    def test_manifest_rejects_undeclared_permission(self):
        with self.assertRaises(ValueError):
            build_analysis_manifest("reference.mp4", "scraped")

    def test_persian_text_is_exact_in_html(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "frame.html"
            render_rtl_html("مهندسی معکوس ریل", "متن دقیق فارسی", target)
            document = target.read_text(encoding="utf-8")
            self.assertIn('dir="rtl"', document)
            self.assertIn("مهندسی معکوس ریل", document)
            self.assertIn("متن دقیق فارسی", document)


if __name__ == "__main__":
    unittest.main()

