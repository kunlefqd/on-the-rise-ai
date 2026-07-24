from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TrendCategory(str, Enum):
    format = "format"
    flavour = "flavour"
    ingredient = "ingredient"
    consumer_attribute = "consumer_attribute"


class Confidence(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TrendSummary(BaseModel):
    trend_name: str
    category: TrendCategory
    # term_leaderboard sums per-source scores (multi-source corroboration —
    # see supabase/migrations/20260724170701_add_trend_score.sql), so a term
    # trending on both youtube and blog can legitimately exceed 100.
    trend_score: float = Field(ge=0)
    growth_24h: float | None = None
    growth_7d: float | None = None
    confidence: Confidence
    confidence_score: float = Field(ge=0, le=100)
    supporting_video_count: int = Field(ge=0)
    supporting_blog_count: int = Field(ge=0, default=0)
    query_region_code: str
    last_updated: datetime
