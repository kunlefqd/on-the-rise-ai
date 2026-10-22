"""YouTube Data API v3 collector.

Fetches recent public baking videos via the official YouTube Data API v3
(``search.list`` -> ``videos.list``) and normalizes each into a
``trendbaker.models.Item`` (see docs/db-schema.md). No HTML scraping and no
quota workarounds, per docs/ethical-data-policy.md.

Tagging against the bakery taxonomy is a separate pass (it needs
``trendbaker.taxonomy``); this collector only fetches and normalizes. YouTube's
own video tags are preserved in ``Item.raw`` so the tagging pass can use them.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

from trendbaker.collectors.base import Collector
from trendbaker.config import settings
from trendbaker.models import Item

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

# search.list returns up to 50 results/page; videos.list accepts up to 50 ids/call.
_MAX_BATCH = 50

# Error `reason`s that will never succeed on retry within this run — fail fast
# (see docs/ethical-data-policy.md: do not hammer a source that has told us to
# stop). Quota only resets at midnight Pacific, so retrying it just burns time.
_FATAL_REASONS = frozenset(
    {
        "quotaExceeded",
        "dailyLimitExceeded",
        "accessNotConfigured",
        "keyInvalid",
        "badRequest",
    }
)
# Transient conditions worth retrying with exponential backoff.
_RETRY_REASONS = frozenset(
    {"rateLimitExceeded", "userRateLimitExceeded", "backendError", "internalError"}
)
_RETRY_STATUS = frozenset({429, 500, 502, 503, 504})
_MAX_ATTEMPTS = 5
_BACKOFF_BASE_SECONDS = 1.0
_TIMEOUT_SECONDS = 30.0


class YouTubeAPIError(RuntimeError):
    """Raised when the YouTube API returns an error we won't (or can't) retry."""


class YouTubeCollector(Collector):
    """Collects recent baking videos from the YouTube Data API v3."""

    source_name = "youtube"

    def __init__(
        self,
        queries: list[str],
        *,
        days: int = 30,
        max_per_query: int = 50,
        order: str = "relevance",
        region: str | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.queries = list(queries)
        self.days = days
        self.max_per_query = min(max_per_query, _MAX_BATCH)
        self.order = order
        self.region = region
        # An injected client is reused (and left open) — handy for tests; when
        # none is given, collect() owns a client for the duration of the run.
        self._client = client

    # ---------- public API ----------

    def collect(self) -> list[Item]:
        settings.require("youtube_api_key")
        owns_client = self._client is None
        client = self._client or httpx.Client(timeout=_TIMEOUT_SECONDS)
        try:
            video_ids = self._search_all(client)
            raw_videos = self._hydrate(client, video_ids)
        finally:
            if owns_client:
                client.close()
        return [self._normalize(v) for v in raw_videos]

    # ---------- steps ----------

    def _search_all(self, client: httpx.Client) -> list[str]:
        """Run one search per query; return deduped video IDs (insertion order)."""
        published_after = (
            datetime.now(UTC) - timedelta(days=self.days)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        seen: dict[str, None] = {}
        for query in self.queries:
            params: dict[str, Any] = {
                "key": settings.youtube_api_key,
                "part": "id",
                "type": "video",
                "q": query,
                "order": self.order,
                "maxResults": self.max_per_query,
                "publishedAfter": published_after,
            }
            if self.region:
                params["regionCode"] = self.region
            payload = self._request(client, SEARCH_URL, params)
            for item in payload.get("items", []):
                vid = item.get("id", {}).get("videoId")
                if vid:
                    seen.setdefault(vid, None)
        return list(seen)

    def _hydrate(self, client: httpx.Client, video_ids: list[str]) -> list[dict[str, Any]]:
        """Fetch full video records in batches of 50."""
        videos: list[dict[str, Any]] = []
        for start in range(0, len(video_ids), _MAX_BATCH):
            batch = video_ids[start : start + _MAX_BATCH]
            params: dict[str, Any] = {
                "key": settings.youtube_api_key,
                "part": "snippet,statistics",
                "id": ",".join(batch),
                "maxResults": _MAX_BATCH,
            }
            payload = self._request(client, VIDEOS_URL, params)
            videos.extend(payload.get("items", []))
        return videos

    def _normalize(self, video: dict[str, Any]) -> Item:
        """Map one raw videos.list entry to an Item (see docs/db-schema.md §6)."""
        vid = video["id"]
        snippet = video.get("snippet", {})
        stats = video.get("statistics", {})
        return Item(
            source=self.source_name,
            source_id=vid,
            url=f"https://www.youtube.com/watch?v={vid}",
            title=snippet.get("title"),
            body=snippet.get("description"),
            author=snippet.get("channelTitle"),
            published_at=snippet.get("publishedAt"),
            region=self.region,
            views=_to_int(stats.get("viewCount")),
            likes=_to_int(stats.get("likeCount")),
            comments_count=_to_int(stats.get("commentCount")),
            # Trimmed per docs/ethical-data-policy.md — keep only what the tagging
            # pass needs, not the entire API payload.
            raw={
                "tags": snippet.get("tags", []),
                "channel_id": snippet.get("channelId"),
                "category_id": snippet.get("categoryId"),
            },
        )

    # ---------- HTTP with quota-aware retry ----------

    def _request(
        self, client: httpx.Client, url: str, params: dict[str, Any]
    ) -> dict[str, Any]:
        delay = _BACKOFF_BASE_SECONDS
        last_error: YouTubeAPIError | None = None
        for attempt in range(_MAX_ATTEMPTS):
            response = client.get(url, params=params)
            if response.status_code == 200:
                return response.json()

            reason = _error_reason(response)
            retryable = response.status_code in _RETRY_STATUS or reason in _RETRY_REASONS
            if reason in _FATAL_REASONS or not retryable:
                raise YouTubeAPIError(
                    f"YouTube API {response.status_code} "
                    f"({reason or 'unknown'}) for {url} — not retrying."
                )
            last_error = YouTubeAPIError(
                f"YouTube API {response.status_code} ({reason or 'transient'})"
            )
            if attempt < _MAX_ATTEMPTS - 1:
                time.sleep(delay)
                delay *= 2
        raise YouTubeAPIError(
            f"YouTube API still failing after {_MAX_ATTEMPTS} attempts: {last_error}"
        )


def _to_int(value: Any) -> int:
    """API stat counts arrive as strings and may be absent (e.g. hidden likes)."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _error_reason(response: httpx.Response) -> str | None:
    """Pull the first error `reason` from a YouTube API error body, if present."""
    try:
        errors = response.json().get("error", {}).get("errors", [])
    except (ValueError, AttributeError):
        return None
    if errors:
        return errors[0].get("reason")
    return None
