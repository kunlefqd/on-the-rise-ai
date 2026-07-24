from trendbaker.models import Term
from trendbaker.trend_engine.term_tagging import match_terms, tag_blog_items

ITEM_1 = "11111111-1111-1111-1111-111111111111"
ITEM_2 = "22222222-2222-2222-2222-222222222222"

TERMS = [
    Term(id=8, slug="pistachio", label="pistachio", categories=["flavour"]),
    Term(id=4, slug="cookie", label="cookie", categories=["format"]),
    Term(
        id=9,
        slug="dubai_chocolate",
        label="dubai chocolate",
        categories=["format", "flavour"],
    ),
]


def test_match_terms_is_case_insensitive():
    matches = match_terms("PISTACHIO croissants are trending", TERMS)
    assert (8, "flavour") in matches


def test_match_terms_matches_multi_word_label():
    matches = match_terms("Dubai Chocolate bars sold out", TERMS)
    assert (9, "format") in matches
    assert (9, "flavour") in matches


def test_match_terms_produces_one_pair_per_category():
    matches = match_terms("dubai chocolate everywhere", TERMS)
    assert len(matches) == 2


def test_match_terms_no_match_returns_empty():
    assert match_terms("a plain sentence about baking", TERMS) == []


def test_match_terms_respects_word_boundaries():
    # 'cookie' must not match inside an unrelated longer word.
    matches = match_terms("cookiecutter shapes for kids", TERMS)
    assert not any(term_id == 4 for term_id, _ in matches)


def test_match_terms_skips_terms_without_a_persisted_id():
    unsaved = Term(slug="new_term", label="new term", categories=["flavour"])
    assert match_terms("new term appears here", [unsaved]) == []


class _FakeRepoForTagging:
    """Fake SupabaseRepository for tag_blog_items, no network."""

    def __init__(self, terms, items):
        self._terms = terms
        self._items = items
        self.insert_calls: list[list] = []

    def get_terms(self):
        return self._terms

    def get_items_by_source(self, source, fields="id,title,body"):
        assert source == "blog"
        return self._items

    def insert_item_terms(self, item_terms):
        self.insert_calls.append(item_terms)
        # Simulate ON CONFLICT DO NOTHING: dedupe against nothing already
        # inserted in this fake (a real duplicate-avoidance test is below).
        return item_terms


def test_tag_blog_items_inserts_matches_for_each_item():
    repo = _FakeRepoForTagging(
        terms=TERMS,
        items=[
            {"id": ITEM_1, "title": "Pistachio Croissants", "body": "so good"},
            {"id": ITEM_2, "title": "Plain Bread", "body": "nothing special"},
        ],
    )
    inserted = tag_blog_items(repo)

    assert inserted == 1
    [item_terms] = repo.insert_calls
    assert len(item_terms) == 1
    assert str(item_terms[0].item_id) == ITEM_1
    assert item_terms[0].term_id == 8
    assert item_terms[0].category == "flavour"


def test_tag_blog_items_does_not_create_new_terms():
    # tag_blog_items only ever reads repo.get_terms(); it has no code path
    # that inserts into `terms`, so no fake term can appear in item_terms.
    repo = _FakeRepoForTagging(
        terms=[], items=[{"id": ITEM_1, "title": "Ube Bread", "body": ""}]
    )
    inserted = tag_blog_items(repo)
    assert inserted == 0
    assert repo.insert_calls == [] or repo.insert_calls == [[]]


class _FakeRepoWithConflictDedup:
    """Fake repo whose insert_item_terms mimics ON CONFLICT DO NOTHING against
    a pre-existing set of (item_id, term_id, category) rows."""

    def __init__(self, terms, items, existing: set[tuple[str, int, str]]):
        self._terms = terms
        self._items = items
        self._existing = set(existing)
        self.insert_calls: list[list] = []

    def get_terms(self):
        return self._terms

    def get_items_by_source(self, source, fields="id,title,body"):
        return self._items

    def insert_item_terms(self, item_terms):
        self.insert_calls.append(item_terms)
        new = [
            it
            for it in item_terms
            if (str(it.item_id), it.term_id, it.category) not in self._existing
        ]
        for it in new:
            self._existing.add((str(it.item_id), it.term_id, it.category))
        return new


def test_tag_blog_items_does_not_error_on_pre_existing_mention():
    repo = _FakeRepoWithConflictDedup(
        terms=TERMS,
        items=[{"id": ITEM_1, "title": "Pistachio Croissants", "body": ""}],
        existing={(ITEM_1, 8, "flavour")},
    )
    inserted = tag_blog_items(repo)
    assert inserted == 0  # already tagged; ignored, not an error
