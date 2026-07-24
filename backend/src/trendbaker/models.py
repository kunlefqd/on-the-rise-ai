"""Data models mirroring the Supabase/Postgres schema.

These Pydantic models mirror the tables defined in
``supabase/migrations/20260724101100_build_tables.sql`` (documented in
``docs/db-schema.md``): ``terms`` -> ``items`` -> ``item_terms``, plus a
read-only view of the ``term_week_stats`` materialized view.

Database-generated columns (``id``, ``created_at``, ``collected_at``) are
optional so the same model can be used to build a row for insertion (leave
them unset) and to parse a row read back from the database (they are present).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# Constrained vocabularies. `Source` distinguishes consumer buzz (youtube/blog)
# from market adoption (retailer). `Category` matches the collector's tag
# categories and the `item_terms.category` column.
Source = Literal["youtube", "blog", "retailer"]
Category = Literal["format", "flavour", "ingredient", "dietary"]


class Term(BaseModel):
    """A canonical concept (the taxonomy dimension). Maps to ``terms``."""

    model_config = ConfigDict(extra="ignore")

    id: int | None = None
    slug: str  # canonical key, e.g. 'dubai_chocolate'
    label: str  # display name, e.g. 'Dubai chocolate'
    categories: list[str] = Field(default_factory=list)  # e.g. ['format', 'flavour']
    created_at: datetime | None = None


class Item(BaseModel):
    """One collected piece of content. Maps to ``items``.

    Unique on ``(source, source_id)`` for idempotent upserts.
    """

    model_config = ConfigDict(extra="ignore")

    id: UUID | None = None
    source: Source
    source_id: str  # video id / url / sku
    url: str | None = None
    title: str | None = None
    body: str | None = None  # description / article / product copy
    author: str | None = None  # channel / blog / brand
    published_at: datetime | None = None
    region: str | None = None  # ISO code, or None = unscoped/global
    views: int = 0
    likes: int = 0
    comments_count: int = 0
    sentiment: float | None = None  # optional, -1..1 from enrichment pass
    collected_at: datetime | None = None
    raw: dict[str, Any] | None = None  # full original payload


class ItemTerm(BaseModel):
    """A single mention: one item tagged with one term under one category.

    Maps to ``item_terms``. Grain is ``(item_id, term_id, category)`` — an item
    tagged under both 'format' and 'flavour' is two rows.
    """

    model_config = ConfigDict(extra="ignore")

    item_id: UUID
    term_id: int
    category: Category


class TermWeekStat(BaseModel):
    """A weekly rollup row. Read-only view of the ``term_week_stats`` matview.

    Produced by ``refresh_term_week_stats()``; consumed by the trend engine and
    dashboard. Not intended for direct insertion.
    """

    model_config = ConfigDict(extra="ignore")

    term_id: int
    category: Category
    source: Source
    region: str | None = None
    week: datetime
    item_count: int
    creator_count: int  # distinct authors — competitive breadth
    total_views: int | None = None
    total_likes: int | None = None
    total_comments: int | None = None
    avg_sentiment: float | None = None
