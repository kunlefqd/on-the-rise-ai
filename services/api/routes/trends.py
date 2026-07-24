from collections import defaultdict
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from services.api.models.trend_detail import SupportingItem, TrendDetail
from services.api.models.trend_summary import Confidence, TrendCategory, TrendSummary
from services.api.supabase_client import rest_get

router = APIRouter(prefix="/api/v1/trends", tags=["trends"])

# DB categories are format | flavour | ingredient | dietary; the API
# contract's fourth bucket is named consumer_attribute. Everything else
# passes through unchanged. Unmapped/unexpected category values are
# dropped rather than guessed into a bucket.
_CATEGORY_MAP: dict[str, TrendCategory] = {
    "format": TrendCategory.format,
    "flavour": TrendCategory.flavour,
    "ingredient": TrendCategory.ingredient,
    "dietary": TrendCategory.consumer_attribute,
}


def _confidence_from_breadth(creators: int, videos: int) -> tuple[Confidence, float]:
    # Placeholder pending a real confidence formula from the trend-scoring
    # workstream (see docs/trend-scoring.md — still provisional as of
    # 2026-07-24). creators/videos are the only breadth signals currently
    # exposed by term_leaderboard.
    score = min(100.0, creators * 15 + videos * 5)
    if score >= 70:
        level = Confidence.high
    elif score >= 40:
        level = Confidence.medium
    else:
        level = Confidence.low
    return level, score


def _latest_collected_at() -> datetime:
    rows = rest_get(
        "items",
        {"select": "collected_at", "order": "collected_at.desc", "limit": "1"},
    )
    if not rows or not rows[0].get("collected_at"):
        return datetime.now(timezone.utc)
    return datetime.fromisoformat(rows[0]["collected_at"])


@router.get("", response_model=list[TrendSummary])
def list_trends(
    region: str | None = Query(default=None, description="Region code filter, e.g. CA"),
    limit: int | None = Query(default=None, ge=1, description="Max number of trends to return"),
) -> list[TrendSummary]:
    params: dict[str, str] = {
        "select": "term_id,label,category,videos,creators,trend_score",
        "order": "trend_score.desc",
    }
    if limit is not None:
        params["limit"] = str(limit)

    rows = rest_get("term_leaderboard", params)
    last_updated = _latest_collected_at()

    # term_leaderboard's `videos` is summed across every source (youtube +
    # blog + ...). term_trend_scores keeps the per-source grain, so pull that
    # separately to split "supporting videos" from "supporting blog posts".
    source_rows = rest_get(
        "term_trend_scores", {"select": "term_id,category,source,videos"}
    )
    counts_by_term: dict[tuple[int, str], dict[str, int]] = defaultdict(dict)
    for source_row in source_rows:
        key = (source_row["term_id"], source_row["category"])
        counts_by_term[key][source_row["source"]] = source_row["videos"]

    results: list[TrendSummary] = []
    for row in rows:
        category = _CATEGORY_MAP.get(row["category"])
        if category is None:
            continue
        confidence, confidence_score = _confidence_from_breadth(row["creators"], row["videos"])
        source_counts = counts_by_term.get((row["term_id"], row["category"]), {})
        results.append(
            TrendSummary(
                trend_name=row["label"],
                category=category,
                trend_score=row["trend_score"],
                # Not yet computable from the DB (no per-window snapshots) —
                # see docs/trend-scoring.md. Never guessed.
                growth_24h=None,
                growth_7d=None,
                confidence=confidence,
                confidence_score=confidence_score,
                supporting_video_count=source_counts.get("youtube", 0),
                supporting_blog_count=source_counts.get("blog", 0),
                # term_leaderboard is not region-segmented yet; echo back what
                # was requested rather than inferring a region from the data.
                query_region_code=region or "global",
                last_updated=last_updated,
            )
        )
    return results


@router.get("/{trend_name}", response_model=TrendDetail)
def get_trend_detail(trend_name: str) -> TrendDetail:
    leaderboard_rows = rest_get(
        "term_leaderboard",
        {
            "label": f"ilike.{trend_name}",
            "select": "term_id,label,category,videos,creators,trend_score",
        },
    )
    if not leaderboard_rows:
        raise HTTPException(status_code=404, detail=f"Trend '{trend_name}' not found")
    term = leaderboard_rows[0]

    item_rows = rest_get(
        "item_terms",
        {
            "term_id": f"eq.{term['term_id']}",
            "select": "items(source,title,author,url,published_at,views,likes,comments_count)",
        },
    )

    supporting_items: list[SupportingItem] = []
    for row in item_rows:
        item = row.get("items")
        if not item:
            continue
        views, likes, comments = item.get("views"), item.get("likes"), item.get("comments_count")
        supporting_items.append(
            SupportingItem(
                source=item.get("source") or "youtube",
                title=item.get("title") or "Untitled",
                author=item.get("author") or "Unknown source",
                url=item.get("url") or "",
                published_at=item.get("published_at") or "",
                view_count=views,
                like_count=likes,
                comment_count=comments,
                evidence_reason=(
                    f"{views if views is not None else 'unknown'} views, "
                    f"{likes if likes is not None else 'unknown'} likes, "
                    f"{comments if comments is not None else 'unknown'} comments"
                ),
            )
        )

    summary = (
        f"'{term['label']}' appears in {term['videos']} supporting item(s) (video "
        f"or blog) from {term['creators']} distinct source(s), with a current "
        f"trend score of {term['trend_score']}."
    )
    suggested_rd_opportunity = (
        "R&D opportunity scoring is not yet generated from real data — review "
        "the supporting evidence below manually."
    )

    return TrendDetail(
        trend_name=term["label"],
        summary=summary,
        suggested_rd_opportunity=suggested_rd_opportunity,
        supporting_items=supporting_items,
    )
