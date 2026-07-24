"""Application settings.

Settings are loaded from environment variables (see .env.example at the repo
root). Values are optional at import time so the app can start without every
integration configured; individual features must call `require()` for the
settings they actually need and will fail with a clear error otherwise.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

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
