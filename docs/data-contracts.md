# Data contracts

TrendBaker AI has two shared JSON Schema contracts, both defined in [`contracts/`](../contracts/). See [`contracts/README.md`](../contracts/README.md) for the full change policy; this page explains what each contract represents.

## `normalized-content`

Represents a single piece of public content collected from one source (e.g. a YouTube video), normalized to a common shape regardless of source. Produced by collectors, consumed by the database and the trend engine.

Key fields: `source`, `external_id`, `title`, `url`, `content_type`, `metrics` (views/likes/comments/shares, any of which may be `null` if unavailable), and `captured_at`.

## `trend-summary`

Represents one computed, scored trend (a format, flavour, ingredient, or consumer attribute) derived from one or more `normalized-content` items. Produced by the trend engine, consumed exclusively by the dashboard.

Key fields: `trend_name`, `category`, `trend_score`, `confidence`, `source_count`, `supporting_item_count`, and `last_updated`.

## Why two contracts instead of one

Keeping raw collected content and computed trend summaries as separate contracts lets the trend-scoring workstream change its methodology freely as long as it still emits a valid `trend-summary`, without ever requiring a change to what collectors produce or what the dashboard reads.
