-- Migration: trend scoring
--   1. term_trend_scores : per (term, category, SOURCE) score, normalized
--      against other terms in the SAME source (log-scaled min-max, weighted).
--   2. term_leaderboard  : rebuilt to carry a trend_score column.
--
-- Weights (tune to taste; must sum to 1):
--   views 0.4  · engagement 0.4  · mentions/videos 0.2

create or replace view term_trend_scores as
with per_source as (
    -- collapse week/region: one row per term+category+source
    select
        s.term_id,
        t.label,
        s.category,
        s.source,
        sum(s.item_count)                                   as videos,
        sum(s.creator_count)                                as creators,
        coalesce(sum(s.total_views), 0)                     as views,
        coalesce(sum(s.total_likes), 0)                     as likes,
        coalesce(sum(s.total_comments), 0)                  as comments,
        coalesce(sum(s.total_likes + s.total_comments), 0)  as engagement
    from term_week_stats s
    join terms t on t.id = s.term_id
    group by s.term_id, t.label, s.category, s.source
),
bounds as (
    -- log-scale each metric, and find each source's min/max for normalization
    select
        p.*,
        ln(1 + views)      as l_views,
        ln(1 + engagement) as l_eng,
        ln(1 + videos)     as l_vids,
        min(ln(1 + views))      over (partition by source) as min_v,
        max(ln(1 + views))      over (partition by source) as max_v,
        min(ln(1 + engagement)) over (partition by source) as min_e,
        max(ln(1 + engagement)) over (partition by source) as max_e,
        min(ln(1 + videos))     over (partition by source) as min_m,
        max(ln(1 + videos))     over (partition by source) as max_m
    from per_source p
),
scored as (
    -- normalize 0..1 within source; if a source has one term (min=max), give 1
    select
        term_id, label, category, source,
        videos, creators, views, likes, comments, engagement,
        case when max_v = min_v then 1 else (l_views - min_v) / (max_v - min_v) end as n_views,
        case when max_e = min_e then 1 else (l_eng   - min_e) / (max_e - min_e) end as n_eng,
        case when max_m = min_m then 1 else (l_vids  - min_m) / (max_m - min_m) end as n_vids
    from bounds
)
select
    term_id, label, category, source,
    videos, creators, views, likes, comments, engagement,
    round(100 * (0.4 * n_views + 0.4 * n_eng + 0.2 * n_vids), 1) as trend_score
from scored;


-- Rebuild the leaderboard with the score. Summing per-source scores means a
-- term trending across MULTIPLE sources scores higher (multi-source
-- corroboration). With one source today it's just that source's 0..100 score.
-- To cap at 0..100 instead, swap sum(trend_score) for avg(trend_score).
create or replace view term_leaderboard as
select
    term_id,
    label,
    category,
    sum(videos)                 as videos,
    sum(creators)               as creators,
    sum(views)                  as views,
    sum(likes)                  as likes,
    sum(comments)               as comments,
    sum(engagement)             as engagement,
    round(sum(trend_score), 1)  as trend_score
from term_trend_scores
group by term_id, label, category;