"""End-to-end trend-scoring pipeline: Stage 1 -> Stage 5.

Wires the independent stages together into one ranked list of emerging
trends. Each stage stays swappable and independently testable -- this
module only sequences them.
"""

from __future__ import annotations

import pandas as pd

from trendbaker.trend_engine.aggregate import compute_daily_bins
from trendbaker.trend_engine.ingest import ingest_items
from trendbaker.trend_engine.keywords import fetch_keyword_links
from trendbaker.trend_engine.lifecycle import compute_lifecycle_states
from trendbaker.trend_engine.scoring import compute_trend_scores


def run_pipeline() -> pd.DataFrame:
    """Fetch fresh data from Supabase and return one ranked row per keyword:
    keyword, n, velocity_raw, engagement, trend_score, momentum,
    acceleration, attention_level, lifecycle_state.
    """
    items = ingest_items()
    keyword_links = fetch_keyword_links()
    daily_bins = compute_daily_bins(items, keyword_links)

    scores = compute_trend_scores(daily_bins)
    lifecycle = compute_lifecycle_states(daily_bins)

    ranked = scores.merge(lifecycle, on="keyword", how="left")
    return ranked.sort_values("trend_score", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    result = run_pipeline()
    print(f"Ranked {len(result)} trending keywords")
    print(result.head(20))
