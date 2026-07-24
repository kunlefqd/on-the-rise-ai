"""YouTube Data API collector.

PLACEHOLDER — not yet implemented.

When implemented, this collector must:
  - Use the official YouTube Data API v3 only (via an API key from
    YOUTUBE_API_KEY). Do not scrape YouTube HTML or bypass API quotas.
  - Respect API quota and rate limits.
  - Produce items conforming to contracts/normalized-content.schema.json.

No real API calls are made yet.
"""

from __future__ import annotations

from typing import Any

from trendbaker.collectors.base import Collector
from trendbaker.config import settings


class YouTubeCollector(Collector):
    source_name = "youtube"

    def collect(self) -> list[dict[str, Any]]:
        settings.require("youtube_api_key")
        raise NotImplementedError("YouTube collection is not implemented yet.")
