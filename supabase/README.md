# Supabase

This directory holds the Supabase project's migrations, views, and seed data.

## Current schema

One shared migration (`20260724101100_build_tables.sql`, on `dev`) covers every source — see [docs/db-schema.md](../docs/db-schema.md) for the full column-level reference. There is no per-source migration or per-source table set:

- **`terms`** — canonical trend concepts (taxonomy).
- **`items`** — one row per collected piece of content (YouTube video, blog article, etc.), discriminated by the `source` column (`youtube` | `blog` | `retailer`). Blog/RSS articles are `source = 'blog'` rows in this same table, not a separate `blog_articles` table.
- **`item_terms`** — many-to-many mention bridge between `items` and `terms`.
- **`term_week_stats`** — a materialized view rolling item/engagement stats up by term, category, source, region, and week. Must be refreshed via the `refresh_term_week_stats()` RPC after each collection run — it does not update automatically on insert.

**Known gap:** this migration does not enable Row Level Security on `terms`, `items`, or `item_terms`, and a materialized view like `term_week_stats` cannot have RLS at all (which is why it shows as "Unrestricted" in the Supabase Table Editor — the underlying tables having no RLS is the same reason it also gets flagged there). Until RLS policies are added and reviewed, treat all four as **not safe to expose to `anon`/`authenticated` roles**; only trusted server-side (service-role) code should read or write them.

## Migrations

Put one SQL file per schema change in `migrations/`, named with a timestamp prefix so ordering is unambiguous:

```
migrations/20260101120000_create_normalized_content_table.sql
migrations/20260102090000_create_trend_summary_table.sql
```

Apply migrations with the Supabase CLI:

```
supabase db push
```

or, for local development, `supabase start` followed by `supabase migration up`.

## Views

Put read-only SQL views (e.g. materialized views used by the dashboard or trend engine) in `views/`, one file per view.

## Seed data

`seed.sql` is a **placeholder** — it does not yet contain real or representative seed data. Any seed data added here should be clearly labeled as simulated/seeded per [docs/ethical-data-policy.md](../docs/ethical-data-policy.md), never mistaken for real collected content.
