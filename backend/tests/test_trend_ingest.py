from trendbaker.trend_engine.ingest import OUTPUT_COLUMNS, clean_item


def test_clean_item_casts_types_and_defaults_missing_counts():
    raw = {
        "id": "abc123",
        "published_at": "2026-07-20T12:00:00+00:00",
        "title": "Sourdough tips",
        "body": None,
        "views": 1000,
        "likes": None,
        "comments_count": 5,
    }

    record = clean_item(raw)

    assert set(record.keys()) == set(OUTPUT_COLUMNS)
    assert record["item_id"] == "abc123"
    assert record["body"] == ""
    assert record["views"] == 1000
    assert record["likes"] == 0
    assert record["comments"] == 5
    assert record["published_at"].tzinfo is not None


def test_clean_item_coerces_string_counts():
    raw = {
        "id": 1,
        "published_at": "2026-07-20T00:00:00Z",
        "title": "t",
        "body": "b",
        "views": "250",
        "likes": "10",
        "comments_count": "0",
    }

    record = clean_item(raw)

    assert record["item_id"] == "1"
    assert record["views"] == 250
    assert record["likes"] == 10
    assert record["comments"] == 0
