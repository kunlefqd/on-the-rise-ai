"""Supabase repository.

Single point of access for reading content and derived data from the
Supabase Postgres database. Individual features (collectors, the trend
engine) should go through this rather than creating their own client.
"""

from __future__ import annotations

from typing import Any

from supabase import Client, create_client

from trendbaker.config import settings

DEFAULT_PAGE_SIZE = 1000


class SupabaseRepository:
    """Repository for Supabase-backed reads and writes."""

    def __init__(self) -> None:
        self._client: Client | None = None

    def _get_client(self) -> Client:
        settings.require("supabase_url", "supabase_service_role_key")
        if self._client is None:
            self._client = create_client(
                settings.supabase_url, settings.supabase_service_role_key
            )
        return self._client

    def fetch_all(
        self, table: str, select: str = "*", page_size: int = DEFAULT_PAGE_SIZE
    ) -> list[dict[str, Any]]:
        """Fetch every row from `table`, paginating in batches of `page_size`.

        `select` may use PostgREST's embedded-resource syntax (e.g.
        "item_id,category,terms(slug,label)") to pull a related table's
        columns in the same round trip.
        """
        client = self._get_client()
        rows: list[dict[str, Any]] = []
        start = 0
        while True:
            end = start + page_size - 1
            response = client.table(table).select(select).range(start, end).execute()
            batch = response.data
            rows.extend(batch)
            if len(batch) < page_size:
                break
            start += page_size
        return rows
