# Trend scoring

This document lists the planned scoring categories only. **Weights and the final scoring formula are not finalized** — `backend/src/trendbaker/trend_engine/scoring.py` is a placeholder interface, not an implementation.

Planned categories:

- **Velocity** — how fast a signal is growing over time.
- **Engagement** — the volume and quality of engagement (views, likes, comments, shares) relative to the item's reach. YouTube-only: see below.
- **Cross-source confirmation** — whether the same entity is appearing across multiple independent sources, not just one.
- **Recency** — how recently supporting items were published or captured.
- **Novelty** — how new or unexpected the entity is relative to prior observations.
- **Confidence** — an overall confidence signal derived from the categories above and the amount of supporting data.

The trend-scoring workstream owns turning these categories into an actual weighted formula. Until that's agreed, `trend_score` in [`contracts/trend-summary.schema.json`](../contracts/trend-summary.schema.json) should be treated as provisional wherever it's consumed.

## How this maps onto the actual shared schema

The database (`supabase/migrations/20260724101100_build_tables.sql`, see [docs/db-schema.md](db-schema.md)) uses one shared schema for every source, not per-source tables: `items` (one row per collected video or article, discriminated by `source`), `item_terms` (mentions), and the `term_week_stats` materialized view (the weekly rollup insight is actually computed from).

`term_week_stats` already groups by `source` alongside `term_id`/`category`/`region`/`week`, so YouTube and Blog/RSS rollups are naturally kept separate per source while sharing one mechanism — no separate per-source scoring table exists or is needed for that.

Not every planned category is equally available for every source today:

- **YouTube** items have `views`/`likes`/`comments_count` populated, so an engagement-based score is possible.
- **Blog/RSS** items (`source = 'blog'`) always have `views`/`likes`/`comments_count` as `null` — RSS/Atom feeds don't reliably expose engagement metrics, so Blog/RSS trend signal leans on **article volume** (`item_count`), **source diversity** (distinct blogs covering the same term — this source's version of cross-source confirmation), **recency**, and **novelty** instead. See [docs/blog-rss-sources.md](blog-rss-sources.md).

`items` currently stores only the latest metrics per row (upserted on `(source, source_id)`) — there is no historical metrics snapshot table. So today's trend signal reflects publication timing, term-mention frequency, and the most recently observed engagement numbers, not true per-item velocity over time. Adding a historical snapshot table is a possible future enhancement, not implemented here.
