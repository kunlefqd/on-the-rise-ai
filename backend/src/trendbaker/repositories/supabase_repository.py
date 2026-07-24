"""Supabase repository.

PLACEHOLDER — not yet implemented.

This will be the single point of access for reading and writing normalized
content and trend summaries in the Supabase Postgres database. No tables
exist yet and no database requests are made here.
"""

from __future__ import annotations

from supabase import Client, create_client

from trendbaker.config import settings


class SupabaseRepository:
    """Placeholder repository for Supabase-backed persistence."""

    def __init__(self) -> None:
        self._client: Client | None = None

    def _get_client(self) -> Client:
        settings.require("supabase_url", "supabase_service_role_key")
        if self._client is None:
            self._client = create_client(
                settings.supabase_url, settings.supabase_service_role_key
            )
        return self._client
