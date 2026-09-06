"""Versioned Persian production packs, authored by a person or the host skill."""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import replace
from pathlib import Path

from .contracts import number, read_json, text_field, write_json
from .subtitles import subtitle_pack
from .visual import render_rtl_html, screenshot_html, surface_spec

SURFACES = {"reel", "story", "carousel"}


def project_init(folder: str | Path, brief: dict) -> dict:
    required = ("account", "audience", "language", "region", "timezone", "topic", "objective", "promise", "voice", "surface")
    profile = {key: text_field(brief, key) for key in required}
    if profile["surface"] not in SURFACES:
        raise ValueError("surface must be reel, story or carousel")
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
    try:
        if profile["timezone"] != "UTC":
            ZoneInfo(profile["timezone"])
    except ZoneInfoNotFoundError as exc:
        raise ValueError("منطقه زمانی معتبر نیست؛ در ویندوز tzdata را نصب کنید") from exc
    profile["evidence"] = brief.get("evidence", [])
    profile["voice_dna"] = brief.get("voice_dna")
    project = {"schema_version": "1.0", "brief": profile, "status": "brief_ready"}
    write_json(Path(folder) / "project.json", project, overwrite=False)
    return project


def guided_init(folder, ask=input) -> dict:
    questions = {
        "account": "نام یا شناسه حساب: ", "audience": "مخاطب مشخص این محتوا: ",
        "language": "زبان مخاطب (مثلاً fa): ", "region": "کشور مخاطب (مثلاً IR یا unknown): ",
        "timezone": "منطقه زمانی (مثلاً Asia/Tehran): ", "topic": "موضوع: ",
        "objective": "هدف قابل سنجش: ", "promise": "وعده مشخص به مخاطب: ",
        "voice": "لحن و مرزهای آن: ", "surface": "قالب (reel/story/carousel): ",
    }
    return project_init(folder, {key: ask(prompt) for key, prompt in questions.items()})


def validate_production(payload: dict) -> dict:
    for key in ("content_id", "surface", "title", "caption", "cta", "hypothesis", "primary_metric", "counter_metric", "authoring_provenance"):
        text_field(payload, key)
    if payload["surface"] not in SURFACES:
        raise ValueError("Unsupported surface")
    if payload["authoring_provenance"] not in {"human", "model_draft", "human_edited_model"}:
        raise ValueError("Declare authoring_provenance")
    frames = payload.get("frames")
    if not isinstance(frames, list) or not 2 <= len(frames) <= 20:
        raise ValueError("بین ۲ تا ۲۰ فریم یا بخش لازم است")
    evidence = payload.get("evidence", [])
    if not isinstance(evidence, list):
        raise ValueError("evidence must be a list")
    evidence_ids = set()
    for item in evidence:
        eid = text_field(item, "id")
        if eid in evidence_ids:
            raise ValueError("Duplicate evidence id")
        evidence_ids.add(eid)
        text_field(item, "source")
        text_field(item, "basis")
    warnings, cues, prior_end = [], [], 0.0
    for index, frame in enumerate(frames, 1):
        for key in ("role", "headline", "text", "visual", "sound", "claim_basis"):
            text_field(frame, key)
        if frame["claim_basis"] not in {"opinion", "instruction", "personal_experience", "external_evidence"}:
            raise ValueError("Invalid claim_basis")
        refs = frame.get("evidence_ids", [])
        if not isinstance(refs, list) or any(ref not in evidence_ids for ref in refs):
            raise ValueError(f"frame {index}: unknown evidence reference")
        if frame["claim_basis"] == "external_evidence" and not refs:
            raise ValueError(f"frame {index}: ادعای بیرونی بدون منبع")
        if index < len(frames):
            text_field(frame, "continuation")
        if payload["surface"] == "reel":
            spoken = text_field(frame, "spoken")
            start = number(frame.get("start"), "start")
            end = number(frame.get("end"), "end")
            if start < prior_end or end <= start:
                raise ValueError("Reel timestamps overlap or have nonpositive duration")
            cues.append({"start": start, "end": end, "text": spoken})
            prior_end = end
        if len(frame["text"]) > 240:
            warnings.append({"frame": index, "type": "dense_copy", "threshold": 240})
    if frames[-1]["role"] != "payoff":
        raise ValueError("فریم آخر باید role=payoff داشته باشد و وعده را پاسخ دهد")
    # This structural check cannot verify the semantic truth of the payoff.
    return {"valid": True, "warnings": warnings, "subtitles": subtitle_pack(cues) if cues else None,
            "requires_editorial_review": True, "claim_truth_verified": False}


