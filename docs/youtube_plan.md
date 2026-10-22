# YouTube Collector — Phase 1 Plan

The first data source for the TrendBaker pipeline. Goal: pull recent, public
baking content from YouTube, tag it against a bakery taxonomy, and land it in
Supabase as countable trend signals. Built on the **YouTube Data API v3** (not
scraping) so it's compliant with platform terms and stable over time.

This plan targets the existing backend package (`backend/src/trendbaker/`) and
the database defined in [`docs/db-schema.md`](../docs/db-schema.md). It does not
introduce standalone top-level scripts — it fills in modules that already exist.

---

## 1. Scope

**In scope for this phase**
- Search YouTube for baking content about baked goods, flavours, and ingredients.
- Normalize each video into the `Item` shape from `trendbaker.models`.
- Tag each video against the bakery taxonomy (format / flavour / ingredient / dietary).
- Persist to Supabase via `SupabaseRepository`, then refresh `term_week_stats`.

**Out of scope (later phases)**
- Blogs / recipe sites.
- Retailer and restaurant menus (needed later for the "market adoption" signal).
- Per-video metric history over time (see *Open Questions*).

---

## 2. Where the code lives (package layout)

Everything slots into the existing package — no new top-level scripts:

| Concern | Module | Status |
|---|---|---|
| API-access + normalize + tag | `trendbaker/collectors/youtube.py` (`YouTubeCollector.collect()`) | placeholder → implement |
| Collector interface | `trendbaker/collectors/base.py` (`Collector`) | exists |
| DB-facing models | `trendbaker/models.py` (`Item`, `Term`, `ItemTerm`) | exists |
| Persistence | `trendbaker/repositories/supabase_repository.py` | exists (`upsert_*`, `insert_item_terms`, `refresh_term_week_stats`) |
| Settings / secrets | `trendbaker/config.py` (`settings`) | exists (`youtube_api_key`, `supabase_*`) |
| Bakery taxonomy | `trendbaker/taxonomy.py` | **to add** — term list per category |
| CLI runner | `trendbaker/cli.py` + `console_scripts` entry in `pyproject.toml` | **to add** |

---

## 3. Prerequisites

1. **YouTube Data API v3 key**
   - Google Cloud Console → create/select a project.
   - APIs & Services → Library → enable *YouTube Data API v3*.
   - Credentials → Create credentials → API key.
   - (Optional) restrict the key to *YouTube Data API v3*. Do **not** add an
     HTTP-referrer restriction — this runs server-side, not in a browser.
2. **Environment.** Secrets are read by `trendbaker.config.settings` from the
   process env or a `.env` file — never hard-coded. Install the package (the
   repo uses `pyproject.toml`, not `requirements.txt`):
   ```bash
   cd backend
   python3 -m venv .venv && source .venv/bin/activate
   pip install -e ".[dev]"
   export YOUTUBE_API_KEY="AIza..."
   export SUPABASE_URL="https://<ref>.supabase.co"
   export SUPABASE_SERVICE_ROLE_KEY="..."     # loader only
   ```
   `settings.require("youtube_api_key")` (already in the collector) fails fast
   with a clear message if the key is unset.

---

## 4. Data flow

```
queries ──▶ search.list ──▶ video IDs ──▶ videos.list ──▶ raw videos
                                                              │
                                                     normalize + tag
                                                              │
                                                              ▼
                                         CollectedRecord(Item, [TagMatch])
                                                              │
                                                   SupabaseRepository
                                                              │
                                                              ▼
                                            terms · items · item_terms
                                                              │
                                              refresh_term_week_stats()
```

### Step by step

1. **Build queries.** With no `--queries` override, the collector crosses the
   first 6 formats and 6 flavours from `taxonomy.py` with the modifiers `recipe`
   and `trend` (24 queries, e.g. `"dubai chocolate recipe"`, `"pistachio trend"`).
2. **Search.** `search.list` runs per query with `type=video`, `part=id`,
   `publishedAfter` (from `--days`), `order`, and optional `regionCode`. Returns
   video IDs only — deliberately thin, because search is the expensive call.
3. **Hydrate.** Video IDs go to `videos.list` in batches of 50, pulling
   `snippet,statistics` (title, description, channel, tags, view/like/comment
   counts, publish date).
