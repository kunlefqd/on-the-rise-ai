"""Stage 1 -- ingest & clean.

Reads rows from Supabase's `items` table and produces a flat, typed
DataFrame. This is the only stage that talks to Supabase or knows about
the `items` table's column names -- every later stage consumes the
DataFrame this returns and does not care where it came from.

`views` / `likes` / `comments_count` are already integers in `items`, but
we still coerce defensively here so this stage stays correct even if that
ever changes upstream.

Output columns (one row per item):
    item_id      : str
    published_at : pandas.Timestamp (UTC)
    title        : str
    body         : str
    views        : int
    likes        : int
    comments     : int
"""

from __future__ import annotations

import pandas as pd

from trendbaker.repositories.supabase_repository import SupabaseRepository

TABLE_NAME = "items"

OUTPUT_COLUMNS = ["item_id", "published_at", "title", "body", "views", "likes", "comments"]


def _to_int(value: object) -> int:
    if value is None or value == "":
        return 0
    return int(value)


def clean_item(raw: dict) -> dict:
    """Cast one raw `items` row into the canonical flat-record shape."""
    return {
        "item_id": str(raw["id"]),
        "published_at": pd.to_datetime(raw["published_at"], utc=True),
        "title": raw.get("title") or "",
        "body": raw.get("body") or "",
        "views": _to_int(raw.get("views")),
        "likes": _to_int(raw.get("likes")),
        "comments": _to_int(raw.get("comments_count")),
    }


def ingest_items(repo: SupabaseRepository | None = None) -> pd.DataFrame:
    """Fetch + clean every row in `items`. Returns a DataFrame with OUTPUT_COLUMNS."""
    repo = repo or SupabaseRepository()
    raw_rows = repo.fetch_all(TABLE_NAME)
    records = [clean_item(row) for row in raw_rows]
    return pd.DataFrame(records, columns=OUTPUT_COLUMNS)


if __name__ == "__main__":
    df = ingest_items()
    print(f"Ingested {len(df)} items")
    print(df.head())
