# Shared data contracts

This directory holds the JSON Schema contracts shared across TrendBaker AI's workstreams. They are the interface boundary between teams working in parallel, so all four workstreams should validate against these schemas rather than inventing ad hoc shapes.

## Contracts

- **`normalized-content.schema.json`** — the shape every collector (YouTube, and any future source) must produce. The Supabase database and the trend engine consume these objects; nothing downstream should need to know which source an item came from beyond the `source` field.
- **`trend-summary.schema.json`** — the shape produced by the trend engine after scoring. The Next.js dashboard consumes these objects exclusively; it should never need to read raw normalized-content directly.

## How the contracts connect the workstreams

- **YouTube API data collection** must produce `normalized-content` objects, one per collected item.
- **Supabase database** stores `normalized-content` objects and the trend engine reads them back out.
- **Trend scoring and entity extraction** reads `normalized-content` objects and produces `trend-summary` objects.
- **Next.js dashboard** reads only `trend-summary` objects.

```
collectors ──> normalized-content ──> Supabase ──> trend engine ──> trend-summary ──> dashboard
```

## Change policy

These schemas are a cross-team agreement. Any change to a required field, an enum, or a type must be discussed and agreed with all four workstreams before merging, since a silent breaking change here will break collectors, storage, scoring, or the dashboard without an obvious error at the point of change.
