import json
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path

from trendbaker.collectors.blog_rss import (
    BlogRssCollector,
    BlogSource,
    _guid_or_fallback,
    _html_to_text,
    clean_existing_blog_bodies,
    parse_rss_entries,
)

CONTRACT_PATH = Path(__file__).resolve().parents[2] / "contracts" / "blog-article.schema.json"


def _to_contract_instance(item) -> dict:
    """Serialize an Item the way the contract describes a collector output
    record: every field present (mode="json" without exclude_none), minus
    fields the collector itself never sets — `id` (database-generated) and
    `sentiment` (populated by a later enrichment pass, per models.Item's own
    docstring). The real SupabaseRepository.upsert_items() call additionally
    uses exclude_none=True to avoid overwriting existing values with null on
    upsert — a storage-layer optimization, not part of this shape contract."""
    dumped = item.model_dump(mode="json")
    dumped.pop("id", None)
    dumped.pop("sentiment", None)
    return dumped


def _check_type(value, type_spec) -> bool:
    types = type_spec if isinstance(type_spec, list) else [type_spec]
    for t in types:
        if t == "null" and value is None:
            return True
        if t == "string" and isinstance(value, str):
            return True
        if t == "object" and isinstance(value, dict):
            return True
    return False


def _check_format(value, fmt: str) -> bool:
    if fmt == "uri":
        return isinstance(value, str) and value.startswith(("http://", "https://"))
    if fmt == "date-time":
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            return True
        except (TypeError, ValueError):
            return False
    return True


def _validate_against_schema(instance: dict, schema: dict) -> None:
    """Minimal validator covering exactly the JSON Schema features this one
    schema uses (type unions incl. null, const, min/maxLength, format uri/
    date-time, required, additionalProperties, one level of nested object).
    Not a general-purpose JSON Schema engine.
    """
    properties = schema.get("properties", {})

    for key in schema.get("required", []):
        assert key in instance, f"missing required field: {key}"

    if schema.get("additionalProperties") is False:
        extra = set(instance.keys()) - set(properties.keys())
        assert not extra, f"unexpected fields not in contract: {extra}"

    for key, value in instance.items():
        if key not in properties:
            continue
        prop_schema = properties[key]

        if "const" in prop_schema:
            assert value == prop_schema["const"], (
                f"{key}: expected const {prop_schema['const']!r}, got {value!r}"
            )
            continue

        if "type" in prop_schema:
            assert _check_type(value, prop_schema["type"]), (
                f"{key}: value {value!r} does not match type {prop_schema['type']!r}"
            )

        if value is None:
            continue

        if "minLength" in prop_schema:
            assert len(value) >= prop_schema["minLength"], f"{key}: shorter than minLength"
        if "maxLength" in prop_schema:
            assert len(value) <= prop_schema["maxLength"], f"{key}: longer than maxLength"
        if "format" in prop_schema:
            assert _check_format(value, prop_schema["format"]), (
                f"{key}: value {value!r} does not match format {prop_schema['format']!r}"
            )
        if prop_schema.get("type") == "object":
            _validate_against_schema(value, prop_schema)


SOURCE = BlogSource(
    slug="test_source",
    name="Test Bakery Blog",
    website_url="https://example.com",
    feed_url="https://example.com/feed",
)

EXPECTED_ITEM_FIELDS = {
    "id",
    "source",
    "source_id",
    "url",
    "title",
    "body",
    "author",
    "published_at",
    "region",
    "views",
    "likes",
    "comments_count",
    "sentiment",
    "collected_at",
    "raw",
}

RSS_WITH_GUID = """<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Pistachio Croissants Are Everywhere</title>
      <link>https://example.com/pistachio-croissants</link>
      <guid>example-guid-123</guid>
      <pubDate>Wed, 22 Jul 2026 10:00:00 GMT</pubDate>
      <description>A short summary about pistachio croissants.</description>
      <content:encoded xmlns:content="http://purl.org/rss/1.0/modules/content/">
        This is the FULL article body that must never be stored.
      </content:encoded>
    </item>
  </channel>
</rss>
"""

