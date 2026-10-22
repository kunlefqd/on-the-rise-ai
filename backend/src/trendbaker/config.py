"""Application settings.

Settings are loaded from environment variables (see .env.example at the repo
root). Values are optional at import time so the app can start without every
integration configured; individual features must call `require()` for the
settings they actually need and will fail with a clear error otherwise.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# The backend directory, resolved from this file so config loads regardless of
# the current working directory: config.py -> trendbaker -> src -> backend.
_BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # Later files win, so `.env.local` (optional local overrides) beats `.env`
    # (the shared backend env). Real process env vars still take precedence over
    # both. Frontend/Next.js keys live in `frontend/.env.local`, not here.
    model_config = SettingsConfigDict(
        env_file=(_BACKEND_DIR / ".env", _BACKEND_DIR / ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"

    supabase_url: str | None = None
    supabase_service_role_key: str | None = None

    youtube_api_key: str | None = None

    def require(self, *field_names: str) -> None:
        """Raise a clear error if any of the named settings are unset.

        Call this at the start of a feature (e.g. a collector or repository
        method) that depends on external configuration, rather than at import
        time, so the app can boot without every integration configured.
        """
        missing = [name for name in field_names if getattr(self, name, None) in (None, "")]
        if missing:
            raise RuntimeError(
                "Missing required settings: "
                f"{', '.join(missing)}. Set them in your environment or .env file."
            )


settings = Settings()
