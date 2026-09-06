"""Blinded human evaluation: key is separate, missing ratings never become success."""
from __future__ import annotations

import hashlib
import json
import random
import statistics
from pathlib import Path

from .contracts import number, text_field, write_json

RUBRIC = {
    "naturalness": "فارسی طبیعی و متناسب با موقعیت: ۱ مصنوعی، ۳ قابل‌قبول، ۵ روان و طبیعی",
    "voice": "شباهت به نمونه‌های تأییدشده برند: ۱ نامرتبط، ۳ نسبی، ۵ مشخص و اصیل",
    "clarity": "وضوح وعده و پاسخ: ۱ مبهم، ۳ قابل‌فهم، ۵ روشن و منسجم",
    "execution": "قابلیت اجرا: ۱ غیرقابل‌اجرا، ۳ نیازمند اصلاح، ۵ آماده تولید",
    "evidence": "پشتوانه ادعا: ۱ بی‌پشتوانه، ۳ محدودیت روشن، ۵ ادعا و شاهد هم‌خوان",
}


def prepare_evaluation(candidates: list[dict], folder, *, seed=0) -> dict:
    if len(candidates) < 2:
        raise ValueError("حداقل دو نمونه لازم است")
    prepared, identities = [], set()
    for item in candidates:
        identity = text_field(item, "id")
        if identity in identities:
            raise ValueError("Duplicate candidate id")
        identities.add(identity)
        for key in ("text", "label", "context"):
            text_field(item, key)
        prepared.append(item)
    random.Random(seed).shuffle(prepared)
    fingerprint = hashlib.sha256(json.dumps(candidates, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]
    # Assignment changes with the seed, therefore it is part of the evaluation identity.
    evaluation_id = f"{fingerprint}-{seed}"
    pack = {"evaluation_id": evaluation_id, "rubric": RUBRIC,
            "items": [{"blind_id": f"item-{i}", "text": item["text"], "context": item["context"]} for i, item in enumerate(prepared, 1)],
            "instructions": "هر معیار را ۱ تا ۵ امتیاز بده و دلیل بنویس؛ کلید جداگانه را قبل از امتیازدهی نبین."}
    key = {"evaluation_id": evaluation_id, "mapping": {f"item-{i}": {"id": item["id"], "label": item["label"]} for i, item in enumerate(prepared, 1)}}
    out = Path(folder)
    out.mkdir(parents=True, exist_ok=True)
    if any((out / name).exists() for name in ("blind.json", "answer-key.json", "ratings-template.json")):
        raise FileExistsError("Evaluation folder already contains an evaluation")
    write_json(out / "blind.json", pack, overwrite=False)
    write_json(out / "answer-key.json", key, overwrite=False)
    template = {"evaluation_id": evaluation_id, "evaluator": "", "ratings": [
        {"blind_id": item["blind_id"], "scores": {criterion: None for criterion in RUBRIC}, "reason": ""} for item in pack["items"]]}
    write_json(out / "ratings-template.json", template, overwrite=False)
    return {"evaluation_id": evaluation_id, "blind_pack": str(out / "blind.json"), "key": str(out / "answer-key.json")}


def score_evaluation(pack: dict, ratings: dict) -> dict:
    if pack["evaluation_id"] != ratings.get("evaluation_id"):
        raise ValueError("Evaluation identity mismatch")
    text_field(ratings, "evaluator")
    expected = {item["blind_id"] for item in pack["items"]}
    seen, scores, incomplete = set(), [], []
    for row in ratings.get("ratings", []):
        identity = text_field(row, "blind_id")
        if identity not in expected or identity in seen:
            raise ValueError("Unknown or duplicate blind_id")
        seen.add(identity)
        values = row.get("scores", {})
        if not row.get("reason", "").strip() or any(values.get(key) is None for key in RUBRIC):
            incomplete.append(identity)
            continue
        checked = {key: number(values[key], key, minimum=1, maximum=5) for key in RUBRIC}
        if any(not value.is_integer() for value in checked.values()):
            raise ValueError("Ratings must be integers 1..5")
        scores.append({"blind_id": identity, "scores": checked, "mean": statistics.mean(checked.values()), "reason": row["reason"]})
    incomplete.extend(sorted(expected - seen))
    return {"evaluation_id": pack["evaluation_id"], "evaluator": ratings["evaluator"], "complete": not incomplete,
            "incomplete": incomplete, "results": scores,
            "acceptance": "owner_decision_required", "warning": "Human quality ratings do not measure Instagram performance."}
