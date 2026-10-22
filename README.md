# TrendBaker AI

TrendBaker AI collects permitted public bakery-related signals, preserves historical engagement metrics, identifies emerging bakery formats, flavours, ingredients, and consumer attributes, calculates transparent trend scores, and displays the findings in a dashboard. An AI assistant will later be able to query the results through restricted, read-only tools.

## Architecture

```
Official APIs / RSS / permitted public websites
        │
        ▼
Python collectors  →  normalized-content contract  →  Supabase PostgreSQL
        │
        ▼
Trend entity extraction and scoring  →  trend-summary contract
        │
        ▼
Next.js dashboard  →  restricted read-only AI tools (later)
```

See [docs/architecture.md](docs/architecture.md) for the full picture and [docs/data-contracts.md](docs/data-contracts.md) for the two contracts that connect these pieces.

## Repository structure

```
trendbaker-ai/
├── frontend/                 Next.js (React) dashboard
├── backend/                  Python collectors, repositories, trend engine, API
├── contracts/                Shared JSON Schema contracts
├── supabase/                 Migrations, views, seed data
├── docs/                     Architecture, policy, and contract documentation
└── .github/workflows/        CI (not yet configured)
```

## Team workstreams

1. **Supabase database and integration** — schema design, migrations, and the repository layer in `backend/src/trendbaker/repositories/`.
2. **YouTube API data collection** — the collector in `backend/src/trendbaker/collectors/youtube.py`.
3. **Next.js dashboard** — `frontend/`.
4. **Trend scoring and entity extraction** — `backend/src/trendbaker/trend_engine/`.

All four workstreams share the contracts in `contracts/` — see [contracts/README.md](contracts/README.md) before changing them.

## Frontend setup

```
cd frontend
npm install
npm run dev      # start dev server
npm run lint     # ESLint
npm run build    # production build
```

## Backend setup

```
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash; use .venv/bin/activate on macOS/Linux
pip install -e ".[dev]"

python -m pytest         # tests
python -m ruff check .   # lint
uvicorn trendbaker.api.main:app --reload   # run the API locally
```

## Environment variables

Copy `.env.example` to `.env` and fill in real values locally. Never commit `.env`. `SUPABASE_SERVICE_ROLE_KEY` and `YOUTUBE_API_KEY` are server-side secrets and must never be exposed to frontend code or via `NEXT_PUBLIC_*` variables — see the comments in `.env.example` for details. Features that depend on a missing setting fail with a clear configuration error at the point of use rather than at startup.

## Chatbot / MCP rule

Chatbot and MCP (AI assistant tool access) development was implemted **after** the data pipeline — collection → normalized-content → Supabase → scoring → trend-summary → dashboard — was working end to end with real data.
