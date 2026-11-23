"""Environment-driven framework configuration."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5100")
TIMEOUT = int(os.getenv("TIMEOUT", "15000"))
BROWSER = os.getenv("BROWSER", "chromium")
HEADLESS = os.getenv("HEADLESS", "true").casefold() == "true"
ARTIFACTS = Path(os.getenv("ARTIFACTS_DIR", "artifacts"))
SCREENSHOTS = ARTIFACTS / "screenshots"
VIDEOS = ARTIFACTS / "videos"
ALLURE_RESULTS = Path(os.getenv("ALLURE_RESULTS_DIR", "allure-results"))
DEMO_EMAIL = os.getenv("DEMO_EMAIL", "demo@example.com")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "DemoPass123!")
