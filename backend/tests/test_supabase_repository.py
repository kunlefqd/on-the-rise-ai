from trendbaker.models import Term
from trendbaker.repositories.supabase_repository import SupabaseRepository


class _FakeExecuteResult:
    def __init__(self, data):
        self.data = data


class _FakeRequestBuilder:
    """Minimal fake of postgrest's chainable request builder, recording the
    call actually made (only resolved at .execute()) so tests can assert on
    table/op/args without a real network connection."""

    def __init__(self, table_name: str, calls: list, table_data: dict):
        self.table_name = table_name
        self._calls = calls
        self._table_data = table_data
        self._filters: dict = {}
        self._op: str | None = None
        self._payload = None
        self._on_conflict = ""
        self._ignore_duplicates = False

    def select(self, fields):
        self._op = "select"
        self._select_fields = fields
        return self

    def eq(self, column, value):
        self._filters[column] = value
        return self

    def update(self, payload):
        self._op = "update"
        self._payload = payload
        return self

    def upsert(self, payload, *, on_conflict="", ignore_duplicates=False):
        self._op = "upsert"
        self._payload = payload
        self._on_conflict = on_conflict
        self._ignore_duplicates = ignore_duplicates
        return self

    def execute(self):
        if self._op == "upsert":
            self._calls.append(
                {
                    "op": "upsert",
                    "table": self.table_name,
                    "payload": self._payload,
                    "on_conflict": self._on_conflict,
                    "ignore_duplicates": self._ignore_duplicates,
                }
            )
            return _FakeExecuteResult(self._payload)

        if self._op == "update":
            self._calls.append(
                {
                    "op": "update",
                    "table": self.table_name,
                    "payload": self._payload,
                    "filters": dict(self._filters),
                }
            )
            return _FakeExecuteResult([self._payload])

        # select
        rows = self._table_data.get(self.table_name, [])
        for column, value in self._filters.items():
            rows = [r for r in rows if r.get(column) == value]
        self._calls.append({"op": "select", "table": self.table_name})
        return _FakeExecuteResult(rows)


class _FakeClient:
    def __init__(self, table_data: dict | None = None):
        self.calls: list = []
        self._table_data = table_data or {}

    def table(self, table_name):
        return _FakeRequestBuilder(table_name, self.calls, self._table_data)


def _repo_with_fake_client(table_data: dict | None = None):
    repo = SupabaseRepository()
    fake_client = _FakeClient(table_data)
    repo._client = fake_client  # bypass settings.require()/create_client for this unit test
    return repo, fake_client


def test_get_items_by_source_filters_by_source():
    repo, client = _repo_with_fake_client(
        table_data={
            "items": [
                {"id": "1", "source": "blog", "body": "a"},
                {"id": "2", "source": "youtube", "body": "b"},
            ]
        }
    )
    result = repo.get_items_by_source("blog", fields="id,body")

    assert result == [{"id": "1", "source": "blog", "body": "a"}]


def test_get_items_by_source_returns_empty_list_for_no_data():
    repo, client = _repo_with_fake_client(table_data={"items": []})
    assert repo.get_items_by_source("blog") == []


def test_update_item_body_updates_only_body_column():
    repo, client = _repo_with_fake_client()
    repo.update_item_body("item-1", "cleaned text")

    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["op"] == "update"
    assert call["table"] == "items"
    assert call["payload"] == {"body": "cleaned text"}
    assert call["filters"] == {"id": "item-1"}


def test_get_terms_parses_rows_into_term_models():
    repo, client = _repo_with_fake_client(
        table_data={
            "terms": [
                {"id": 8, "slug": "pistachio", "label": "pistachio", "categories": ["flavour"]},
            ]
        }
    )
    terms = repo.get_terms()

    assert len(terms) == 1
    assert isinstance(terms[0], Term)
    assert terms[0].id == 8
    assert terms[0].slug == "pistachio"
    assert terms[0].categories == ["flavour"]
