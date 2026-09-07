"""Validate a private design plan or compile prompts, without image generation."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from instagram_content_intelligence.contracts import read_json, write_json
from instagram_content_intelligence.story_design import compile_prompts, validate_design


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("validate", "prompts"))
    parser.add_argument("input")
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        plan = read_json(args.input)
        result = validate_design(plan)
        if args.action == "prompts":
            result["prompts"] = compile_prompts(plan)
        if args.output:
            write_json(args.output, result, overwrite=False)
        else:
            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
            print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.exit(2, f"Design error: {exc}\n")


if __name__ == "__main__":
    main()
