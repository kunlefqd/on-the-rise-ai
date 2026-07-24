from pydantic import BaseModel


class SupportingItem(BaseModel):
    source: str  # youtube | blog | retailer
    title: str
    author: str  # channel / blog / brand
    url: str
    published_at: str
    view_count: int | None = None
    like_count: int | None = None
    comment_count: int | None = None
    evidence_reason: str


class TrendDetail(BaseModel):
    trend_name: str
    summary: str
    suggested_rd_opportunity: str
    supporting_items: list[SupportingItem]
