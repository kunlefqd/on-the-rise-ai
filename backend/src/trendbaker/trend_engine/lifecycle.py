"""Stage 5 -- lifecycle state.

Runs a moving average over the same per-(keyword, day) attention series
Stage 4 uses, takes its first difference (momentum) and second difference
(acceleration), and classifies each keyword's current lifecycle stage:

    accelerating : momentum > 0 and acceleration > 0
    peaking      : momentum ~= 0 and acceleration < 0
    declining    : momentum < 0
    dormant      : flat (momentum ~= 0, acceleration ~= 0) and attention low

Momentum/acceleration "~= 0" and "low attention" have no team-agreed
thresholds yet -- MOMENTUM_EPSILON, ACCELERATION_EPSILON, and
DORMANT_ATTENTION_PERCENTILE below are tunable placeholders.

Bins operate on whatever days a keyword actually has data for -- gaps
(days with zero videos) are not reindexed as explicit zero-attention rows,
so the moving average advances by "bins observed" rather than strictly by
calendar day. Revisit once real data shows how sparse keywords' bins are.
"""

from __future__ import annotations

import pandas as pd

from trendbaker.trend_engine.scoring import drop_freshest_bin

MOVING_AVERAGE_WINDOW = 3
MOMENTUM_EPSILON = 0.1
ACCELERATION_EPSILON = 0.1
DORMANT_ATTENTION_PERCENTILE = 0.25

OUTPUT_COLUMNS = ["keyword", "momentum", "acceleration", "attention_level", "lifecycle_state"]


def _classify(momentum: float, acceleration: float, low_attention: bool) -> str:
    flat_momentum = abs(momentum) <= MOMENTUM_EPSILON
    flat_acceleration = abs(acceleration) <= ACCELERATION_EPSILON

    if flat_momentum and flat_acceleration and low_attention:
        return "dormant"
    if momentum > MOMENTUM_EPSILON and acceleration > 0:
        return "accelerating"
    if flat_momentum and acceleration < 0:
        return "peaking"
    if momentum < -MOMENTUM_EPSILON:
        return "declining"
    return "peaking"  # flat-but-not-dormant / transitional fallback


def _keyword_lifecycle(keyword_bins: pd.DataFrame) -> pd.Series:
    keyword_bins = keyword_bins.sort_values("day")
    smoothed = keyword_bins["attention"].rolling(MOVING_AVERAGE_WINDOW, min_periods=1).mean()
    momentum = smoothed.diff()
    acceleration = momentum.diff()

    return pd.Series(
        {
            "momentum": float(momentum.iloc[-1]) if len(momentum) else 0.0,
            "acceleration": float(acceleration.iloc[-1]) if len(acceleration) else 0.0,
            "attention_level": float(smoothed.iloc[-1]) if len(smoothed) else 0.0,
        }
    )


def compute_lifecycle_states(daily_bins: pd.DataFrame) -> pd.DataFrame:
    """Stage 5 entry point.

    Takes Stage 3's per-(keyword, day) bins and returns one row per keyword:
    momentum, acceleration, attention_level, lifecycle_state.
    """
    trimmed = drop_freshest_bin(daily_bins)
    if trimmed.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    per_keyword = pd.DataFrame(
        {keyword: _keyword_lifecycle(group) for keyword, group in trimmed.groupby("keyword")}
    ).T

    low_attention_cutoff = per_keyword["attention_level"].quantile(DORMANT_ATTENTION_PERCENTILE)
    per_keyword["lifecycle_state"] = [
        _classify(row.momentum, row.acceleration, row.attention_level <= low_attention_cutoff)
        for row in per_keyword.itertuples()
    ]

    return per_keyword.reset_index(names="keyword")[OUTPUT_COLUMNS]