RSS_WITH_ISO8601_PUBDATE = """<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Sourdough Focaccia</title>
      <link>https://example.com/sourdough-focaccia</link>
      <guid>iso-date-guid</guid>
      <pubDate>2026-07-22T10:00:00-0400</pubDate>
      <description>A short summary about sourdough focaccia.</description>
    </item>
  </channel>
</rss>
"""

RSS_WITHOUT_GUID = """<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Ube Is Trending</title>
      <link>https://example.com/ube-is-trending</link>
      <pubDate>Thu, 23 Jul 2026 08:30:00 GMT</pubDate>
      <description>A short summary about ube.</description>
    </item>
  </channel>
</rss>
"""

RSS_WITH_HTML_DESCRIPTION = (
    "<?xml version=\"1.0\"?>\n"
    "<rss version=\"2.0\">\n"
    "  <channel>\n"
    "    <item>\n"
    "      <title>Sourdough Tips</title>\n"
    "      <link>https://example.com/sourdough-tips</link>\n"
    "      <guid>html-description-guid</guid>\n"
    "      <description>&lt;p&gt;Great &lt;em&gt;sourdough&lt;/em&gt; needs "
    "&lt;a href=\"https://example.com\"&gt;patience&lt;/a&gt; and&amp;nbsp;time."
    "&lt;/p&gt;   &lt;p&gt;It&amp;#8217;s worth it.&lt;/p&gt;</description>\n"
    "    </item>\n"
    "  </channel>\n"
    "</rss>\n"
)

ATOM_FEED = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Matcha Bakes</title>
    <id>tag:example.com,2026:matcha-bakes</id>
    <link href="https://example.com/matcha-bakes" />
    <updated>2026-07-21T12:00:00Z</updated>
    <summary>A short summary about matcha bakes.</summary>
  </entry>
</feed>
"""


def test_rss_entry_normalizes_into_item_model():
    rows = parse_rss_entries(RSS_WITH_GUID.encode("utf-8"), SOURCE)
    assert len(rows) == 1
    item = rows[0]

    assert set(type(item).model_fields.keys()) == EXPECTED_ITEM_FIELDS
    assert item.source == "blog"
    assert item.source_id == "example-guid-123"
    assert item.url == "https://example.com/pistachio-croissants"
    assert item.title == "Pistachio Croissants Are Everywhere"
    assert item.author == "Test Bakery Blog"
    assert item.published_at == datetime(2026, 7, 22, 10, 0, tzinfo=UTC)
    assert item.region is None


def test_engagement_metrics_default_to_zero_under_shared_item_model():
    # trendbaker.models.Item types views/likes/comments_count as plain int
    # (default 0), not int | None, so Blog/RSS items get 0, not null, even
    # though RSS/Atom feeds never actually provide these. This is a known
    # regression from the null-safety the dict-based collector had before
    # adopting the shared model — see the module docstring for the
    # recommended (small, backward-compatible) model fix.
    rows = parse_rss_entries(RSS_WITH_GUID.encode("utf-8"), SOURCE)
    item = rows[0]
    assert item.views == 0
    assert item.likes == 0
    assert item.comments_count == 0


def test_no_full_article_body_is_stored():
    rows = parse_rss_entries(RSS_WITH_GUID.encode("utf-8"), SOURCE)
    item = rows[0]

    assert item.body == "A short summary about pistachio croissants."
    assert "FULL article body" not in item.body
    assert "FULL article body" not in str(item.raw)


def test_excerpt_is_truncated_when_too_long():
    long_description = "x" * 5000
    xml = f"""<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <item>
      <title>Long Article</title>
      <link>https://example.com/long-article</link>
      <guid>long-article-guid</guid>
      <description>{long_description}</description>
    </item>
  </channel>