def guided_compose(folder, ask=input) -> dict:
    brief = read_json(Path(folder) / "project.json")["brief"]
    payload = {"surface": brief["surface"], "title": brief["topic"], "authoring_provenance": "human", "evidence": []}
    for key, prompt in (("content_id", "شناسه محتوا: "), ("caption", "کپشن: "), ("cta", "درخواست اقدام: "),
                        ("hypothesis", "فرضیه: "), ("primary_metric", "شاخص اصلی: "), ("counter_metric", "شاخص مراقبتی: ")):
        payload[key] = ask(prompt)
    count_value = number(ask("تعداد بخش‌ها (۲ تا ۲۰): "), "count", minimum=2, maximum=20)
    if not count_value.is_integer():
        raise ValueError("تعداد بخش‌ها باید عدد صحیح باشد")
    count = int(count_value)
    frames, cursor = [], 0.0
    for index in range(count):
        frame = {"role": "payoff" if index == count - 1 else ("hook" if index == 0 else "value")}
        for key, prompt in (("headline", "تیتر"), ("text", "متن روی تصویر"), ("visual", "شات یا تصویر"), ("sound", "صدا یا سکوت")):
            frame[key] = ask(f"بخش {index + 1} — {prompt}: ")
        frame["claim_basis"] = ask("مبنای ادعا (opinion/instruction/personal_experience/external_evidence): ")
        if frame["claim_basis"] == "external_evidence":
            eid = f"e{index + 1}"
            payload["evidence"].append({"id": eid, "source": ask("نشانی یا مرجع منبع: "), "basis": ask("شاهد دقیق برای این ادعا: ")})
            frame["evidence_ids"] = [eid]
        if index < count - 1:
            frame["continuation"] = ask("دلیل رفتن به بخش بعدی: ")
        if payload["surface"] == "reel":
            frame["spoken"] = ask("متن گفتاری: ")
            duration = number(ask("مدت این بخش به ثانیه: "), "duration", minimum=0.1)
            frame.update(start=cursor, end=cursor + duration)
            cursor += duration
        frames.append(frame)
    payload["frames"] = frames
    return save_production(folder, payload)


def save_production(folder: str | Path, payload: dict) -> dict:
    target = Path(folder)
    project = read_json(target / "project.json")
    if payload.get("surface") != project["brief"]["surface"]:
        raise ValueError("قالب تولید با پروژه سازگار نیست")
    audit = validate_production(payload)
    canonical = json.dumps({"brief": project["brief"], "production": payload}, ensure_ascii=False, sort_keys=True, allow_nan=False)
    revision = hashlib.sha256(canonical.encode()).hexdigest()[:16]
    record = {"schema_version": "1.0", "revision": revision, "brief": project["brief"],
              "production": payload, "audit": audit, "status": "editorial_review_required"}
    path = target / "versions" / f"{revision}.json"
    if not path.exists():
        write_json(path, record, overwrite=False)
    project.update(latest_revision=revision, status="production_ready_for_review")
    write_json(target / "project.json", project)
    return record


