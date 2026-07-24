import pandas as pd

from trendbaker.trend_engine.lifecycle import (
    ACCELERATION_EPSILON,
    MOMENTUM_EPSILON,
    _classify,
    compute_lifecycle_states,
)

DAYS = pd.date_range("2026-07-10", periods=7, freq="D", tz="UTC")


def _bins(keyword, attentions):
    return pd.DataFrame(
        {"keyword": keyword, "day": DAYS, "attention": attentions, "engagement": 0.5, "n": 1}
    )


def test_classify_accelerating():
    assert _classify(momentum=1.0, acceleration=1.0, low_attention=False) == "accelerating"


def test_classify_peaking():
    assert _classify(momentum=0.0, acceleration=-1.0, low_attention=False) == "peaking"


def test_classify_declining():
    assert _classify(momentum=-1.0, acceleration=0.0, low_attention=False) == "declining"


def test_classify_dormant_requires_flat_and_low():
    assert _classify(momentum=0.0, acceleration=0.0, low_attention=True) == "dormant"
    # flat but not low attention should not be classified dormant
    assert _classify(momentum=0.0, acceleration=0.0, low_attention=False) != "dormant"


def test_classify_epsilon_boundaries_are_inclusive():
    assert _classify(MOMENTUM_EPSILON, -ACCELERATION_EPSILON - 0.01, False) == "peaking"


def test_compute_lifecycle_states_detects_accelerating_series():
    # freshest bin (day6) is a spike that gets dropped; growth happens across day0..day5
    bins = _bins("rising", [1, 1, 2, 4, 7, 11, 999])

    states = compute_lifecycle_states(bins).set_index("keyword")

    assert states.loc["rising", "momentum"] > 0
    assert states.loc["rising", "lifecycle_state"] == "accelerating"


def test_compute_lifecycle_states_detects_declining_series():
    bins = _bins("fading", [11, 7, 4, 2, 1, 1, 999])

    states = compute_lifecycle_states(bins).set_index("keyword")

    assert states.loc["fading", "momentum"] < 0
    assert states.loc["fading", "lifecycle_state"] == "declining"


def test_compute_lifecycle_states_ignores_freshest_bin_spike():
    steady = _bins("steady", [3, 3, 3, 3, 3, 3, 3])
    steady_with_spike = _bins("steady_spike", [3, 3, 3, 3, 3, 3, 999])
    bins = pd.concat([steady, steady_with_spike], ignore_index=True)

    states = compute_lifecycle_states(bins).set_index("keyword")

    assert states.loc["steady", "momentum"] == states.loc["steady_spike", "momentum"]


def test_empty_bins_returns_empty_frame():
    empty = pd.DataFrame(columns=["keyword", "day", "attention", "engagement", "n"])

    states = compute_lifecycle_states(empty)

    assert states.empty
