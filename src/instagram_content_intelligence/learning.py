"""Private publication ledger and explicitly observational matched comparisons."""
from __future__ import annotations

import csv
import hashlib
import json
import random
import sqlite3
import statistics
from datetime import datetime
from pathlib import Path

from .contracts import number, text_field
from .production import latest_production

METRICS = {"share_per_reach": "shares", "save_per_reach": "saved", "reply_per_reach": "replies"}
COUNTS = ("reach", "shares", "saved", "likes", "comments", "replies", "views")
STRATA = ("account", "surface", "objective", "window_hours", "traffic", "source_kind", "experiment_id")


def _instant(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("زمان باید offset یا Z داشته باشد")
    return result


def validate_result(payload: dict) -> dict:
    row = dict(payload)
    for key in ("account", "content_id", "revision", "media_id", "surface", "objective", "variant",
                "experiment_id", "traffic", "source_kind", "source_ref", "published_at", "observed_at"):
        row[key] = text_field(row, key)
    if row["surface"] not in {"reel", "story", "carousel"}:
        raise ValueError("Invalid surface")
    if row["traffic"] not in {"organic", "paid", "mixed"}:
        raise ValueError("traffic must be organic, paid or mixed")
    if row["source_kind"] not in {"meta_api", "instagram_dashboard", "manual_import"}:
        raise ValueError("Declare metric provenance")
    if row.get("reviewed") is not True or row.get("uncertain_fields"):
        raise ValueError("مقادیر نامطمئن باید بازبینی شوند؛ reviewed=true لازم است")
    row["window_hours"] = number(row.get("window_hours"), "window_hours", minimum=0.01)
    elapsed = (_instant(row["observed_at"]) - _instant(row["published_at"])).total_seconds() / 3600
    if abs(elapsed - row["window_hours"]) > 0.05:
        raise ValueError("بازه گزارش با زمان انتشار و مشاهده سازگار نیست (حداکثر اختلاف ۳ دقیقه)")
    for key in COUNTS:
        value = row.get(key)
        row[key] = None if value is None or value == "" else number(value, key)
        if row[key] is not None and not row[key].is_integer():
            raise ValueError(f"{key}: شمارش باید عدد صحیح باشد")
    row["schema_version"] = "1.0"
    return row


def bind_result(folder, payload: dict) -> dict:
    version = latest_production(folder, payload.get("revision"))
    bound = dict(payload)
    expected = {"account": version["brief"]["account"], "content_id": version["production"]["content_id"],
                "revision": version["revision"], "surface": version["production"]["surface"],
                "objective": version["brief"]["objective"]}
    for key, value in expected.items():
        if key in bound and bound[key] != value:
            raise ValueError(f"{key}: نتیجه با نسخه پروژه سازگار نیست")
        bound[key] = value
    return validate_result(bound)


def _connection(path):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)
    connection.execute("CREATE TABLE IF NOT EXISTS results (identity TEXT PRIMARY KEY, payload TEXT NOT NULL)")
    return connection


def record_results(database, rows: list[dict]) -> dict:
    validated = [validate_result(row) for row in rows]
    added, duplicates = 0, 0
    connection = _connection(database)
    try:
        with connection:
            for row in validated:
                # One snapshot per publication, observation window and source. Never count retries twice.
                identity = json.dumps([row[key] for key in ("account", "media_id", "window_hours", "source_kind")])
                key = hashlib.sha256(identity.encode()).hexdigest()
                serialized = json.dumps(row, ensure_ascii=False, sort_keys=True, allow_nan=False)
                previous = connection.execute("SELECT payload FROM results WHERE identity=?", (key,)).fetchone()
                if previous:
                    if previous[0] != serialized:
                        raise ValueError("این snapshot قبلاً با مقادیر متفاوت ثبت شده؛ اختلاف را حل کنید")
                    duplicates += 1
                else:
                    connection.execute("INSERT INTO results VALUES (?, ?)", (key, serialized))
                    added += 1
    finally:
        connection.close()
    return {"added": added, "duplicates": duplicates}


def import_csv(database, path) -> dict:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["reviewed"] = row.get("reviewed", "").lower() == "true"
        row["uncertain_fields"] = [x.strip() for x in row.get("uncertain_fields", "").split(";") if x.strip()]
    return record_results(database, rows)


def read_results(database) -> list[dict]:
    if not Path(database).exists():
        return []
    connection = _connection(database)
    try:
        return [json.loads(row[0]) for row in connection.execute("SELECT payload FROM results ORDER BY identity")]
    finally:
        connection.close()


def compare_results(rows: list[dict], *, metric="share_per_reach", min_per_variant=5, seed=0) -> dict:
    if metric not in METRICS or min_per_variant < 2:
        raise ValueError("Unsupported metric or sample threshold")
    groups, missing = {}, 0
    seen = set()
    for raw in rows:
        row = validate_result(raw)
        identity = tuple(row[key] for key in ("account", "media_id", "window_hours", "source_kind"))
        if identity in seen:
            raise ValueError("Duplicate snapshot in comparison")
        seen.add(identity)
        numerator, denominator = row[METRICS[metric]], row["reach"]
        if numerator is None or denominator is None or denominator == 0:
            missing += 1
            continue
        stratum = tuple(row[key] for key in STRATA)
        groups.setdefault(stratum, {}).setdefault(row["variant"], []).append(numerator / denominator)
    reports, rng = [], random.Random(seed)
    for stratum, variants in sorted(groups.items()):
        summary = {key: {"n": len(values), "median": statistics.median(values), "min": min(values), "max": max(values)}
                   for key, values in sorted(variants.items())}
        enough = len(variants) >= 2 and all(len(values) >= min_per_variant for values in variants.values())
        comparisons = []
        priors = {}
        if enough:
            medians = [item["median"] for item in summary.values()]
            for name, item in summary.items():
                below = sum(value < item["median"] for value in medians)
                tied = sum(value == item["median"] for value in medians)
                priors[name] = (below + 0.5 * tied) / len(medians)
            baseline = sorted(variants)[0]
            for name in sorted(variants)[1:]:
                left, right = variants[baseline], variants[name]
                deltas = sorted(statistics.median(rng.choices(right, k=len(right))) - statistics.median(rng.choices(left, k=len(left))) for _ in range(1000))
                comparisons.append({"baseline": baseline, "variant": name,
                                    "median_difference": summary[name]["median"] - summary[baseline]["median"],
                                    "bootstrap_95_interval": [deltas[24], deltas[974]]})
        reports.append({"stratum": dict(zip(STRATA, stratum)), "variants": summary,
                        "status": "observational_comparison" if enough else "insufficient_data",
                        "comparisons": comparisons,
                        "advisory_historical_priors": priors,
                        "prior_method": "within-stratum median percentile; ties use midrank; not a probability",
                        "next_step": "replicate_in_matched_experiment" if enough else "collect_more_comparable_publications"})
    return {"metric": metric, "groups": reports, "excluded_missing_or_zero_reach": missing,
            "seed": seed, "minimum_per_variant": min_per_variant,
            "warning": "Observational publication-level comparison; bootstrap intervals do not establish causality. No weights are changed automatically."}
