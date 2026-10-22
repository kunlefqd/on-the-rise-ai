"""Blog/RSS collector.

Fetches configured RSS/Atom feeds and normalizes entries into
``trendbaker.models.Item`` — the same model YouTube videos are collected
into, distinguished by ``source``. There is no separate blog_articles table:
Blog/RSS is a second `source` value ("blog") in the shared `items` table
(supabase/migrations/20260724101100_build_tables.sql, see docs/db-schema.md),
per docs/blog-rss-sources.md.

Ethical rules (see docs/ethical-data-policy.md and docs/blog-rss-sources.md):
  - RSS/Atom feeds only. No HTML scraping, no headless browsers.
  - Never bypass paywalls, logins, CAPTCHAs, bot controls, or robots
    restrictions.
  - Store only a short feed-provided excerpt/summary in `body` — never the
    full article text. Only title/link/guid-id/pubDate-or-updated/
    description-or-summary are read from each entry; a full-content field
    such as RSS's <content:encoded> is never read or stored.
  - Engagement metrics: ``Item.views``/``likes``/``comments_count`` are typed
    ``int`` (default 0) in ``trendbaker.models.Item``, not ``int | None``, so
    they are always 0 for Blog/RSS items, not left unset. Ideally these would
    be null (RSS/Atom feeds don't provide them, and 0 could be misread as
    "measured zero engagement") — this is a known limitation of adopting the
    shared model as-is; loosening those three fields to ``int | None = None``
    in trendbaker.models is a small, backward-compatible follow-up (YouTube
    always supplies real values, so its behavior wouldn't change).

Term extraction/tagging (`item_terms`) is implemented separately in
trendbaker.trend_engine.term_tagging, not here — that module runs generically
over `items` regardless of `source`, since `item_terms` has no source-specific
columns. See the "How the pieces connect" section of docs/db-schema.md.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
from typing import TYPE_CHECKING
from xml.etree import ElementTree

import httpx

from trendbaker.collectors.base import Collector
from trendbaker.models import Item

if TYPE_CHECKING:
    from trendbaker.repositories.supabase_repository import SupabaseRepository

EXCERPT_MAX_LENGTH = 1000
_REQUEST_TIMEOUT_SECONDS = 10.0
_USER_AGENT = "TrendBakerAI-BlogRssCollector/0.1 (+https://github.com/harshikamboj/FGFHackathon26)"

_ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


@dataclass(frozen=True)
class BlogSource:
    """One configured RSS/Atom source. See docs/blog-rss-sources.md."""

    slug: str
    name: str
    website_url: str
    feed_url: str
    enabled: bool = True


# Configured MVP sources. Setting enabled=False disables a source without
# removing its configuration or losing collection history.
BLOG_SOURCES: list[BlogSource] = [
    BlogSource(
        slug="king_arthur_baking",
        name="King Arthur Baking Blog",
        website_url="https://www.kingarthurbaking.com",
        feed_url="https://www.kingarthurbaking.com/blog/feed",
    ),
    BlogSource(
        slug="food_dive",
        name="Food Dive",
        website_url="https://www.fooddive.com",
        feed_url="https://www.fooddive.com/feeds/news/",
    ),
    BlogSource(
        slug="the_kitchn",
        name="The Kitchn",
        website_url="https://www.thekitchn.com",
        feed_url="https://www.thekitchn.com/main.rss",
    ),
]


def _text(element: ElementTree.Element | None) -> str | None:
    if element is None or element.text is None:
        return None
    stripped = element.text.strip()
    return stripped or None


def _truncate(value: str | None, max_length: int) -> str | None:
    if value is None:
        return None
    if len(value) <= max_length:
        return value
    return value[: max_length - 1].rstrip() + "…"


class _HTMLTextExtractor(HTMLParser):
    """Collects text data while discarding tags. Stdlib only."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        self._chunks.append(data)

    def get_text(self) -> str:
        return "".join(self._chunks)


_WHITESPACE_RE = re.compile(r"\s+")


def _html_to_text(raw: str | None) -> str | None:
    """Strip HTML tags, decode entities, and collapse whitespace.

    Applied to RSS <description> / Atom <summary> only — a short
    feed-provided excerpt, never <content:encoded> or any full-body field,
    which are never read from the feed in the first place. Stdlib only
    (html.parser + html.unescape); no BeautifulSoup.
    """
    if raw is None:
        return None
    parser = _HTMLTextExtractor()
    parser.feed(raw)
    parser.close()
    # convert_charrefs already decodes most entities in text nodes; unescape
    # again to catch anything left over (e.g. double-escaped entities).
    text = unescape(parser.get_text())
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text or None


