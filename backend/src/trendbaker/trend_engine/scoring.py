"""Stage 4 -- trend score.

    trend_score = 100 * (n / (n + SHRINKAGE_K)) * (0.7 * velocity_pct + 0.3 * engagement_pct)

- `n` is each keyword's total supporting video count, used as a Bayesian-
  style shrinkage factor so a keyword backed by only one or two videos
  can't outrank a well-supported one on a lucky spike.
- `velocity` is the smoothed log-ratio of a keyword's recent attention vs.
  its prior attention (VELOCITY_WINDOW_DAYS each), percentile-ranked across
  all keywords.
- `engagement` is each keyword's median per-bin engagement, percentile-
  ranked across all keywords.

Every keyword's single freshest day bin is dropped before any of the above
is computed: a video published "today" hasn't had time to accumulate views,
so leaving that bin in would read as a fake decline for every keyword, not
just the newest ones.

This is a placeholder formula per docs/trend-scoring.md -- the 0.7/0.3
weights, SHRINKAGE_K, and VELOCITY_WINDOW_DAYS are not finalized and are
easy to retune once real data shows how they behave.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np
import pandas as pd

SHRINKAGE_K = 5
VELOCITY_WINDOW_DAYS = 3
LOG_RATIO_EPSILON = 1.0  # pseudo-count added to attention sums before taking a log-ratio

OUTPUT_COLUMNS = ["keyword", "n", "velocity_raw", "engagement", "trend_score"]


class TrendScorer(ABC):
    """Base interface for computing a trend-summary score from raw signals.

    Kept for interface compatibility -- percentile normalization needs every
    keyword's data at once, so the real implementation is the batch function
    `compute_trend_scores` below rather than a per-entity `.score()` call.
    """

    @abstractmethod
    def score(self, entity: str, items: list[dict[str, Any]]) -> float:
        """Return a trend score for `entity` given its supporting items."""
        raise NotImplementedError


def drop_freshest_bin(bins: pd.DataFrame) -> pd.DataFrame:
    """Drop each keyword's single most recent day bin."""
    if bins.empty:
        return bins
    latest_day = bins.groupby("keyword")["day"].transform("max")
    return bins[bins["day"] < latest_day].copy()


def _velocity_raw(keyword_bins: pd.DataFrame) -> float:
    """Smoothed log-ratio of recent vs. prior attention for one keyword's bins."""
    keyword_bins = keyword_bins.sort_values("day")
    cutoff = keyword_bins["day"].max() - pd.Timedelta(days=VELOCITY_WINDOW_DAYS)
    prior_cutoff = cutoff - pd.Timedelta(days=VELOCITY_WINDOW_DAYS)

    recent = keyword_bins.loc[keyword_bins["day"] > cutoff, "attention"].sum()
    prior = keyword_bins.loc[
        (keyword_bins["day"] > prior_cutoff) & (keyword_bins["day"] <= cutoff), "attention"
    ].sum()
    return float(np.log((recent + LOG_RATIO_EPSILON) / (prior + LOG_RATIO_EPSILON)))


def compute_trend_scores(daily_bins: pd.DataFrame, k: int = SHRINKAGE_K) -> pd.DataFrame:
    """Stage 4 entry point.

    Takes Stage 3's per-(keyword, day) bins and returns one row per keyword:
    n, velocity_raw, engagement, trend_score -- ranked highest score first.
    """
    trimmed = drop_freshest_bin(daily_bins)
    if trimmed.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    per_keyword = trimmed.groupby("keyword").agg(
        n=("n", "sum"),
        engagement=("engagement", "median"),
    )
    per_keyword["velocity_raw"] = pd.Series(
        {keyword: _velocity_raw(group) for keyword, group in trimmed.groupby("keyword")}
    )

    velocity_pct = per_keyword["velocity_raw"].rank(pct=True)
    engagement_pct = per_keyword["engagement"].rank(pct=True)

    shrinkage = per_keyword["n"] / (per_keyword["n"] + k)
    weighted = 0.7 * velocity_pct + 0.3 * engagement_pct
    per_keyword["trend_score"] = 100 * shrinkage * weighted

    return (
        per_keyword.reset_index()[OUTPUT_COLUMNS]
        .sort_values("trend_score", ascending=False)
        .reset_index(drop=True)
    )
