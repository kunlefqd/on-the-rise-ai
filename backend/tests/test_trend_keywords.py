from trendbaker.trend_engine.keywords import OUTPUT_COLUMNS, clean_link


def test_clean_link_flattens_embedded_term():
    raw = {
        "item_id": "abc123",
        "term_id": 7,
        "category": "flavour",
        "terms": {"slug": "brown-butter", "label": "Brown Butter"},
    }

    link = clean_link(raw)

    assert set(link.keys()) == set(OUTPUT_COLUMNS)
    assert link["item_id"] == "abc123"
    assert link["keyword"] == "brown-butter"
    assert link["label"] == "Brown Butter"
    assert link["category"] == "flavour"


def test_clean_link_handles_missing_term_embed():
    raw = {"item_id": "abc123", "term_id": 7, "category": "flavour", "terms": None}

    link = clean_link(raw)

    assert link["keyword"] == ""
    assert link["label"] == ""
