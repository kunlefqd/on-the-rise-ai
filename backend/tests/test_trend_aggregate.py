import numpy as np
import pandas as pd
import pytest

from trendbaker.trend_engine.aggregate import compute_daily_bins


def _item(item_id, day, views, likes):
    return {
        "item_id": item_id,
        "published_at": pd.Timestamp(day, tz="UTC"),
        "title": "t",
        "body": "b",
        "views": views,
        "likes": likes,
        "comments": 0,
    }


def _link(item_id, keyword):
    return {
        "item_id": item_id,
        "term_id": 1,
        "keyword": keyword,
        "label": keyword,
        "category": "flavour",
    }


def test_compute_daily_bins_groups_by_keyword_and_day():
    items = pd.DataFrame(
        [
            _item("1", "2026-07-20", views=100, likes=10),
            _item("2", "2026-07-20", views=400, likes=40),
            _item("3", "2026-07-21", views=50, likes=5),
        ]
    )
    links = pd.DataFrame(
        [
            _link("1", "brown-butter"),
            _link("2", "brown-butter"),
            _link("3", "brown-butter"),
        ]
    )

    bins = compute_daily_bins(items, links)

    assert list(bins["day"].dt.strftime("%Y-%m-%d")) == ["2026-07-20", "2026-07-21"]

    day1 = bins.iloc[0]
    assert day1["n"] == 2
    expected_attention = np.log1p(100) + np.log1p(400)
    assert day1["attention"] == pytest.approx(expected_attention)
    # engagement ratios are 10/100=0.1 and 40/400=0.1 -> median 0.1
    assert day1["engagement"] == pytest.approx(0.1)

    day2 = bins.iloc[1]
    assert day2["n"] == 1


def test_compute_daily_bins_handles_zero_views_without_error():
    items = pd.DataFrame([_item("1", "2026-07-20", views=0, likes=0)])
    links = pd.DataFrame([_link("1", "brown-butter")])

    bins = compute_daily_bins(items, links)

    assert len(bins) == 1
    assert bins.iloc[0]["engagement"] == 0.0


def test_compute_daily_bins_empty_input_returns_empty_frame():
    items = pd.DataFrame(
        columns=["item_id", "published_at", "title", "body", "views", "likes", "comments"]
    )
    links = pd.DataFrame(columns=["item_id", "term_id", "keyword", "label", "category"])

    bins = compute_daily_bins(items, links)

    assert bins.empty
