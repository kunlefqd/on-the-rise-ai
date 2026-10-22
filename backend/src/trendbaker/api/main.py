"""FastAPI application entrypoint."""

from fastapi import FastAPI

from trendbaker.config import settings

app = FastAPI(title="TrendBaker AI API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "app_env": settings.app_env}
