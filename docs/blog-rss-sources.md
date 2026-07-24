# Blog/RSS sources

Blog/RSS is TrendBaker AI's second signal-source type, alongside YouTube. This page documents the MVP approach, the source list, and the ethical rules behind it.

## MVP approach

RSS/Atom feeds only. No HTML scraping, no headless browsers, no bypassing paywalls, logins, CAPTCHAs, or bot controls. Every configured source is tracked in `public.blog_sources` with a `compliance_status` (`approved` / `review_required` / `disabled`) so a source can be reviewed before it's ever polled, and disabled independently without losing its history.

## First three enabled sources (`compliance_status = approved`)

| Source | Website | Feed |
|---|---|---|
| King Arthur Baking Blog | https://www.kingarthurbaking.com | https://www.kingarthurbaking.com/blog/feed |
| Food Dive | https://www.fooddive.com | https://www.fooddive.com/feeds/news/ |
| The Kitchn | https://www.thekitchn.com | https://www.thekitchn.com/main.rss |

These three were chosen because their feeds were confirmed reachable and valid RSS during evaluation, with no paywall, login, or CAPTCHA in front of the feed itself.

## Backlog sources (require verification before enabling)

These are candidates for a later wave, not enabled in the MVP seed. Each needs a human to confirm the exact feed URL and re-check `robots.txt` from the actual collector environment before being marked `approved`:

- Baking Business (bakingbusiness.com) — bakery/grain-industry trade news
- Food Business News (foodbusinessnews.net) — broader food-industry trade news
- Snack Food & Wholesale Bakery (snackandbakery.com) — bakery/snack product launches
- Bake Magazine (bakemag.com) — bakery-industry trade news; its `robots.txt` explicitly disallows some AI crawlers by name, so this one needs particular care over how a collector identifies itself
- British Baker (bakeryinfo.co.uk) — UK/international bakery trade news
- Serious Eats (seriouseats.com) — recipe/food-trend coverage; feed URL not independently confirmed yet

Reddit (e.g. r/Baking) was considered and is **not** on the backlog list — its 2023 API/data-use policy changes make automated use of even its public `.rss` endpoint legally murkier than a standard blog/trade-pub feed, so it's out of scope until that's resolved.

## Ethical rules

- RSS/Atom feeds only — no scraping of arbitrary blog HTML.
- No headless browsers.
- Never bypass paywalls, logins, CAPTCHAs, bot controls, or robots restrictions.
- No private content.
- Any source can be individually disabled (`BlogSource.enabled` in `backend/src/trendbaker/collectors/blog_rss.py`) without deleting its collected history.

## Storage: the shared `items` schema, not a dedicated Blog/RSS schema

Blog/RSS does not have its own database tables. It stores rows in the same shared schema YouTube uses (`supabase/migrations/20260724101100_build_tables.sql`, see [docs/db-schema.md](db-schema.md)): `items` (one row per article, `source = 'blog'`), `item_terms` (trend mentions, once an extractor exists), and `term_week_stats` (the weekly rollup, shared across all sources).

Source configuration (name, website/feed URL, enabled flag) lives in code for the MVP — `BLOG_SOURCES` in `backend/src/trendbaker/collectors/blog_rss.py` — not in the database, since the shared schema has no dedicated sources-registry table. Setting a source's `enabled` to `False` there disables it without touching collected history.

## What is stored (in `items`, per article)

- `source = 'blog'`, `author` = the publication name (e.g. "King Arthur Baking Blog" — the shared schema's `author` column is documented as "channel / blog / brand", not a personal byline)
- `title`, `url` (the article's own URL), `published_at`, `collected_at`
- `body` = a short feed-provided excerpt/summary only, capped at 1000 characters
- `source_id` = the feed's own guid when available, otherwise a deterministic hash of the article URL
- `views`/`likes`/`comments_count` are always `null` for Blog/RSS rows — see below
- Source URLs are always retained for attribution and evidence

## What is not stored

- Full article bodies — only a short excerpt/feed summary, length-capped
- Comment text, comment authors, or any private/gated content
- Views, likes, comments, or shares — see below

## Why no views, likes, comments, or shares

RSS/Atom feeds don't reliably expose engagement metrics the way the YouTube Data API does. Rather than fake or approximate these numbers, the Blog/RSS contract and schema simply omit them. Blog/RSS trend scoring (`public.blog_trend_scores`) is based on **article volume, source diversity, recency, and novelty** instead — see [docs/trend-scoring.md](trend-scoring.md).

## How Blog/RSS complements YouTube

YouTube signals consumer/creator attention (what people are making and watching). Blog/RSS signals editorial and industry attention (what food writers and trade publications are covering, including B2B product launches). A trend confirmed by both a YouTube video and an independent blog/trade article in the same window is stronger evidence than either alone — this is exactly the "cross-source confirmation" scoring category already planned in `docs/trend-scoring.md`. Both source types are rows in the same shared `items` table (distinguished by `source`) and roll up through the same `term_week_stats` materialized view, so the dashboard can eventually show YouTube and blog evidence side by side under one trend term without needing a separate query path per source.
