import tempfile
import unittest
from pathlib import Path

from instagram_content_intelligence.adapters import google_trends_csv


class AdapterTests(unittest.TestCase):
    def test_google_trends_csv_preserves_relative_scale(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "trend.csv"
            path.write_text("Week,topic\n2026-08-01,20\n2026-08-08,30\n2026-08-15,70\n", encoding="utf-8")
            observation = google_trends_csv(path, "topic")
            self.assertEqual(observation.value, 70)
            self.assertEqual(observation.baseline, 25)


if __name__ == "__main__":
    unittest.main()

