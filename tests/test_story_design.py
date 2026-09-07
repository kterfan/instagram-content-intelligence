import copy
import json
import unittest
from pathlib import Path
from instagram_content_intelligence.story_design import compile_prompts, validate_design


class StoryDesignTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((Path(__file__).resolve().parents[1] / "examples/story-design.json").read_text(encoding="utf-8"))

    def test_prompt_preserves_visible_copy_once_and_discloses_unverified(self):
        result = validate_design(self.plan)
        self.assertFalse(result["sequence_preview"])
        self.assertIn("shaped text fit", result["unverified"])
        prompt = compile_prompts(self.plan)[0]
        for block in self.plan["slides"][0]["text_blocks"]:
            self.assertEqual(prompt.count(block["text"]), 1)

    def test_rejects_punctuation_zwnj_and_order_changes(self):
        for transform in (lambda s: s.replace(".", ""), lambda s: s.replace("\u200c", " "), lambda s: " ".join(reversed(s.split()))):
            plan = copy.deepcopy(self.plan)
            block = plan["slides"][0]["text_blocks"][0]
            block["text"] = transform(block["text"])
            with self.assertRaises(ValueError):
                validate_design(plan)

    def test_rejects_overlap_reserved_area_and_outside_canvas(self):
        for box in ([90, 900, 900, 180], [90, 1450, 900, 100], [1000, 650, 900, 180]):
            plan = copy.deepcopy(self.plan)
            plan["slides"][0]["text_blocks"][0]["box"] = box
            with self.assertRaises(ValueError):
                validate_design(plan)

    def test_rejects_undeclared_weight_nonfinite_size_and_invalid_color(self):
        for key, value in (("weight", "Black"), ("size", float("nan")), ("color", "red")):
            plan = copy.deepcopy(self.plan)
            plan["slides"][0]["text_blocks"][0][key] = value
            with self.assertRaises(ValueError):
                validate_design(plan)

    def test_whitespace_reflow_allowed(self):
        self.plan["slides"][0]["text_blocks"][0]["text"] = self.plan["slides"][0]["text_blocks"][0]["text"].replace(" ", "\n")
        self.assertEqual(validate_design(self.plan)["status"], "structurally_valid")

    def test_sequence_rejects_family_and_asset_drift(self):
        for target in ("slide", "block"):
            for key, value in (("font_family", "Different"), ("font_asset", "different.woff2")):
                plan = copy.deepcopy(self.plan)
                plan["slides"].append(copy.deepcopy(plan["slides"][0]))
                node = plan["slides"][1]
                if target == "block":
                    node = node["text_blocks"][0]
                node[key] = value
                with self.assertRaisesRegex(ValueError, "sequence font lock"):
                    validate_design(plan)

    def test_every_prompt_carries_same_lock(self):
        self.plan["profile"]["font_asset"] = "private/font-package-v1"
        self.plan["slides"].append(copy.deepcopy(self.plan["slides"][0]))
        for prompt in compile_prompts(self.plan):
            self.assertIn("[SEQUENCE FONT LOCK]", prompt)
            self.assertIn("private/font-package-v1", prompt)

    def test_resolution_and_profiles_are_independent(self):
        for family in ("Yekan Bakh", "Peyda"):
            self.plan["profile"]["font_family"] = family
            self.assertIn(family, compile_prompts(self.plan)[0])
        self.plan["output_size"] = [4320, 7680]
        self.assertIn("4320x7680", compile_prompts(self.plan)[0])
        self.plan["output_size"] = [1920, 1080]
        with self.assertRaises(ValueError):
            validate_design(self.plan)
