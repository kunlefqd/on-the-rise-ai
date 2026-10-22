# Database schema

The TrendBaker Supabase/Postgres schema, defined in [`supabase/migrations/20260724101100_build_tables.sql`](../supabase/migrations/20260724101100_build_tables.sql). This page is the shared reference so every workstream reads and writes the same shape.

**Model:** `terms` (taxonomy) → `items` (content) → `item_terms` (mentions bridge) → `term_week_stats` (weekly rollup materialized view).

## 1. `terms` — canonical concept dimension

One row per concept. A term can belong to multiple categories (e.g. Dubai chocolate is both a format and a flavour).

| Column | Type | Notes |
|---|---|---|
| `id` | `bigint` identity | PK |
| `slug` | `text` | **unique, not null** — canonical key, e.g. `dubai_chocolate` |
| `label` | `text` | not null — display name, e.g. `Dubai chocolate` |
| `categories` | `text[]` | not null, default `{}` — e.g. `{format,flavour}` |
| `created_at` | `timestamptz` | not null, default `now()` |

## 2. `items` — one row per collected piece of content

A YouTube video today; a blog post or retail product later. Same table, differentiated by `source`. That single fact is what lets us compare consumer buzz (youtube/blog) against market adoption (retailer).

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` | PK, default `gen_random_uuid()` |
| `source` | `text` | not null — `youtube` \| `blog` \| `retailer` |
| `source_id` | `text` | not null — video id / url / sku |
| `url` | `text` | nullable |
| `title` | `text` | nullable |
| `body` | `text` | nullable — description / article / product copy |
| `author` | `text` | nullable — channel / blog / brand |
| `published_at` | `timestamptz` | nullable |
| `region` | `text` | ISO code, or null = unscoped/global |
| `views` | `bigint` | default `0` |
| `likes` | `bigint` | default `0` |
| `comments_count` | `bigint` | default `0` |
| `sentiment` | `numeric` | optional, −1..1 from enrichment pass |
| `collected_at` | `timestamptz` | not null, default `now()` |
| `raw` | `jsonb` | full original payload |

- **Unique constraint:** `(source, source_id)` — enables idempotent upserts.
- **Indexes:** `published_at`, `source`, `region`.

## 3. `item_terms` — mention fact table (many-to-many)

Where the collector's `matched_terms` gets normalized. Grain is `(item, term, category)`, matching the collector's output exactly — a video tagged Dubai chocolate under both `format` and `flavour` is 2 rows.

| Column | Type | Notes |
|---|---|---|
| `item_id` | `uuid` | not null, FK → `items(id)` **on delete cascade** |
| `term_id` | `bigint` | not null, FK → `terms(id)` |
| `category` | `text` | not null — `format` \| `flavour` \| `ingredient` \| `dietary` |

- **Primary key:** `(item_id, term_id, category)`.
- **Index:** `(term_id, category)`.

## 4. `term_week_stats` — materialized view (the insight rollup)

Weekly grain smooths the spikiness of social data. Refresh on a schedule (Supabase cron / pg_cron) after each collection run.

- **Group by:** `term_id, category, source, region, week` (`week = date_trunc('week', published_at)`).
- **Filter:** rows where `published_at is null` are excluded.
- **Aggregates:**

| Column | Meaning |
|---|---|
| `item_count` | distinct items |
| `creator_count` | distinct authors — competitive breadth |
| `total_views` | sum of views |
| `total_likes` | sum of likes |
| `total_comments` | sum of comments |
| `avg_sentiment` | average sentiment |

- **Index:** `(term_id, category, week)`.

### `refresh_term_week_stats()` — RPC

SQL function that runs `refresh materialized view term_week_stats`. Call from the loader after ingestion:

```js
await supabase.rpc('refresh_term_week_stats')
```

## How the pieces connect (for writers)

1. Upsert a `terms` row per concept (unique on `slug`).
2. Upsert `items` on `(source, source_id)`.
3. Insert `item_terms` rows — one per `(item, term, category)` match.
4. After a batch, call `refresh_term_week_stats()`; read insights from `term_week_stats`.
