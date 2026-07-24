# Shared data contracts

This directory holds the JSON Schema contracts shared across TrendBaker AI's workstreams. They are the interface boundary between teams working in parallel, so all four workstreams should validate against these schemas rather than inventing ad hoc shapes.

## Contracts

- **`normalized-content.schema.json`** — the shape the YouTube collector produces. The Supabase database and the trend engine consume these objects.
- **`blog-article.schema.json`** — the exact shape `BlogRssCollector.collect()` returns (`backend/src/trendbaker/collectors/blog_rss.py`), which maps column-for-column into the shared `items` table (there is no separate `blog_articles` table — see [docs/db-schema.md](../docs/db-schema.md)). This is a **separate contract**, not a variant of `normalized-content`, because Blog/RSS articles carry no real engagement metrics (RSS/Atom feeds don't reliably expose views/likes/comments — those fields are present but always `0`, a known limitation of the shared `trendbaker.models.Item` typing these as plain `int`, not `int | None`; see the module docstring in `blog_rss.py`). See [docs/blog-rss-sources.md](../docs/blog-rss-sources.md) for the source list and ethical rules behind it.
- **`trend-summary.schema.json`** — the shape produced by the trend engine after scoring, regardless of which source(s) contributed. The Next.js dashboard consumes these objects exclusively; it should never need to read raw normalized-content or blog-article objects directly.

## How the contracts connect the workstreams

- **YouTube API data collection** must produce `normalized-content` objects, one per collected item.
- **Blog/RSS data collection** must produce `blog-article` objects, one per collected article.
- **Supabase database** stores both `normalized-content` and `blog-article` objects in the same shared `items` table (discriminated by `source`), and the trend engine reads them back out.
- **Trend scoring and entity extraction** reads both content types and produces `trend-summary` objects.
- **Next.js dashboard** reads only `trend-summary` objects.

```
YouTube collector   ──> normalized-content ──┐
                                              ├──> Supabase ──> trend engine ──> trend-summary ──> dashboard
Blog/RSS collector  ──> blog-article       ──┘
```

## Change policy

These schemas are a cross-team agreement. Any change to a required field, an enum, or a type must be discussed and agreed with all four workstreams before merging, since a silent breaking change here will break collectors, storage, scoring, or the dashboard without an obvious error at the point of change. This applies equally to `blog-article.schema.json` — coordinate with the YouTube-collector workstream before changing it.