def _guid_or_fallback(guid: str | None, url: str | None) -> str:
    """RSS/Atom guid when available; otherwise a deterministic hash of the URL.

    The fallback must be deterministic so re-polling the same feed upserts
    the same item (via the shared `items` table's unique(source, source_id))
    instead of inserting duplicates.
    """
    if guid:
        return guid
    basis = url or ""
    return "url-" + hashlib.sha256(basis.encode("utf-8")).hexdigest()


def _parse_iso8601(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_rss_pub_date(value: str | None) -> datetime | None:
    """Parse an RSS <pubDate>.

    The RSS 2.0 spec mandates RFC 822, but some real feeds (observed: King
    Arthur Baking Blog) use ISO 8601 instead — fall back to that rather than
    silently dropping the date.
    """
    if not value:
        return None
    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return _parse_iso8601(value)


def parse_rss_entries(xml_bytes: bytes, source: BlogSource) -> list[Item]:
    """Parse an RSS 2.0 (<item>) or Atom (<entry>) feed body into Item models.

    Pure function: no network I/O. Returned Items are ready for
    SupabaseRepository.upsert_items() (upsert on (source, source_id)).
    """
    root = ElementTree.fromstring(xml_bytes)
    rows: list[Item] = []

    for entry in root.findall("./channel/item"):
        link = _text(entry.find("link"))
        guid = _text(entry.find("guid"))
        pub_date = _text(entry.find("pubDate"))
        rows.append(
            Item(
                source="blog",
                source_id=_guid_or_fallback(guid, link),
                url=link,
                title=_text(entry.find("title")),
                body=_truncate(
                    _html_to_text(_text(entry.find("description"))), EXCERPT_MAX_LENGTH
                ),
                author=source.name,
                published_at=_parse_rss_pub_date(pub_date),
                region=None,
                collected_at=datetime.now(UTC),
                raw={
                    "feed_slug": source.slug,
                    "feed_url": source.feed_url,
                    "guid": guid,
                    "link": link,
                    "pub_date": pub_date,
                },
            )
        )

    for entry in root.findall("./atom:entry", _ATOM_NS):
        link_el = entry.find("atom:link", _ATOM_NS)
        link = link_el.get("href") if link_el is not None else None
        entry_id = _text(entry.find("atom:id", _ATOM_NS))
        updated = _text(entry.find("atom:updated", _ATOM_NS)) or _text(
            entry.find("atom:published", _ATOM_NS)
        )
        summary = _text(entry.find("atom:summary", _ATOM_NS))
        rows.append(
            Item(
                source="blog",
                source_id=_guid_or_fallback(entry_id, link),
                url=link,
                title=_text(entry.find("atom:title", _ATOM_NS)),
                body=_truncate(_html_to_text(summary), EXCERPT_MAX_LENGTH),
                author=source.name,
                published_at=_parse_iso8601(updated),
                region=None,
                collected_at=datetime.now(UTC),
                raw={
                    "feed_slug": source.slug,
                    "feed_url": source.feed_url,
                    "id": entry_id,
                    "link": link,
                    "updated": updated,
                },
            )
        )

    return rows


class BlogRssCollector(Collector):
    source_name = "blog_rss"

    def fetch(self, feed_url: str) -> bytes:
        """Fetch one feed's raw bytes. Performs a real HTTP GET."""
        response = httpx.get(
            feed_url,
            timeout=_REQUEST_TIMEOUT_SECONDS,
            headers={"User-Agent": _USER_AGENT},
        )
        response.raise_for_status()
        return response.content

    def collect(self) -> list[Item]:
        rows: list[Item] = []
        for source in BLOG_SOURCES:
            if not source.enabled:
                continue
            xml_bytes = self.fetch(source.feed_url)
            rows.extend(parse_rss_entries(xml_bytes, source))
        return rows


def clean_existing_blog_bodies(repo: SupabaseRepository) -> int:
    """Reprocess already-stored source='blog' rows in `items`, converting any
    HTML left in `body` (from before _html_to_text existed) into plain text.

    Only `body` is written — title, source_id, source, published_at, author,
    url, views/likes/comments_count, and raw are all left untouched, since
    the update targets a single column by id. Rows whose body is already
    clean are left alone (no-op), so this is safe to re-run. Does not run
    automatically: call this explicitly when approved, e.g.:

        from trendbaker.collectors.blog_rss import clean_existing_blog_bodies
        from trendbaker.repositories.supabase_repository import SupabaseRepository
        updated = clean_existing_blog_bodies(SupabaseRepository())
        print(f"updated {updated} blog rows")
    """
    items = repo.get_items_by_source("blog", fields="id,body")
    updated = 0
    for item in items:
        original = item.get("body")
        cleaned = _html_to_text(original)
        if cleaned != original:
            repo.update_item_body(item["id"], cleaned)
            updated += 1
    return updated