4. **Normalize + tag.** Each raw video maps to a `trendbaker.models.Item` (field
   mapping in §6), with statistics cast to `int`. Taxonomy matching scans
   title/description/tags and yields a list of `TagMatch(term_slug, label,
   category)`. Duplicates dropped by video ID.
5. **Persist** (loader step, §7) via `SupabaseRepository` — no JSONL step is
   required. An optional `--dump data/youtube_trends.jsonl` writes records to a
   gitignored file for debugging/evidence only.

---

## 5. Configuration knobs

CLI flags on the runner (`trendbaker.cli`); the API key comes from `settings`,
never a flag:

| Flag | Default | Purpose |
|------|---------|---------|
| `--queries` | 24 auto-generated | Override the search set entirely |
| `--days` | 30 | Only videos published within this window count as a signal |
| `--max-per-query` | 50 | Video results per query (API page max is 50) |
| `--order` | `relevance` | `relevance` / `date` / `viewCount` / `rating` |
| `--regions` | *(none → global)* | ISO codes to bias search; omit for an unscoped pass |
| `--with-comments` | off | Fetch top comments (adds quota cost + PII — see §10) |
| `--dump` | *(off)* | Optional JSONL debug artifact path |

### Order strategy
Run the same queries under different sort orders to catch different signals:
- `date` — freshest uploads → *what's just emerging*.
- `viewCount` — highest views → *what's already exploding*.
- `relevance` — balanced general pass.

Note: each extra order re-runs the full search set, **tripling** search quota
(see §8).

---

## 6. Record shape (mapping YouTube → `models.Item`)

The collector's normalized unit is a `trendbaker.models.Item` plus its matched
taxonomy tags. There is **no separate ad-hoc JSON shape** — the model *is* the
contract, and it maps 1:1 to the `items` table in `docs/db-schema.md`.

| YouTube API field | `Item` field | Notes |
|---|---|---|
| video `id` | `source_id` | `source` is the constant `"youtube"` |
| `snippet.title` | `title` | |
| `snippet.description` | `body` | (not `text`) |
| `snippet.channelTitle` | `author` | feeds `creator_count` in the rollup |
| `snippet.publishedAt` | `published_at` | ISO-8601 |
| `statistics.viewCount` | `views` | cast to `int`, default 0 |
| `statistics.likeCount` | `likes` | cast to `int`, default 0 |
| `statistics.commentCount` | `comments_count` | cast to `int`, default 0 |
| — | `region` | the queried region, or `null` for a global pass |
| — | `url` | `https://www.youtube.com/watch?v=<id>` |
| trimmed payload | `raw` | see §10 — store only fields we may need, not the whole blob |
| *(later, enrichment)* | `sentiment` | left `null` in Phase 1 |

`id`, `collected_at` are left unset so Postgres defaults (`gen_random_uuid()`,
`now()`) apply. Matched tags become `Term` + `ItemTerm` rows; the four
categories are the singular DB values: `format`, `flavour`, `ingredient`,
`dietary`.

> **Relationship to `contracts/normalized-content.schema.json`.** That contract
> is a deliberately minimal interchange subset and does **not** include `author`
> or matched tags, which the DB and the `creator_count` signal require. Phase 1
> therefore treats the `models` types as the internal source of truth. If a
> contract-validated boundary is later needed, extend the contract (per
> `contracts/README.md`) to add `author` — do not silently emit fields the
> contract forbids (`additionalProperties: false`).

---

## 7. Loading into Supabase

The loader is `SupabaseRepository` (no standalone `load_to_supabase.py`). The
ID-mapping order matters because `item_terms` needs generated IDs:

1. `upsert_terms(terms)` — dedupes on `slug`; use the returned rows to build a
   `slug → id` map.
2. `upsert_items(items)` — dedupes on `(source, source_id)` (idempotent
   re-runs); use returned rows to build a `(source, source_id) → id` map.
3. `insert_item_terms(item_terms)` — builds rows from the two maps; idempotent
   via `ignore_duplicates` on the composite PK.
4. `refresh_term_week_stats()` — rebuild the rollup once per batch.
5. Read back with `fetch_term_week_stats()` to sanity-check.

> **Append-only caveat.** `insert_item_terms` never *removes* tags. If a re-run
> re-tags a video with fewer terms, stale `item_terms` rows remain. Phase 1
> accepts this; a true resync (delete by `item_id`, then re-insert) is a
> follow-up if tagging logic changes frequently (see §11).

---

## 8. Quota planning

Daily budget defaults to **10,000 units**.

