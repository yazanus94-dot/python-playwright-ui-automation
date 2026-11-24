"""Entry point for the ShopEase FastAPI system under test."""

from app.store import app, application

__all__ = ["app", "application"]


if __name__ == "__main__":
    import os

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        log_level="warning",
    )
