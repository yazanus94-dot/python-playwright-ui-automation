"""Backward-compatible entry point for the ShopEase SUT."""

from app.store import app, app as application

__all__ = ["app", "application"]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
