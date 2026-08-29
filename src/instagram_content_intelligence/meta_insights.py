from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from .provenance import Provenance, ProvenanceKind


REEL_MEDIA_METRICS = {
    "comments",
    "crossposted_views",
    "facebook_views",
    "ig_reels_avg_watch_time",
    "ig_reels_video_view_total_time",
    "likes",
    "reach",
    "reels_skip_rate",
    "reposts",
    "saved",
    "shares",
    "total_comments",
    "total_interactions",
    "total_likes",
    "total_views",
    "views",
}

STORY_MEDIA_METRICS = {
    "facebook_views",
    "follows",
    "impressions",
    "link_clicks",
    "navigation",
    "profile_activity",
    "profile_visits",
    "reach",
    "replies",
    "reposts",
    "shares",
    "total_interactions",
    "views",
}


@dataclass(frozen=True)
class MetaClientConfig:
    access_token: str
    api_version: str = "v26.0"
    host: str = "https://graph.instagram.com"
    timeout_seconds: int = 30

    def __post_init__(self) -> None:
        hostname = urllib.parse.urlsplit(self.host).hostname
        if hostname not in {"graph.instagram.com", "graph.facebook.com"}:
            raise ValueError("Meta Graph host must be graph.instagram.com or graph.facebook.com")

    @classmethod
    def from_environment(cls) -> "MetaClientConfig":
        token = os.getenv("META_ACCESS_TOKEN")
        if not token:
            raise RuntimeError("META_ACCESS_TOKEN is required")
        return cls(
            token,
            os.getenv("META_API_VERSION", "v26.0"),
            "https://graph.instagram.com",
        )


class MetaInsightsError(RuntimeError):
    def __init__(self, message: str, *, status: int | None = None, payload: Any = None):
        super().__init__(message)
        self.status = status
        self.payload = payload


class MetaInsightsClient:
    def __init__(
        self,
        config: MetaClientConfig,
        transport: Callable[[str, int], dict[str, Any]] | None = None,
    ) -> None:
        self.config = config
        self.transport = transport or self._http_get

    def media_insights(self, media_id: str, metrics: list[str], media_type: str) -> dict[str, Any]:
        allowed = REEL_MEDIA_METRICS if media_type.upper() == "REELS" else STORY_MEDIA_METRICS if media_type.upper() == "STORY" else None
        if allowed is not None:
            unsupported = sorted(set(metrics) - allowed)
            if unsupported:
                raise ValueError(f"Metrics not documented for {media_type}: {', '.join(unsupported)}")
        payload = self._get(f"{media_id}/insights", {"metric": ",".join(metrics)})
        return self._normalize(payload, scope="single_media", route="media_insights")

    def account_insights(
        self,
        instagram_user_id: str,
        metrics: list[str],
        *,
        period: str = "day",
        since: str | None = None,
        until: str | None = None,
        metric_type: str | None = None,
        breakdown: str | None = None,
    ) -> dict[str, Any]:
        params = {"metric": ",".join(metrics), "period": period}
        for name, value in (("since", since), ("until", until), ("metric_type", metric_type), ("breakdown", breakdown)):
            if value is not None:
                params[name] = value
        payload = self._get(f"{instagram_user_id}/insights", params)
        return self._normalize(payload, scope="account_interval", route="account_insights")

    def _get(self, route: str, params: dict[str, Any]) -> dict[str, Any]:
        base = self.config.host.rstrip("/")
        version = self.config.api_version.strip("/")
        query = dict(params, access_token=self.config.access_token)
        url = f"{base}/{version}/{route.lstrip('/')}?{urllib.parse.urlencode(query)}"
        return self.transport(url, self.config.timeout_seconds)

    def _http_get(self, url: str, timeout: int) -> dict[str, Any]:
        request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "instagram-content-intelligence/0.1"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                payload = body
            raise MetaInsightsError("Meta Insights request failed", status=exc.code, payload=payload) from exc

    def _normalize(self, payload: dict[str, Any], *, scope: str, route: str) -> dict[str, Any]:
        collected = datetime.now(timezone.utc).isoformat()
        metrics = []
        for item in payload.get("data", []):
            provenance = Provenance(
                ProvenanceKind.META_API,
                route,
                collected,
                api_version=self.config.api_version,
                scope=scope,
                estimated=item.get("name") in {"reach", "views", "reels_skip_rate"},
                in_development=item.get("name") in {"views", "reels_skip_rate", "total_interactions", "ig_reels_video_view_total_time"},
            )
            metrics.append({"name": item.get("name"), "period": item.get("period"), "title": item.get("title"), "description": item.get("description"), "values": item.get("values"), "total_value": item.get("total_value"), "provenance": provenance.to_dict()})
        return {"metrics": metrics, "paging": payload.get("paging"), "raw_errors": payload.get("error")}


def redact_meta_url(url: str) -> str:
    """Safe helper for logs and tests."""

    parsed = urllib.parse.urlsplit(url)
    pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    redacted = [(key, "[REDACTED]" if key == "access_token" else value) for key, value in pairs]
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urllib.parse.urlencode(redacted), parsed.fragment))
