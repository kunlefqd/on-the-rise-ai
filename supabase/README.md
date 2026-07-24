# Supabase

This directory holds the Supabase project's migrations, views, and seed data. **No schema has been created yet** — this is a placeholder structure for the Supabase workstream to build on.

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
