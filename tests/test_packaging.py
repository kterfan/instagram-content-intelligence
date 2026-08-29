import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    def test_installation_free_runner_works_outside_repo(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "ici.py"), "doctor"],
                cwd=folder,
                check=True,
                capture_output=True,
            )
        report = json.loads(result.stdout.decode("utf-8"))
        self.assertTrue(report["capabilities"]["core_analytics"])

    def test_repository_validator_covers_both_plugin_formats(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_repository.py")],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Codex + Claude packaging", result.stdout)


if __name__ == "__main__":
    unittest.main()

