from __future__ import annotations

import argparse
import json
import sys
from dataclasses import fields
from pathlib import Path
from typing import Any

from .brand_voice import (
    build_blind_test,
    build_interview,
    build_voice_dna,
    evaluate_blind_test,
    detect_voice_drift,
    rank_candidates,
    score_voice_fit,
)
from .cloud_reel import align_retention, audit_cloud_result, build_prompt_pack, compare_reports, verify_hybrid
from .insights import analyze_account_distribution, analyze_reel, analyze_story_sequence
from .doctor import environment_report
from .matrix import ContentCandidate, MatrixConfig, select_portfolio
from .reel_reverse import analyze_measured_features, build_analysis_manifest, inspect_toolchain, probe_media, run_local_pipeline
from .story import design_story_sequence
from .trends import SourceDescriptor, TrendObservation, TrendProfile, score_trends
from .visual import VisualSpec, render_rtl_html, screenshot_html
from .visual import surface_spec
from .contracts import read_json, write_json
from .calendar_fa import calendar_days, write_ics
from .production import guided_init, guided_compose, project_init, save_production, latest_production, export_production, production_prompt
from .learning import bind_result, record_results, import_csv, read_results, compare_results
from .evaluation import prepare_evaluation, score_evaluation
from .subtitles import subtitle_pack


