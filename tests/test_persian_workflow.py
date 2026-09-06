import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from instagram_content_intelligence.calendar_fa import parse_date, jalali_label, local_instant, calendar_days, write_ics
from instagram_content_intelligence.contracts import number, read_json
from instagram_content_intelligence.production import project_init, save_production, latest_production, export_production, validate_production, guided_init
from instagram_content_intelligence.subtitles import subtitle_pack
from instagram_content_intelligence.learning import bind_result, validate_result, record_results, read_results, compare_results, import_csv
from instagram_content_intelligence.evaluation import prepare_evaluation, score_evaluation, RUBRIC
from instagram_content_intelligence.visual import render_rtl_html, screenshot_html, surface_spec

ROOT = Path(__file__).resolve().parents[1]


def fixture(name):
    return read_json(ROOT / "examples" / name)


class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.brief = fixture("persian-brief.json")
        self.brief["timezone"] = "UTC"
        self.content = fixture("persian-production.json")

    def test_version_identity_changes_with_content_and_preserves_history(self):
        with tempfile.TemporaryDirectory() as folder:
            project_init(folder, self.brief)
            first = save_production(folder, self.content)
            self.assertEqual(first["revision"], save_production(folder, self.content)["revision"])
            self.content["caption"] += " متن تازه."
            second = save_production(folder, self.content)
            self.assertNotEqual(first["revision"], second["revision"])
            self.assertEqual(len(list((Path(folder) / "versions").glob("*.json"))), 2)
            self.assertEqual(latest_production(folder)["revision"], second["revision"])

    def test_init_never_overwrites_a_project(self):
        with tempfile.TemporaryDirectory() as folder:
            project_init(folder, self.brief)
            with self.assertRaises(FileExistsError):
                project_init(folder, self.brief)

    def test_guided_init_does_not_infer_country_from_language(self):
        answers = iter(["account", "مخاطب مهاجر", "fa", "DE", "UTC", "موضوع", "save_per_reach", "وعده", "صمیمی", "story"])
        with tempfile.TemporaryDirectory() as folder:
            result = guided_init(folder, ask=lambda _: next(answers))
            self.assertEqual(result["brief"]["region"], "DE")

    def test_external_claim_without_evidence_is_rejected(self):
        self.content["frames"][0]["claim_basis"] = "external_evidence"
        with self.assertRaises(ValueError):
            validate_production(self.content)

    def test_evidence_reference_must_resolve(self):
        self.content["frames"][0]["evidence_ids"] = ["missing"]
        with self.assertRaises(ValueError):
            validate_production(self.content)

    def test_open_loop_requires_continuation_and_final_payoff(self):
        self.content["frames"][0]["continuation"] = ""
        with self.assertRaises(ValueError):
            validate_production(self.content)
        self.content = fixture("persian-production.json")
        self.content["frames"][-1]["role"] = "value"
        with self.assertRaises(ValueError):
            validate_production(self.content)

    def test_reel_overlap_is_rejected(self):
        self.content["frames"][1]["start"] = 4
        with self.assertRaises(ValueError):
            validate_production(self.content)

    def test_story_and_carousel_export_complete_packs(self):
        for surface in ("story", "carousel"):
            with self.subTest(surface=surface), tempfile.TemporaryDirectory() as folder:
                self.brief["surface"] = self.content["surface"] = surface
                project_init(folder, self.brief)
                save_production(folder, self.content)
                result = export_production(folder, Path(folder) / "export")
                out = Path(result["directory"])
                self.assertTrue((out / "cover.html").exists())
                self.assertEqual(len(list(out.glob("frame-*.html"))), 3)
                self.assertIn("@font-face", (out / "cover.html").read_text(encoding="utf-8"))
                self.assertIn(self.content["caption"], (out / "caption.txt").read_text(encoding="utf-8"))
                self.assertFalse(result["published"])

    def test_reel_exports_subtitles_and_escaped_csv(self):
        self.content["frames"][0]["visual"] = '=HYPERLINK("example")'
        with tempfile.TemporaryDirectory() as folder:
            project_init(folder, self.brief)
            save_production(folder, self.content)
            out = Path(export_production(folder, Path(folder) / "exports")["directory"])
            self.assertTrue((out / "subtitles.srt").exists())
            self.assertTrue((out / "subtitles.vtt").exists())
            self.assertIn("'=HYPERLINK", (out / "shot-list.csv").read_text(encoding="utf-8-sig"))

    def test_cli_workflow_from_outside_repo(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            brief = root / "brief.json"
            brief.write_text(json.dumps(self.brief), encoding="utf-8")
            def run(*args):
                return subprocess.run([sys.executable, str(ROOT / "scripts/ici.py"), *args], cwd=root, capture_output=True, check=True)
            run("workflow", "init", "--project", str(root / "project"), "--input", str(brief))
            run("workflow", "import", "--project", str(root / "project"), "--input", str(ROOT / "examples/persian-production.json"))
            result = json.loads(run("workflow", "export", "--project", str(root / "project"), "--output-dir", str(root / "out")).stdout)
            self.assertTrue(Path(result["directory"]).exists())


class SubtitleTests(unittest.TestCase):
    def test_utf8_subtitles_and_millisecond_carry(self):
        result = subtitle_pack([{"start": 59.9996, "end": 62, "text": "می‌روم با API و ۱۲۳"}])
        self.assertIn("00:01:00,000", result["srt"])
        self.assertIn("می‌روم", result["srt"])
        self.assertTrue(result["vtt"].startswith("WEBVTT"))

    def test_overlap_and_nan_rejected(self):
        for cues in ([{"start": 0, "end": 2, "text": "اول"}, {"start": 1, "end": 3, "text": "دوم"}],
                     [{"start": 0, "end": float("nan"), "text": "نامعتبر"}]):
            with self.assertRaises(ValueError):
                subtitle_pack(cues)

    def test_dense_copy_is_warned_not_truncated(self):
        result = subtitle_pack([{"start": 0, "end": 1, "text": "این متن فارسی خواندنی است " * 10}])
        self.assertTrue(result["warnings"])
        self.assertEqual(result["srt"].count("خواندنی"), 10)

    def test_vtt_does_not_interpret_markup(self):
        result = subtitle_pack([{"start": 0, "end": 5, "text": "<b>متن</b>"}])
        self.assertIn("&lt;b&gt;", result["vtt"])


@unittest.skipUnless(importlib.util.find_spec("jdatetime"), "optional calendar dependencies")
class CalendarTests(unittest.TestCase):
    def test_nowruz_and_leap_boundaries(self):
        self.assertEqual(parse_date("۱۴۰۳/۰۱/۰۱").isoformat(), "2024-03-20")
        self.assertEqual(parse_date("1404-01-01").isoformat(), "2025-03-21")
        self.assertEqual(parse_date("1399-12-30").isoformat(), "2021-03-20")
        with self.assertRaises(ValueError):
            parse_date("1400-12-30")

    def test_round_trip_and_midnight_crossing(self):
        day = parse_date("1405-06-15")
        self.assertEqual(jalali_label(day), "1405-06-15")
        rows = calendar_days("1405-06-15", 1, time="00:30")
        self.assertNotEqual(rows[0]["utc"][:10], rows[0]["gregorian"])

    def test_sourced_events_and_ics(self):
        events = read_json(ROOT / "config/iran-occasions.json")
        rows = calendar_days("1405-09-30", 2, events=events)
        self.assertEqual(len(rows[0]["occasions"]), 1)
        self.assertEqual(rows[1]["occasions"], [])
        with tempfile.TemporaryDirectory() as folder:
            data = write_ics(rows, Path(folder) / "calendar.ics", title="عنوان فارسی " * 20).read_bytes()
            self.assertIn(b"DTSTART:", data)
            self.assertTrue(all(len(line) <= 75 for line in data.split(b"\r\n")))

    def test_dst_nonexistent_and_ambiguous_time_rejected(self):
        from datetime import date
        for day in (date(2025, 3, 9), date(2025, 11, 2)):
            with self.assertRaises(ValueError):
                local_instant(day, "02:30" if day.month == 3 else "01:30", "America/New_York")


class LearningTests(unittest.TestCase):
    def row(self, variant="a", index=0, **changes):
        row = fixture("publication-result.json")
        row.update(account="demo", content_id="c1", revision="abc", surface="reel", objective="save_per_reach", media_id=f"{variant}-{index}", variant=variant)
        row.update(changes)
        return row

    def test_missing_and_uncertain_results_are_not_success(self):
        for changes in ({"reviewed": False}, {"uncertain_fields": ["reach"]}, {"reach": "nan"}, {"window_hours": 48}):
            with self.assertRaises(ValueError):
                validate_result(self.row(**changes))

    def test_idempotency_and_atomic_batch_conflict(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "results.sqlite"
            self.assertEqual(record_results(db, [self.row()])["added"], 1)
            self.assertEqual(record_results(db, [self.row()])["duplicates"], 1)
            with self.assertRaises(ValueError):
                record_results(db, [self.row(index=1), self.row(reach=2000)])
            self.assertEqual(len(read_results(db)), 1)

    def test_comparison_separates_paid_and_organic_and_requires_samples(self):
        rows = [self.row("a", i) for i in range(5)] + [self.row("b", i, shares=40) for i in range(5)]
        report = compare_results(rows)
        self.assertEqual(report["groups"][0]["status"], "observational_comparison")
        self.assertAlmostEqual(report["groups"][0]["comparisons"][0]["median_difference"], 0.028)
        self.assertEqual(report, compare_results(rows))
        rows[-1]["traffic"] = "paid"
        self.assertTrue(all(group["status"] == "insufficient_data" for group in compare_results(rows)["groups"]))

    def test_duplicate_and_missing_metrics(self):
        with self.assertRaises(ValueError):
            compare_results([self.row(), self.row()])
        result = compare_results([self.row(shares=None)])
        self.assertEqual(result["excluded_missing_or_zero_reach"], 1)
        self.assertEqual(result["groups"], [])

    def test_project_result_binding_rejects_wrong_revision(self):
        with tempfile.TemporaryDirectory() as folder:
            brief = fixture("persian-brief.json")
            brief["timezone"] = "UTC"
            project_init(folder, brief)
            saved = save_production(folder, fixture("persian-production.json"))
            result = bind_result(folder, fixture("publication-result.json"))
            self.assertEqual(result["revision"], saved["revision"])
            changed = fixture("persian-production.json")
            changed["caption"] += " تازه"
            save_production(folder, changed)
            old_result = bind_result(folder, dict(fixture("publication-result.json"), revision=saved["revision"]))
            self.assertEqual(old_result["revision"], saved["revision"])
            with self.assertRaises(ValueError):
                bind_result(folder, dict(fixture("publication-result.json"), revision="wrong"))

    def test_csv_persian_counts(self):
        import csv
        with tempfile.TemporaryDirectory() as folder:
            row = self.row(reach="۱٬۰۰۰")
            row.update(reviewed="true", uncertain_fields="")
            source = Path(folder) / "source.csv"
            with source.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(row))
                writer.writeheader()
                writer.writerow(row)
            db = Path(folder) / "results.sqlite"
            import_csv(db, source)
            self.assertEqual(read_results(db)[0]["reach"], 1000)


class EvaluationTests(unittest.TestCase):
    def test_key_is_separate_and_missing_ratings_incomplete(self):
        with tempfile.TemporaryDirectory() as folder:
            prepare_evaluation(fixture("quality-candidates.json"), folder)
            pack = read_json(Path(folder) / "blind.json")
            self.assertNotIn("label", pack["items"][0])
            self.assertNotIn("mapping", pack)
            ratings = read_json(Path(folder) / "ratings-template.json")
            ratings["evaluator"] = "synthetic-test-rater"
            result = score_evaluation(pack, ratings)
            self.assertFalse(result["complete"])
            self.assertEqual(result["results"], [])
            for row in ratings["ratings"]:
                row["scores"] = dict.fromkeys(RUBRIC, 4)
                row["reason"] = "Synthetic test input, not a real evaluation"
            self.assertTrue(score_evaluation(pack, ratings)["complete"])
            ratings["ratings"].append(ratings["ratings"][0])
            with self.assertRaises(ValueError):
                score_evaluation(pack, ratings)


@unittest.skipUnless(importlib.util.find_spec("jsonschema"), "optional schema validator")
class SchemaTests(unittest.TestCase):
    def test_production_contract_and_reel_fields(self):
        import jsonschema
        schema = read_json(ROOT / "schemas/production.schema.json")
        payload = fixture("persian-production.json")
        jsonschema.validate(payload, schema)
        del payload["frames"][0]["spoken"]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(payload, schema)

    def test_reviewed_result_schema(self):
        import jsonschema
        schema = read_json(ROOT / "schemas/publication-result.schema.json")
        row = LearningTests().row()
        jsonschema.validate(row, schema)
        row["reviewed"] = False
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(row, schema)


@unittest.skipUnless(os.getenv("ICI_VISUAL_TESTS") == "1", "opt-in browser rendering")
class VisualIntegrationTests(unittest.TestCase):
    def test_bundled_font_renders_both_aspect_ratios(self):
        with tempfile.TemporaryDirectory() as folder:
            for surface in ("story", "carousel"):
                spec = surface_spec(surface)
                path = render_rtl_html("فارسی و API", "می‌روم؛ قیمت ۱۲۳ تومان\nhello@example.com", Path(folder) / f"{surface}.html", spec)
                png = screenshot_html(path, Path(folder) / f"{surface}.png", spec)
                self.assertTrue(png.read_bytes().startswith(b"\x89PNG"))

    def test_overflow_rejects_png_without_deleting_existing_output(self):
        with tempfile.TemporaryDirectory() as folder:
            spec = surface_spec("carousel")
            source = render_rtl_html("تیتر", "متن طولانی " * 1000, Path(folder) / "overflow.html", spec)
            target = Path(folder) / "keep.png"
            target.write_bytes(b"existing")
            with self.assertRaises(ValueError):
                screenshot_html(source, target, spec)
            self.assertEqual(target.read_bytes(), b"existing")
