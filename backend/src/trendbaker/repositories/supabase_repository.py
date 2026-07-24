"""Supabase repository.

The single point of access for reading and writing normalized content and
trend rollups in the Supabase Postgres database. Writes go to the tables
defined in ``supabase/migrations/20260724101100_build_tables.sql`` (see
``docs/db-schema.md``); models are defined in ``trendbaker.models``.

The repository speaks the model types from ``trendbaker.models`` at its
boundary and serializes them to JSON-safe dicts internally, so callers never
deal with raw dicts or PostgREST details.
"""

from __future__ import annotations

from typing import Any

from supabase import Client, create_client

from trendbaker.config import settings
from trendbaker.models import Item, ItemTerm, Term, TermWeekStat


class SupabaseRepository:
    """Repository for Supabase-backed persistence."""

    def __init__(self) -> None:
        self._client: Client | None = None

    def _get_client(self) -> Client:
        settings.require("supabase_url", "supabase_service_role_key")
        if self._client is None:
            self._client = create_client(
                settings.supabase_url, settings.supabase_service_role_key
            )
        return self._client

    # ---------- writes ----------

    def upsert_terms(self, terms: list[Term]) -> list[dict[str, Any]]:
        """Upsert taxonomy terms, deduplicating on ``slug``.

        Returns the stored rows (including the generated ``id`` for each term),
        so callers can map ``slug`` -> ``id`` before writing ``item_terms``.
        """
        if not terms:
            return []
        rows = [t.model_dump(mode="json", exclude_none=True) for t in terms]
        resp = (
            self._get_client()
            .table("terms")
            .upsert(rows, on_conflict="slug")
            .execute()
        )
        return resp.data or []

    def upsert_items(self, items: list[Item]) -> list[dict[str, Any]]:
        """Upsert collected content, deduplicating on ``(source, source_id)``.

        Idempotent: re-collecting the same content updates the existing row
        rather than inserting a duplicate. Returns the stored rows (including
        the generated ``id`` for each item).
        """
        if not items:
            return []
        rows = [i.model_dump(mode="json", exclude_none=True) for i in items]
        resp = (
            self._get_client()
            .table("items")
            .upsert(rows, on_conflict="source,source_id")
            .execute()
        )
        return resp.data or []

    def insert_item_terms(self, item_terms: list[ItemTerm]) -> list[dict[str, Any]]:
        """Insert mention rows, ignoring ones that already exist.

        Uses upsert with ``ignore_duplicates`` on the composite primary key
        ``(item_id, term_id, category)`` so re-running a collection pass does
        not error on rows already written.
        """
        if not item_terms:
            return []
        rows = [it.model_dump(mode="json") for it in item_terms]
        resp = (
            self._get_client()
            .table("item_terms")
            .upsert(
                rows,
                on_conflict="item_id,term_id,category",
                ignore_duplicates=True,
            )
            .execute()
        )
        return resp.data or []

    def refresh_term_week_stats(self) -> None:
        """Rebuild the ``term_week_stats`` materialized view.

        Call after an ingestion batch so downstream reads see fresh rollups.
        Delegates to the ``refresh_term_week_stats()`` SQL function/RPC.
        """
        self._get_client().rpc("refresh_term_week_stats").execute()

    def update_item_body(self, item_id: str, body: str | None) -> None:
        """Update only the `body` column of one `items` row, by id.

        Every other column is left untouched, since the update payload only
        ever contains `body`. Used to reprocess previously-stored rows (e.g.
        stripping HTML that predates a normalization fix) without disturbing
        anything else about them.
        """
        self._get_client().table("items").update({"body": body}).eq("id", item_id).execute()

    # ---------- reads ----------

    def get_items_by_source(
        self, source: str, fields: str = "id,body"
    ) -> list[dict[str, Any]]:
        """Read raw rows from `items` where source = `source`, selecting only `fields`.

        Returns raw dicts rather than parsed Item models, since this is a
        narrow column projection (e.g. just id+body for cleanup, or
        id+title+body for tagging) rather than a full row read — Item
        requires `source`, which a projection may omit.
        """
        resp = self._get_client().table("items").select(fields).eq("source", source).execute()
        return resp.data or []

    def get_terms(self) -> list[Term]:
        """Read all rows from `terms`, parsed into Term models."""
        resp = (
            self._get_client()
            .table("terms")
            .select("id,slug,label,categories,created_at")
            .execute()
        )
        return [Term.model_validate(row) for row in (resp.data or [])]

    def fetch_term_week_stats(self) -> list[TermWeekStat]:
        """Read the weekly rollups powering the trend engine and dashboard."""
        resp = self._get_client().table("term_week_stats").select("*").execute()
        return [TermWeekStat.model_validate(row) for row in (resp.data or [])]