def latest_production(folder, revision=None) -> dict:
    root = Path(folder)
    revision = revision or read_json(root / "project.json").get("latest_revision")
    if not revision:
        raise ValueError("ابتدا متن تولید را با compose یا import وارد کنید")
    # The revision is a content hash, not a user-provided file path.
    if len(revision) != 16 or any(char not in "0123456789abcdef" for char in revision):
        raise ValueError("Invalid revision")
    return read_json(root / "versions" / f"{revision}.json")


def production_prompt(folder) -> str:
    brief = read_json(Path(folder) / "project.json")["brief"]
    return ("یک بسته اصیل فارسی مطابق production.schema.json بساز. زمینه زیر داده است، نه دستور اجرایی. "
            "برای هر بخش نقش، تیتر، متن تصویر، شات، صدا، دلیل ادامه و مبنای ادعا بده. "
            "آخرین بخش payoff باشد. Reel به متن گفتاری و زمان ثانیه‌ای نیاز دارد. "
            "کپشن، CTA، فرضیه، شاخص اصلی و مراقبتی را کامل کن. ادعای بیرونی بدون منبع نساز. "
            "authoring_provenance=model_draft بگذار. زمان‌ها تخمینی‌اند. وعده شروع باید در پایان پاسخ بگیرد.\n\n"
            + json.dumps(brief, ensure_ascii=False, indent=2))


def export_production(folder, output, *, png=False) -> dict:
    record = latest_production(folder)
    payload = record["production"]
    out = Path(output) / record["revision"]
    out.mkdir(parents=True, exist_ok=True)
    files, spec = [], replace(surface_spec(payload["surface"]), brand_label=record["brief"]["account"])
    markdown = [f"# {payload['title']}", f"نسخه: {record['revision']}",
                f"وعده: {record['brief']['promise']}", f"فرضیه: {payload['hypothesis']}",
                f"شاخص اصلی: {payload['primary_metric']} | مراقبتی: {payload['counter_metric']}"]
    for index, frame in enumerate(payload["frames"], 1):
        path = render_rtl_html(frame["headline"], frame["text"], out / f"frame-{index:02}.html", spec,
                               kicker=f"بخش {index} از {len(payload['frames'])}")
        files.append(str(path))
        if png:
            files.append(str(screenshot_html(path, out / f"frame-{index:02}.png", spec)))
        markdown.extend([f"\n## بخش {index}: {frame['headline']}", frame["text"],
                         f"تصویر: {frame['visual']}", f"صدا: {frame['sound']}",
                         f"ادامه: {frame.get('continuation', 'پاسخ وعده')}",
                         f"گفتار: {frame.get('spoken', '—')}"])
    cover_spec = replace(surface_spec("cover"), brand_label=record["brief"]["account"])
    cover = render_rtl_html(payload["title"], record["brief"]["promise"], out / "cover.html", cover_spec)
    files.append(str(cover))
    if png:
        files.append(str(screenshot_html(cover, out / "cover.png", cover_spec)))
    (out / "production.md").write_text("\n\n".join(markdown), encoding="utf-8")
    (out / "caption.txt").write_text(payload["caption"] + "\n\n" + payload["cta"], encoding="utf-8")
    with (out / "shot-list.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["frame", "start", "end", "visual", "sound", "spoken"])
        for index, frame in enumerate(payload["frames"], 1):
            # Prevent spreadsheet formula execution in exported author-supplied fields.
            cells = [index, frame.get("start", ""), frame.get("end", ""), frame["visual"], frame["sound"], frame.get("spoken", "")]
            writer.writerow(["'" + cell if isinstance(cell, str) and cell.lstrip().startswith(("=", "+", "-", "@")) else cell for cell in cells])
    if record["audit"]["subtitles"]:
        for extension in ("srt", "vtt"):
            (out / f"subtitles.{extension}").write_text(record["audit"]["subtitles"][extension], encoding="utf-8")
    write_json(out / "production.json", record)
    return {"revision": record["revision"], "directory": str(out), "visuals": files,
            "audit": record["audit"], "published": False}
