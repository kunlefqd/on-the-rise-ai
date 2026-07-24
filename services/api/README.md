# TrendBaker AI — FastAPI service

Backend layer for the CopilotKit chatbot on the Next.js frontend. Serves two
read-only endpoints backed by mock data until the Supabase migration is applied.

## Endpoints

- `GET /api/v1/trends?region=CA&limit=20` → `TrendSummary[]`
- `GET /api/v1/trends/{trend_name}` → `TrendDetail`

Response shapes are defined in `models/trend_summary.py` and
`models/trend_detail.py`, and are kept in exact sync with
`frontend/src/lib/types.ts` (the source of truth for the contract).

## Run locally

From the repo root:

```
cd services/api
python3.11 -m venv .venv        # or any Python >= 3.11
source .venv/bin/activate
pip install -r requirements.txt

# from the repo root, not services/api, so the `services.api` package resolves:
cd ../..
uvicorn services.api.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`, with CORS enabled for
the frontend dev server at `http://localhost:3000`.

Interactive docs: `http://localhost:8000/docs`.

## Mock data → Supabase swap

Every response currently comes from `mock_data.py` (`MOCK_TREND_SUMMARIES`,
`MOCK_TREND_DETAILS`). Each of those, and each route in `routes/trends.py`,
is marked with a `# TODO(supabase-swap): ...` comment describing exactly
what query should replace it once the migration in `supabase/migrations/`
is applied:

- `list_trends` → query the `trend_summary` table/view, filtering by
  `query_region_code` and applying `limit` as SQL `WHERE` / `LIMIT`
  instead of filtering the mock list in Python.
- `get_trend_detail` → query trend detail joined with supporting
  normalized-content rows by `trend_name`.

The Pydantic models and route signatures should not need to change for the
swap — only the data-fetching code inside `routes/trends.py` and
`mock_data.py`.

## Boundaries

This service only touches `services/api/`. It does not modify `frontend/`,
`supabase/`, or `contracts/`. No authentication is implemented (not needed
for the hackathon demo).
