-- Migration: add term_leaderboard view
-- Depends on: term_week_stats (from schema.sql) — must already exist.
--
-- Apply with the Supabase CLI:
--   supabase migration new add_term_leaderboard
--   (paste this into the generated supabase/migrations/<timestamp>_add_term_leaderboard.sql)
--   supabase db push
--

create or replace view term_leaderboard as
select
    t.id                                                as term_id,
    t.label                                             as label,
    s.category                                          as category,
    sum(s.item_count)                                   as videos,
    sum(s.creator_count)                                as creators,
    coalesce(sum(s.total_views), 0)                     as views,
    coalesce(sum(s.total_likes), 0)                     as likes,
    coalesce(sum(s.total_comments), 0)                  as comments,
    coalesce(sum(s.total_likes + s.total_comments), 0)  as engagement
from term_week_stats s
join terms t on t.id = s.term_id
group by t.id, t.label, s.category;