</rss>
"""
    rows = parse_rss_entries(xml.encode("utf-8"), SOURCE)
    assert len(rows[0].body) <= 1000


def test_rss_pub_date_falls_back_to_iso8601_when_not_rfc822():
    # Real-world quirk observed live from King Arthur Baking Blog's feed,
    # which uses ISO 8601 in <pubDate> instead of the RFC 822 the RSS 2.0
    # spec calls for. Must not silently drop the date.
    rows = parse_rss_entries(RSS_WITH_ISO8601_PUBDATE.encode("utf-8"), SOURCE)
    expected = datetime(2026, 7, 22, 10, 0, tzinfo=timezone(timedelta(hours=-4)))
    assert rows[0].published_at == expected


def test_guid_fallback_is_deterministic_hash_of_url():
    rows = parse_rss_entries(RSS_WITHOUT_GUID.encode("utf-8"), SOURCE)
    item = rows[0]

    assert item.source_id.startswith("url-")
    # Re-parsing the same entry must produce the same fallback id, since the
    # shared items table upserts on (source, source_id).
    rows_again = parse_rss_entries(RSS_WITHOUT_GUID.encode("utf-8"), SOURCE)
    assert item.source_id == rows_again[0].source_id


def test_guid_or_fallback_uses_guid_when_present():
    assert _guid_or_fallback("some-guid", "https://example.com/x") == "some-guid"


def test_guid_or_fallback_hashes_url_when_guid_missing():
    fallback = _guid_or_fallback(None, "https://example.com/x")
    assert fallback.startswith("url-")
    assert len(fallback) == len("url-") + 64  # sha256 hex digest length


def test_atom_entry_normalizes_into_item_model():
    rows = parse_rss_entries(ATOM_FEED.encode("utf-8"), SOURCE)
    assert len(rows) == 1
    item = rows[0]

    assert set(type(item).model_fields.keys()) == EXPECTED_ITEM_FIELDS
    assert item.source == "blog"
    assert item.source_id == "tag:example.com,2026:matcha-bakes"
    assert item.url == "https://example.com/matcha-bakes"
    assert item.title == "Matcha Bakes"
    assert item.body == "A short summary about matcha bakes."
    assert item.published_at == datetime(2026, 7, 21, 12, 0, tzinfo=UTC)


def test_collector_source_name():
    assert BlogRssCollector.source_name == "blog_rss"


def test_rss_output_conforms_to_blog_article_contract():
    schema = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    rows = parse_rss_entries(RSS_WITH_GUID.encode("utf-8"), SOURCE)
    _validate_against_schema(_to_contract_instance(rows[0]), schema)


def test_atom_output_conforms_to_blog_article_contract():
    schema = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    rows = parse_rss_entries(ATOM_FEED.encode("utf-8"), SOURCE)
    _validate_against_schema(_to_contract_instance(rows[0]), schema)


def test_html_tags_are_stripped_from_description():
    rows = parse_rss_entries(RSS_WITH_HTML_DESCRIPTION.encode("utf-8"), SOURCE)
    body = rows[0].body
    assert "<" not in body
    assert ">" not in body
    assert "sourdough" in body
    assert "patience" in body


def test_html_entities_are_decoded():
    rows = parse_rss_entries(RSS_WITH_HTML_DESCRIPTION.encode("utf-8"), SOURCE)
    body = rows[0].body
    assert "&nbsp;" not in body
    assert "&#8217;" not in body
    assert "\xa0" not in body  # nbsp decoded then collapsed to a plain space
    assert "It’s worth it." in body  # curly-quote entity decoded to U+2019


def test_whitespace_is_normalized():
    rows = parse_rss_entries(RSS_WITH_HTML_DESCRIPTION.encode("utf-8"), SOURCE)
    body = rows[0].body
    assert "  " not in body  # no double spaces left from stripped tags
    assert body == body.strip()


def test_html_to_text_handles_none():
    assert _html_to_text(None) is None


class _FakeRepoForCleanup:
    """Fake SupabaseRepository for clean_existing_blog_bodies, no network."""

    def __init__(self, items: list[dict]):
        self._items = items
        self.updates: list[tuple[str, str | None]] = []

    def get_items_by_source(self, source, fields="id,body"):
        assert source == "blog"
        return self._items

    def update_item_body(self, item_id, body):
        self.updates.append((item_id, body))


def test_clean_existing_blog_bodies_only_updates_dirty_rows():
    repo = _FakeRepoForCleanup(
        [
            {"id": "1", "body": "<p>Has &amp;nbsp; HTML</p>"},
            {"id": "2", "body": "Already plain text"},
            {"id": "3", "body": None},
        ]
    )
    updated = clean_existing_blog_bodies(repo)

    assert updated == 1
    assert len(repo.updates) == 1
    assert repo.updates[0][0] == "1"
    assert "<" not in repo.updates[0][1]