| Call | Cost | Notes |
|------|------|-------|
| `search.list` | 100 | The bottleneck — one per query per region per order per page |
| `videos.list` | 1 | Batched 50 IDs/call |
| `commentThreads.list` | 1 | Per video, only with `--with-comments` |

**Default run estimate** (relevance only, no region, no comments):
24 searches (2,400) + up to ~24 hydrate calls (24) ≈ **~2,424 units**.

**Multipliers compound — watch the ceiling:**
- Regions: `--regions US GB CA` ≈ ×3 search cost (~7,200).
- Orders: running date + viewCount + relevance ≈ ×3.
- Combined (3 regions × 3 orders) ≈ **~21,600 units — over the 10k budget.**
- Comments add ~1 unit per video, scaling fast across ~1,200 videos.

---

## 9. Running it

**Connectivity check first** (cheap — 1 search + 1 hydrate):
```bash
trendbaker-collect --queries "dubai chocolate croissant" --max-per-query 10 --dry-run
```
`--dry-run` normalizes and prints a term summary without writing to Supabase.

**Full default run + load:**
```bash
trendbaker-collect --source youtube
```
(`trendbaker-collect` is the `console_scripts` entry backed by `trendbaker.cli`.)

---

## 10. Ethical-data-policy checklist

Reviewed against [`docs/ethical-data-policy.md`](../docs/ethical-data-policy.md)
before making real requests:

- ✅ **Official API only** (Data API v3) — no scraping, no quota workarounds.
- ✅ **Store source URL** for every item (`Item.url`).
- ⚠️ **Trim `raw`.** The policy says store only what trend analysis needs — do
  **not** persist the entire API payload. Keep a minimal subset (or drop `raw`).
- ⚠️ **Comments = PII.** `--with-comments` collects commenter text; keep it off
  unless sentiment analysis is planned, and avoid storing commenter identities.
- ⚠️ **Source must be independently disable-able.** Add a settings flag (e.g.
  `youtube_enabled`) so this source can be turned off without touching others.
- ✅ **No private/gated content**; public search results only.

---

## 11. Error handling

| Error | Cause | Handling |
|-------|-------|----------|
| `403 accessNotConfigured` | API not enabled on the project | **Fail fast** — enable Data API v3; do not retry |
| `400 keyInvalid` ("API key not valid") | Wrong/mistyped key or env not exported | **Fail fast** — re-check `YOUTUBE_API_KEY` |
| `403 quotaExceeded` | Daily quota spent | **Fail fast** — won't recover until midnight Pacific |
| `403 rateLimitExceeded` / `userRateLimitExceeded` | Short-term rate cap | **Retry** with exponential backoff |
| `429` / transient `5xx` | Throttling / server blip | **Retry** with exponential backoff |

Only rate-limit and transient errors are retried — retrying `quotaExceeded` or
config/key errors just burns time and never succeeds. Comment fetches fail soft
(return empty) when comments are disabled on a video.

---

## 12. Open questions / known limits

- **Metric history.** `items` stores only the *latest* views/likes/comments per
  video (upsert overwrites). Growth is measured via `published_at` bucketing,
  not per-video velocity — so a months-old video going viral now is not captured.
  Add an append-only `item_metrics` snapshot table if true velocity is needed.
- **Stale tags on re-run.** `insert_item_terms` is append-only (§7). If tagging
  changes, add a resync path.
- **`regionCode` biases, not filters.** It nudges search ranking toward a region
  but does not guarantee region-of-origin; treat stored `region` accordingly and
  default to `null` (global) unless a region pass is explicit.
- **Search recall.** Results depend on query phrasing; the default query set is
  intentionally small to conserve quota. Expand `--queries` deliberately.

---

## 13. Definition of done for this phase

- [ ] `taxonomy.py` and `trendbaker.cli` added; `trendbaker-collect` entry point wired in `pyproject.toml`.
- [ ] API key working; `--dry-run` connectivity check passes and prints a term summary.
- [ ] `YouTubeCollector.collect()` returns records mapping cleanly to `models.Item` + tags.
- [ ] Full default run persists via `SupabaseRepository` — `terms`, `items`, `item_terms` populated with no duplicates on re-run.
- [ ] `refresh_term_week_stats()` runs and `fetch_term_week_stats()` returns rows.
- [ ] Ethical checklist (§10) satisfied — `raw` trimmed, comments off by default, source disable-able.
