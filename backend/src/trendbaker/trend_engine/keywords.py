"""Stage 2 -- join keywords to videos.

The keyword <-> video association already exists at the database level via
`item_terms` (linking `items` to `terms`), so this stage is a read + flatten
rather than a real join: fetch `item_terms` with its related `terms` row
embedded, and produce flat (keyword, item_id) pairs.

Output columns (one row per item-keyword link):
    item_id  : str
    term_id  : int
    keyword  : str   (terms.slug)
    label    : str   (terms.label, human-readable)
    category : str   (format | flavour | ingredient | consumer_attribute)
"""

from __future__ import annotations

import pandas as pd

from trendbaker.repositories.supabase_repository import SupabaseRepository

TABLE_NAME = "item_terms"
SELECT = "item_id,term_id,category,terms(slug,label)"

OUTPUT_COLUMNS = ["item_id", "term_id", "keyword", "label", "category"]


def clean_link(raw: dict) -> dict:
    """Cast one raw `item_terms` row (with embedded `terms`) into a flat link."""
    term = raw.get("terms") or {}
    return {
        "item_id": str(raw["item_id"]),
        "term_id": raw["term_id"],
        "keyword": term.get("slug", ""),
        "label": term.get("label", ""),
        "category": raw.get("category", ""),
    }


def fetch_keyword_links(repo: SupabaseRepository | None = None) -> pd.DataFrame:
    """Fetch + flatten every item<->term link. Returns a DataFrame with OUTPUT_COLUMNS."""
    repo = repo or SupabaseRepository()
    raw_rows = repo.fetch_all(TABLE_NAME, select=SELECT)
    records = [clean_link(row) for row in raw_rows]
    return pd.DataFrame(records, columns=OUTPUT_COLUMNS)


if __name__ == "__main__":
    df = fetch_keyword_links()
    print(f"Fetched {len(df)} item-keyword links")
    print(df.head())
