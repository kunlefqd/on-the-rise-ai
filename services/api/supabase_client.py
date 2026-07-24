"""Thin Supabase REST (PostgREST) client, service-role key only.

Server-side use only — never expose SUPABASE_SERVICE_ROLE_KEY to the
frontend. Fails at the point of use with a clear error if config is
missing, matching the convention described in the repo root README.
"""

import os

import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")


def _headers() -> dict[str, str]:
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set "
            "(services/api/.env) to query trend data."
        )
    return {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    }


def rest_get(path: str, params: dict[str, str]) -> list[dict]:
    response = httpx.get(
        f"{SUPABASE_URL}/rest/v1/{path}",
        headers=_headers(),
        params=params,
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()
