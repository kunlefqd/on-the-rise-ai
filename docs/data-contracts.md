# Data contracts

TrendBaker AI has three shared JSON Schema contracts, all defined in [`contracts/`](../contracts/). See [`contracts/README.md`](../contracts/README.md) for the full change policy; this page explains what each contract represents.

## `normalized-content`

Represents a single piece of public content collected from the YouTube source, normalized to a common shape. Produced by the YouTube collector, consumed by the database and the trend engine.

Key fields: `source`, `external_id`, `title`, `url`, `content_type`, `metrics` (views/likes/comments/shares, any of which may be `null` if unavailable), and `captured_at`.

## `blog-article`

Represents a single article collected from a Blog/RSS source (RSS/Atom feed only — see [docs/blog-rss-sources.md](blog-rss-sources.md)). This contract is the exact output shape of `BlogRssCollector.collect()` (`backend/src/trendbaker/collectors/blog_rss.py`), which maps column-for-column into the shared `items` table — there is no separate `blog_articles` table (see [docs/db-schema.md](db-schema.md)). This is a **separate contract from `normalized-content`**, not a variant of it: Blog/RSS articles have engagement-metric fields (`views`, `likes`, `comments_count`) that are always `0`, since RSS/Atom feeds don't reliably expose them — `0` rather than `null` because the shared `trendbaker.models.Item` types these as plain `int`, not `int | None` (a known limitation; see `blog_rss.py`'s module docstring for the recommended fix).

Key fields: `source` (fixed `"blog"`), `source_id` (the feed's guid, or a deterministic hash of the URL as a fallback), `title`, `url`, `body` (short excerpt only, never a full article body, capped at 1000 characters), `author` (the publication's name, e.g. "King Arthur Baking Blog" — not a personal byline), `published_at`, `region` (always `null` today), `views`/`likes`/`comments_count` (always `0` today), `collected_at`, and `raw` (an object carrying the feed's machine slug and feed URL, plus format-specific metadata like the RSS guid or Atom id — never full article content).

## `trend-summary`

Represents one computed, scored trend (a format, flavour, ingredient, or consumer attribute) derived from one or more `normalized-content` items. Produced by the trend engine, consumed exclusively by the dashboard.

Key fields: `trend_name`, `category`, `trend_score`, `confidence`, `source_count`, `supporting_item_count`, and `last_updated`.

## Why separate contracts per source, instead of one

Keeping raw collected content and computed trend summaries as separate contracts lets the trend-scoring workstream change its methodology freely as long as it still emits a valid `trend-summary`, without ever requiring a change to what collectors produce or what the dashboard reads. Keeping `normalized-content` and `blog-article` as two distinct contracts (rather than forcing Blog/RSS into the YouTube shape) avoids modeling engagement metrics that don't exist for RSS-sourced articles — every future source type gets its own contract only if its data shape genuinely differs; otherwise it should reuse an existing one.
