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

    def test_prompt_pack_runner_works_outside_repo(self):
        with tempfile.TemporaryDirectory() as folder:
            output_dir = Path(folder) / "pack"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "ici.py"),
                    "reel",
                    "prompt-pack",
                    "--input",
                    str(ROOT / "examples" / "reel-cloud-context.json"),
                    "--provider",
                    "gemini",
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=folder,
                check=True,
                capture_output=True,
            )
            prompt_exists = (output_dir / "reel-analysis-prompt.md").is_file()
        report = json.loads(result.stdout.decode("utf-8"))
        self.assertEqual(report["mode"], "cloud-video-native")
        self.assertTrue(prompt_exists)

    def test_brand_voice_runner_works_outside_repo(self):
        with tempfile.TemporaryDirectory() as folder:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "ici.py"),
                    "voice",
                    "dna",
                    "--input",
                    str(ROOT / "examples" / "brand-voice-interview.json"),
                ],
                cwd=folder,
                check=True,
                capture_output=True,
            )
        dna = json.loads(result.stdout.decode("utf-8"))
        self.assertEqual(dna["status"], "validated-input-ready")


if __name__ == "__main__":
    unittest.main()
