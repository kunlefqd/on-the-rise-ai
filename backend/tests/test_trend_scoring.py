import pandas as pd

from trendbaker.trend_engine.scoring import compute_trend_scores, drop_freshest_bin

DAYS = pd.date_range("2026-07-10", periods=7, freq="D", tz="UTC")  # day0 .. day6


def _bins(keyword, attentions, n=1, engagement=0.5):
    return pd.DataFrame(
        {
            "keyword": keyword,
            "day": DAYS,
            "attention": attentions,
            "engagement": engagement,
            "n": n,
        }
    )


def test_drop_freshest_bin_removes_only_the_latest_day_per_keyword():
    bins = pd.concat(
        [_bins("a", [1] * 7), _bins("b", [2] * 7)],
        ignore_index=True,
    )

    trimmed = drop_freshest_bin(bins)

    assert trimmed.groupby("keyword")["day"].max().eq(DAYS[5]).all()
    assert len(trimmed) == 12  # 6 remaining days each, for 2 keywords


def test_rising_keyword_scores_higher_than_flat_keyword():
    rising = _bins("rising", [1, 1, 1, 5, 5, 5, 999])  # last bin (freshest) is a spike, dropped
    flat = _bins("flat", [3, 3, 3, 3, 3, 3, 3])
    bins = pd.concat([rising, flat], ignore_index=True)

    scores = compute_trend_scores(bins).set_index("keyword")

    assert scores.loc["rising", "trend_score"] > scores.loc["flat", "trend_score"]


def test_freshest_bin_spike_does_not_affect_score():
    # Only difference between the two keywords is the freshest (dropped) bin.
    steady = _bins("steady", [3, 3, 3, 3, 3, 3, 3])
    steady_with_spike = _bins("steady_spike", [3, 3, 3, 3, 3, 3, 999])
    bins = pd.concat([steady, steady_with_spike], ignore_index=True)

    scores = compute_trend_scores(bins).set_index("keyword")

    assert scores.loc["steady", "trend_score"] == scores.loc["steady_spike", "trend_score"]


def test_more_supporting_videos_scores_higher_all_else_equal():
    few = _bins("few", [1, 1, 1, 5, 5, 5, 5], n=1)
    many = _bins("many", [1, 1, 1, 5, 5, 5, 5], n=20)
    bins = pd.concat([few, many], ignore_index=True)

    scores = compute_trend_scores(bins).set_index("keyword")

    assert scores.loc["many", "trend_score"] > scores.loc["few", "trend_score"]


def test_empty_bins_returns_empty_frame():
    empty = pd.DataFrame(columns=["keyword", "day", "attention", "engagement", "n"])

    scores = compute_trend_scores(empty)

    assert scores.empty
