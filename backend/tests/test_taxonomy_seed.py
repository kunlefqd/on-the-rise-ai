from trendbaker import taxonomy as youtube_taxonomy
from trendbaker.trend_engine.taxonomy_seed import (
    PROPOSED_TERMS,
    build_term_rows,
    seed_taxonomy,
    slugify,
)


def test_slugify_lowercases_and_joins_words_with_underscore():
    assert slugify("Brown Butter") == "brown_butter"
    assert slugify("High Protein") == "high_protein"
    assert slugify("Gluten Free") == "gluten_free"


def test_slugify_already_single_word():
    assert slugify("pizza") == "pizza"
    assert slugify("Croissant") == "croissant"


def test_slugify_strips_stray_punctuation():
    assert slugify("  Cinnamon Roll! ") == "cinnamon_roll"


def test_build_term_rows_has_no_duplicate_slugs():
    rows = build_term_rows()
    slugs = [row.slug for row in rows]
    assert len(slugs) == len(set(slugs))
    assert len(rows) == len(PROPOSED_TERMS)


def test_build_term_rows_uses_only_existing_categories():
    allowed = {"format", "flavour", "ingredient", "dietary"}
    for row in build_term_rows():
        assert set(row.categories) <= allowed
        assert row.categories, f"{row.slug} has no categories"


def test_multi_category_terms_preserve_array_design():
    rows = {row.slug: row for row in build_term_rows()}

    assert rows["chocolate"].categories == ["flavour", "ingredient"]
    assert rows["brown_butter"].categories == ["flavour", "ingredient"]
    # black_sesame is single-category (["flavour"]) — reconciled to match
    # trendbaker.taxonomy.FLAVOURS rather than left conflicting; see
    # test_reconciled_terms_match_trendbaker_taxonomy below.
    # Single-category terms remain single-element arrays, not bare strings.
    assert rows["pizza"].categories == ["format"]


def test_reconciled_terms_match_trendbaker_taxonomy():
    # For every proposed term that also appears in trendbaker.taxonomy
    # (Kunle's independently-built YouTube seed taxonomy), the category set
    # here must match exactly — otherwise whichever of seed_taxonomy() /
    # trendbaker.cli's load_to_supabase() runs last would silently overwrite
    # the other's categorization for that slug. Terms absent from
    # trendbaker.taxonomy entirely (net new) are exempt.
    youtube_categories: dict[str, set[str]] = {}
    for category, terms in youtube_taxonomy.SEED_CATEGORIES.items():
        for term in terms:
            youtube_categories.setdefault(term, set()).add(category)

    for term in PROPOSED_TERMS:
        label = term["label"]
        if label not in youtube_categories:
            continue  # net new to this list, nothing to reconcile against
        assert set(term["categories"]) == youtube_categories[label], (
            f"{label!r} categories {term['categories']} conflict with "
            f"trendbaker.taxonomy's {sorted(youtube_categories[label])}"
        )


class _FakeRepoForTaxonomy:
    """Fake SupabaseRepository for seed_taxonomy, no network."""

    def __init__(self):
        self.upsert_calls: list[list] = []

    def upsert_terms(self, terms):
        self.upsert_calls.append(terms)
        return terms


def test_seed_taxonomy_upserts_all_proposed_terms():
    repo = _FakeRepoForTaxonomy()
    count = seed_taxonomy(repo)

    assert count == len(PROPOSED_TERMS)
    [terms] = repo.upsert_calls
    assert {term.slug for term in terms} == {slugify(t["label"]) for t in PROPOSED_TERMS}


def test_seed_taxonomy_is_deterministic_across_calls():
    # Calling twice must build the exact same payload each time — combined
    # with upsert-on-slug at the database level, this is what makes seeding
    # idempotent (same end state, no duplicate rows, nothing deleted).
    repo = _FakeRepoForTaxonomy()
    seed_taxonomy(repo)
    seed_taxonomy(repo)

    first, second = repo.upsert_calls
    assert first == second
