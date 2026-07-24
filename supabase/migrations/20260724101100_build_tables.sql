-- ============================================================
--  TrendBaker schema (Supabase / Postgres)
--  Model: documents (items) -> mentions (item_terms) -> rollup (term_week_stats)
-- ============================================================

-- ---------- 1. terms : the taxonomy as a dimension table ----------
-- One row per canonical concept. `categories` is an array because a term
-- can legitimately be several things (dubai chocolate = format AND flavour).
create table if not exists terms (
    id          bigint generated always as identity primary key,
    slug        text unique not null,          -- 'dubai_chocolate' (canonical key)
    label       text not null,                 -- 'Dubai chocolate' (display)
    categories  text[] not null default '{}',  -- {format,flavour}
    created_at  timestamptz not null default now()
);

-- ---------- 2. items : one row per collected piece of content ----------
-- A YouTube video today; a blog post or retail product later. Same table,
-- different `source`. That single fact is what lets us later compare
-- "consumer buzz" (youtube/blog) against "market adoption" (retailer).
create table if not exists items (
    id             uuid primary key default gen_random_uuid(),
    source         text not null,              -- youtube | blog | retailer
    source_id      text not null,              -- video id / url / sku
    url            text,
    title          text,
    body           text,                       -- description / article / product copy
    author         text,                       -- channel / blog / brand
    published_at   timestamptz,
    region         text,                        -- ISO code, or null = unscoped/global
    views          bigint default 0,
    likes          bigint default 0,
    comments_count bigint default 0,
    sentiment      numeric,                     -- optional: -1..1 from enrichment pass
    collected_at   timestamptz not null default now(),
    raw            jsonb,                       -- full original payload
    unique (source, source_id)                 -- idempotent upserts
);

create index if not exists items_published_idx on items (published_at);
create index if not exists items_source_idx     on items (source);
create index if not exists items_region_idx     on items (region);

-- ---------- 3. item_terms : the mention fact table (many-to-many) ----------
-- This is where the collector's `matched_terms` gets normalized. Grain is
-- (item, term, category) — matching the collector's output exactly, so a
-- video tagged dubai chocolate under both 'format' and 'flavour' is 2 rows.
create table if not exists item_terms (
    item_id   uuid   not null references items(id) on delete cascade,
    term_id   bigint not null references terms(id),
    category  text   not null,                 -- format | flavour | ingredient | dietary
    primary key (item_id, term_id, category)
);

create index if not exists item_terms_term_idx on item_terms (term_id, category);

-- ---------- 4. term_week_stats : the rollup that powers every insight ----------
-- Weekly grain smooths the spikiness of social data. Refresh on a schedule
-- (Supabase cron / pg_cron) after each collection run.
create materialized view if not exists term_week_stats as
select
    it.term_id,
    it.category,
    i.source,
    i.region,
    date_trunc('week', i.published_at)          as week,
    count(distinct i.id)                        as item_count,
    count(distinct i.author)                    as creator_count,   -- competitive breadth
    sum(i.views)                                as total_views,
    sum(i.likes)                                as total_likes,
    sum(i.comments_count)                       as total_comments,
    avg(i.sentiment)                            as avg_sentiment
from item_terms it
join items i on i.id = it.item_id
where i.published_at is not null
group by it.term_id, it.category, i.source, i.region,
         date_trunc('week', i.published_at);

create index if not exists tws_term_idx on term_week_stats (term_id, category, week);

-- Refresh after ingestion (run directly, or via the RPC below):
--   refresh materialized view term_week_stats;

-- Callable from the loader with supabase.rpc('refresh_term_week_stats').
create or replace function refresh_term_week_stats()
returns void
language sql
as $$
    refresh materialized view term_week_stats;
$$;