def _load(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write(data: Any, path: str | None) -> None:
    serialized = json.dumps(data, ensure_ascii=False, indent=2)
    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(serialized + "\n", encoding="utf-8")
    else:
        # Windows consoles can default to a legacy code page that cannot encode Persian.
        sys.stdout.buffer.write((serialized + "\n").encode("utf-8"))


def _dataclass_kwargs(cls: type, payload: dict[str, Any]) -> dict[str, Any]:
    allowed = {item.name for item in fields(cls)}
    return {key: value for key, value in payload.items() if key in allowed}


def cmd_trends(args: argparse.Namespace) -> None:
    payload = _load(args.input)
    observations = [TrendObservation(**item) for item in payload["observations"]]
    sources = [SourceDescriptor(**item) for item in payload["sources"]]
    profile = TrendProfile(**payload["profile"])
    _write(score_trends(observations, sources, profile), args.output)


def cmd_matrix(args: argparse.Namespace) -> None:
    payload = _load(args.input)
    candidates = [ContentCandidate(**item) for item in payload["candidates"]]
    config = MatrixConfig(**payload["config"])
    _write(select_portfolio(candidates, config), args.output)


def cmd_insights(args: argparse.Namespace) -> None:
    payload = _load(args.input)
    if args.kind == "reel":
        result = analyze_reel(payload, args.duration)
    elif args.kind == "story":
        result = analyze_story_sequence(payload["frames"] if isinstance(payload, dict) else payload)
    else:
        result = analyze_account_distribution(payload)
    _write(result, args.output)


def cmd_story_plan(args: argparse.Namespace) -> None:
    _write(
        design_story_sequence(args.objective, args.audience_job, args.promise, args.frames),
        args.output,
    )


def cmd_reel(args: argparse.Namespace) -> None:
    if args.action == "toolchain":
        result = inspect_toolchain()
    elif args.action == "probe":
        result = probe_media(args.media)
    elif args.action == "manifest":
        result = build_analysis_manifest(args.media, args.permission_basis)
    elif args.action == "pipeline":
        result = run_local_pipeline(
            args.media,
            args.output_dir,
            args.permission_basis,
            whisper_model=args.whisper_model,
            language=args.language,
            strict=args.strict,
        )
    elif args.action == "prompt-pack":
        result = build_prompt_pack(
            _load(args.input),
            args.provider,
            args.output_dir,
            mode=args.mode,
        )
    elif args.action == "audit":
        result = audit_cloud_result(
            _load(args.input),
            _load(args.manifest) if args.manifest else None,
        )
    elif args.action == "compare":
        payload = _load(args.input)
        result = compare_reports(payload["reports"] if isinstance(payload, dict) else payload)
    elif args.action == "align-retention":
        result = align_retention(_load(args.input), _load(args.insights), drop_threshold=args.drop_threshold)
    elif args.action == "hybrid-verify":
        result = verify_hybrid(_load(args.input), _load(args.measured), tolerance_seconds=args.tolerance_seconds)
    else:
        result = analyze_measured_features(_load(args.input))
    _write(result, args.output)


def cmd_voice(args: argparse.Namespace) -> None:
    payload = _load(args.input)
    if args.action == "interview":
        result = build_interview(payload)
    elif args.action == "dna":
        result = build_voice_dna(payload)
    elif args.action == "score":
        text = args.text if args.text is not None else payload["text"]
        dna = _load(args.dna) if args.dna else payload["dna"]
        result = score_voice_fit(text, dna)
    elif args.action == "blind-test":
        candidates = payload["candidates"] if isinstance(payload, dict) else payload
        result = build_blind_test(candidates, seed=args.seed)
    elif args.action == "evaluate":
        result = evaluate_blind_test(payload["pack"], payload["selections"])
    elif args.action == "drift":
        result = detect_voice_drift(payload["previous"], payload["current"], threshold=args.drift_threshold)
    else:
        result = rank_candidates(payload["candidates"], payload["dna"])
    _write(result, args.output)


def cmd_visual(args: argparse.Namespace) -> None:
    spec = surface_spec(args.surface)
    html_path = render_rtl_html(args.headline, args.body, args.html, spec, args.background, args.kicker)
    result = {"html": str(html_path)}
    if args.png:
        result["png"] = str(screenshot_html(html_path, args.png, spec))
    _write(result, args.output)


def cmd_doctor(args: argparse.Namespace) -> None:
    _write(environment_report(), args.output)


def cmd_workflow(args):
    if args.action == "init":
        result = project_init(args.project, read_json(args.input)) if args.input else guided_init(args.project)
    elif args.action == "compose":
        result = guided_compose(args.project)
    elif args.action == "import":
        if not args.input:
            raise ValueError("--input لازم است")
        result = save_production(args.project, read_json(args.input))
    elif args.action == "prompt":
        result = {"prompt": production_prompt(args.project), "response_schema": "schemas/production.schema.json"}
    elif args.action == "export":
        if not args.output_dir:
            raise ValueError("--output-dir لازم است")
        result = export_production(args.project, args.output_dir, png=args.png)
    else:
        result = read_json(Path(args.project) / "project.json")
    _write(result, args.output)


def cmd_calendar(args):
    events = read_json(args.events) if args.events else []
    rows = calendar_days(args.start, args.days, calendar=args.calendar, zone=args.timezone, time=args.time, events=events)
    if args.ics:
        write_ics(rows, args.ics)
    _write({"days": rows, "auto_publish": False}, args.output)


def cmd_subtitles(args):
    payload = read_json(args.input)
    pack = subtitle_pack(payload["cues"] if isinstance(payload, dict) else payload)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    for extension in ("srt", "vtt"):
        (out / f"subtitles.{extension}").write_text(pack[extension], encoding="utf-8")
    _write({"warnings": pack["warnings"], "directory": str(out)}, args.output)


def cmd_results(args):
    if args.action in {"record", "import-csv"} and not args.input:
        raise ValueError("--input لازم است")
    if args.action == "record":
        payload = read_json(args.input)
        row = bind_result(args.project, payload) if args.project else payload
        result = record_results(args.database, [row])
    elif args.action == "import-csv":
        result = import_csv(args.database, args.input)
    else:
        result = compare_results(read_results(args.database), metric=args.metric)
    _write(result, args.output)


def cmd_evaluate(args):
    if args.action == "prepare":
        if not args.output_dir:
            raise ValueError("--output-dir لازم است")
        result = prepare_evaluation(read_json(args.input), args.output_dir, seed=args.seed)
    else:
        if not args.ratings:
            raise ValueError("--ratings لازم است")
        result = score_evaluation(read_json(args.input), read_json(args.ratings))
    _write(result, args.output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ici")
    sub = parser.add_subparsers(required=True)

    doctor = sub.add_parser("doctor")
    doctor.add_argument("--output")
    doctor.set_defaults(func=cmd_doctor)

    trends = sub.add_parser("trends")
    trends.add_argument("input")
    trends.add_argument("--output")
    trends.set_defaults(func=cmd_trends)

    matrix = sub.add_parser("matrix")
    matrix.add_argument("input")
    matrix.add_argument("--output")
    matrix.set_defaults(func=cmd_matrix)

    insights = sub.add_parser("insights")
    insights.add_argument("kind", choices=("reel", "story", "account"))
    insights.add_argument("input")
    insights.add_argument("--duration", type=float)
    insights.add_argument("--output")
    insights.set_defaults(func=cmd_insights)

    story = sub.add_parser("story-plan")
    story.add_argument("--objective", required=True)
    story.add_argument("--audience-job", required=True)
    story.add_argument("--promise", required=True)
    story.add_argument("--frames", type=int, default=7)
    story.add_argument("--output")
    story.set_defaults(func=cmd_story_plan)

    reel = sub.add_parser("reel")
    reel.add_argument(
        "action",
        choices=(
            "toolchain", "probe", "manifest", "pipeline", "features",
            "prompt-pack", "audit", "compare", "align-retention", "hybrid-verify",
        ),
    )
    reel.add_argument("--media")
    reel.add_argument("--permission-basis", default="user_provided")
    reel.add_argument("--input")
    reel.add_argument("--output-dir", default="reel-analysis")
    reel.add_argument("--whisper-model", default="turbo")
    reel.add_argument("--language")
    reel.add_argument("--strict", action="store_true")
    reel.add_argument("--provider", default="gemini", choices=("gemini", "chatgpt", "claude", "other"))
    reel.add_argument("--mode", choices=("cloud-video-native", "cloud-evidence-pack", "local-measured", "hybrid-verified"))
    reel.add_argument("--manifest")
    reel.add_argument("--insights")
    reel.add_argument("--drop-threshold", type=float, default=0.08)
    reel.add_argument("--measured")
    reel.add_argument("--tolerance-seconds", type=float, default=0.75)
    reel.add_argument("--output")
    reel.set_defaults(func=cmd_reel)

    voice = sub.add_parser("voice")
    voice.add_argument("action", choices=("interview", "dna", "score", "blind-test", "evaluate", "rank", "drift"))
    voice.add_argument("--input", required=True)
    voice.add_argument("--dna")
    voice.add_argument("--text")
    voice.add_argument("--seed", type=int, default=0)
    voice.add_argument("--drift-threshold", type=float, default=0.2)
    voice.add_argument("--output")
    voice.set_defaults(func=cmd_voice)

    visual = sub.add_parser("visual")
    visual.add_argument("--headline", required=True)
    visual.add_argument("--body", required=True)
    visual.add_argument("--kicker")
    visual.add_argument("--background")
    visual.add_argument("--html", required=True)
    visual.add_argument("--png")
    visual.add_argument("--output")
    visual.add_argument("--surface", choices=("story", "reel", "carousel", "cover"), default="story")
    visual.set_defaults(func=cmd_visual)

    workflow = sub.add_parser("workflow", help="گردش‌کار فارسی از زمینه تا خروجی نسخه‌دار")
    workflow.add_argument("action", choices=("init", "compose", "import", "prompt", "export", "status"))
    workflow.add_argument("--project", required=True)
    workflow.add_argument("--input")
    workflow.add_argument("--output-dir")
    workflow.add_argument("--png", action="store_true")
    workflow.add_argument("--output")
    workflow.set_defaults(func=cmd_workflow)

    calendar = sub.add_parser("calendar", help="تقویم شمسی و خروجی ICS")
    calendar.add_argument("--start", required=True)
    calendar.add_argument("--days", type=int, default=7)
    calendar.add_argument("--calendar", choices=("jalali", "gregorian"), default="jalali")
    calendar.add_argument("--timezone", default="Asia/Tehran")
    calendar.add_argument("--time", default="18:00")
    calendar.add_argument("--events")
    calendar.add_argument("--ics")
    calendar.add_argument("--output")
    calendar.set_defaults(func=cmd_calendar)

    subtitles = sub.add_parser("subtitles", help="خروجی SRT و VTT فارسی")
    subtitles.add_argument("--input", required=True)
    subtitles.add_argument("--output-dir", required=True)
    subtitles.add_argument("--output")
    subtitles.set_defaults(func=cmd_subtitles)

    results = sub.add_parser("results", help="ثبت آمار و مقایسه انتشارهای همسان")
    results.add_argument("action", choices=("record", "import-csv", "compare"))
    results.add_argument("--database", required=True)
    results.add_argument("--project")
    results.add_argument("--input")
    results.add_argument("--metric", choices=("share_per_reach", "save_per_reach", "reply_per_reach"), default="share_per_reach")
    results.add_argument("--output")
    results.set_defaults(func=cmd_results)

    evaluate = sub.add_parser("evaluate", help="ارزیابی کور کیفیت محتوا")
    evaluate.add_argument("action", choices=("prepare", "score"))
    evaluate.add_argument("--input", required=True)
    evaluate.add_argument("--ratings")
    evaluate.add_argument("--output-dir")
    evaluate.add_argument("--seed", type=int, default=0)
    evaluate.add_argument("--output")
    evaluate.set_defaults(func=cmd_evaluate)
    return parser


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except (ValueError, KeyError, OSError, RuntimeError) as exc:
        parser.exit(2, f"خطا: {exc}\n")


if __name__ == "__main__":
    main()
