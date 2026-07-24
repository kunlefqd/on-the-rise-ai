# Architecture

TrendBaker AI is a pipeline: permitted public signals flow through collection, normalization, storage, scoring, and display, with an AI assistant layered on top once the pipeline is proven out.

```
Official APIs / RSS / permitted public websites
        │
        ▼
Python collectors            (backend/src/trendbaker/collectors)
        │
        ▼
normalized-content contract  (contracts/normalized-content.schema.json)
        │
        ▼
Supabase PostgreSQL          (supabase/)
        │
        ▼
Trend entity extraction and scoring
                              (backend/src/trendbaker/trend_engine)
        │
        ▼
trend-summary contract       (contracts/trend-summary.schema.json)
        │
        ▼
Next.js dashboard            (frontend/)
        │
        ▼
Restricted read-only AI tools (later)
```

## Why this shape

- **Collectors are isolated per source.** Each collector (YouTube first, others later) only needs to know how to talk to its source and how to emit a `normalized-content` object. It does not need to know about Supabase, scoring, or the dashboard.
- **The normalized-content contract is the boundary between collection and everything else.** The database and trend engine only ever consume this shape, regardless of which source produced it.
- **Supabase is the single source of truth.** Raw normalized content and computed trend summaries both live there, so the trend engine and dashboard read from one place.
- **The trend-summary contract is the boundary between scoring and display.** The dashboard never computes scores itself and never reads raw content directly — it only reads trend summaries.
- **The AI assistant comes last.** It will be given restricted, read-only tools once there is real data flowing through the pipeline to query. See the root [README](../README.md) for the rule on when that work starts.

## Repository layout

See the root [README.md](../README.md) for the full repository structure and how it maps to the four parallel workstreams.
