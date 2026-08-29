from __future__ import annotations

import statistics
from typing import Any, Iterable

from .provenance import MetricValue, Provenance, ProvenanceKind


def safe_rate(numerator: float | int | None, denominator: float | int | None) -> float | None:
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return float(numerator) / float(denominator)


def _derived(name: str, value: float | None, numerator: str, denominator: str) -> MetricValue:
    return MetricValue(
        name=name,
        value=value,
        numerator=numerator,
        denominator=denominator,
        provenance=Provenance.now(
            ProvenanceKind.DERIVED,
            "instagram-content-intelligence",
            scope="single_media",
            notes="Derived from supplied source metrics; not a native Instagram metric.",
        ),
        unavailable_reason=None if value is not None else "missing_or_zero_denominator",
    )


def analyze_reel(metrics: dict[str, Any], duration_seconds: float | None = None) -> dict[str, Any]:
    """Compute auditable Reel ratios while preserving API/dashboard boundaries."""

    reach = metrics.get("reach")
    views = metrics.get("views")
    shares = metrics.get("shares")
    saves = metrics.get("saved", metrics.get("saves"))
    likes = metrics.get("likes")
    comments = metrics.get("comments")
    watch_time_ms = metrics.get("ig_reels_video_view_total_time")
    average_watch_time_ms = metrics.get("ig_reels_avg_watch_time")
    if average_watch_time_ms is None and watch_time_ms is not None and views:
        average_watch_time_ms = watch_time_ms / views

    interaction_total = sum(value or 0 for value in (shares, saves, likes, comments))
    output: dict[str, Any] = {
        "ratios": {
            item.name: item.to_dict()
            for item in (
                _derived("share_per_reach", safe_rate(shares, reach), "shares", "reach"),
                _derived("save_per_reach", safe_rate(saves, reach), "saved", "reach"),
                _derived("interaction_per_reach", safe_rate(interaction_total, reach), "interaction_sum", "reach"),
                _derived("view_per_reach", safe_rate(views, reach), "views", "reach"),
            )
        },
        "watch": {
            "average_watch_time_ms": average_watch_time_ms,
            "average_watch_fraction": (
                safe_rate(average_watch_time_ms / 1000, duration_seconds)
                if average_watch_time_ms is not None and duration_seconds
                else None
            ),
            "warning": "Average watch fraction is a descriptive proxy, not a completion-rate metric.",
        },
        "native": {
            "reels_skip_rate": metrics.get("reels_skip_rate"),
            "reach": reach,
            "views": views,
            "shares": shares,
            "saved": saves,
        },
        "scope_warnings": [],
    }

    provenance = metrics.get("_provenance", {})
    for field in ("follows", "profile_visits", "profile_activity", "non_follower_reach"):
        if field not in metrics:
            continue
        field_source = provenance.get(field, {}).get("kind")
        if field in {"follows", "profile_visits", "profile_activity"} and field_source == "meta_api":
            output["scope_warnings"].append(
                f"{field} is not documented for Reel media in the current Meta media-insights reference; verify provenance."
            )
        if field == "non_follower_reach" and provenance.get(field, {}).get("scope") != "single_media":
            output["scope_warnings"].append(
                "Account-level follower/non-follower breakdown cannot be attributed to this Reel."
            )
        output.setdefault("attribution", {})[field] = {
            "value": metrics[field],
            "provenance": provenance.get(field),
        }
    return output


def _median_absolute_deviation(values: list[float]) -> float:
    if not values:
        return 0.0
    median = statistics.median(values)
    return statistics.median(abs(value - median) for value in values)


def analyze_story_sequence(frames: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Analyze frame-by-frame Story loss and navigation using reach as the cohort proxy."""

    rows = [dict(frame) for frame in frames]
    if not rows:
        return {"frames": [], "sequence": {}, "alerts": []}
    drops: list[float] = []
    for index, row in enumerate(rows):
        reach = row.get("reach")
        previous_reach = rows[index - 1].get("reach") if index else None
        drop = safe_rate((previous_reach - reach) if previous_reach is not None and reach is not None else None, previous_reach)
        if drop is not None:
            drops.append(drop)
        navigation = row.get("navigation", {}) or {}
        row["derived"] = {
            "drop_from_previous": drop,
            "exit_per_reach": safe_rate(navigation.get("TAP_EXIT"), reach),
            "forward_per_reach": safe_rate(navigation.get("TAP_FORWARD"), reach),
            "next_story_per_reach": safe_rate(navigation.get("SWIPE_FORWARD"), reach),
            "back_per_reach": safe_rate(navigation.get("TAP_BACK"), reach),
            "reply_per_reach": safe_rate(row.get("replies"), reach),
            "share_per_reach": safe_rate(row.get("shares"), reach),
        }

    median_drop = statistics.median(drops) if drops else None
    mad = _median_absolute_deviation(drops)
    alerts = []
    for index, row in enumerate(rows):
        drop = row["derived"]["drop_from_previous"]
        if drop is None or median_drop is None:
            continue
        robust_threshold = median_drop + max(2.5 * mad, 0.05)
        if drop > robust_threshold:
            alerts.append(
                {
                    "frame": row.get("frame", index + 1),
                    "type": "abnormal_drop",
                    "drop": drop,
                    "threshold": robust_threshold,
                    "diagnostic": "Inspect promise continuity, information density, interaction friction, and visual change. This is a flag, not a causal claim.",
                }
            )
    first_reach = rows[0].get("reach")
    last_reach = rows[-1].get("reach")
    return {
        "frames": rows,
        "sequence": {
            "frame_count": len(rows),
            "reach_completion_proxy": safe_rate(last_reach, first_reach),
            "median_frame_drop": median_drop,
            "drop_mad": mad,
            "warning": "Story reach is not a stable user-level cohort identifier; treat completion as a proxy.",
        },
        "alerts": alerts,
    }


def analyze_account_distribution(metrics: dict[str, Any]) -> dict[str, Any]:
    followers = metrics.get("followers")
    non_followers = metrics.get("non_followers")
    total = (followers or 0) + (non_followers or 0)
    return {
        "scope": metrics.get("scope", "account_interval"),
        "follower_share": safe_rate(followers, total),
        "non_follower_share": safe_rate(non_followers, total),
        "warning": "Account-interval distribution must not be assigned to an individual media item.",
    }

