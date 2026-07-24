"""Stage 3 -- per-keyword daily aggregates.

Bins each keyword's videos by publish day and computes, per (keyword, day)
bin:
    attention  = sum(log1p(views)) over videos published that day
    engagement = median(likes / views) over videos published that day
    n          = video count that day

Pure transformation -- takes the DataFrames Stages 1 and 2 already produced
and has no knowledge of Supabase, so it works the same whether the videos
came from the real `items` table or a synthetic test fixture.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

OUTPUT_COLUMNS = ["keyword", "day", "attention", "engagement", "n"]


def compute_daily_bins(items: pd.DataFrame, keyword_links: pd.DataFrame) -> pd.DataFrame:
    """Join items to their keywords and bin by publish day.

    `items` must have the Stage 1 output shape (item_id, published_at, views,
    likes, ...). `keyword_links` must have the Stage 2 output shape (item_id,
    keyword, ...).
    """
    merged = keyword_links.merge(items, on="item_id", how="inner")
    if merged.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    merged["day"] = merged["published_at"].dt.floor("D")
    merged["log_views"] = np.log1p(merged["views"])
    merged["engagement_ratio"] = merged["likes"] / merged["views"].replace(0, np.nan)

    bins = (
        merged.groupby(["keyword", "day"])
        .agg(
            attention=("log_views", "sum"),
            engagement=("engagement_ratio", "median"),
            n=("item_id", "count"),
        )
        .reset_index()
    )
    bins["engagement"] = bins["engagement"].fillna(0.0)
    return bins.sort_values(["keyword", "day"]).reset_index(drop=True)
