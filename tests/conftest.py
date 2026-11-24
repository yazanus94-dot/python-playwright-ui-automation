"""Fixtures: live SUT server, isolated browser contexts and failure evidence."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import time
from collections.abc import Generator, Iterator
from pathlib import Path

import allure
import pytest
import requests
from playwright.sync_api import Browser, BrowserContext, Page

ROOT = Path(__file__).resolve().parents[1]
WORKER = os.getenv("PYTEST_XDIST_WORKER", "")
WORKER_INDEX = int(WORKER[2:]) + 1 if re.fullmatch(r"gw\d+", WORKER) else 0
PORT = 5100 + WORKER_INDEX
EXTERNAL_SUT_URL = os.getenv("EXTERNAL_SUT_URL", "").rstrip("/")
BASE_URL = EXTERNAL_SUT_URL or f"http://127.0.0.1:{PORT}"


def pytest_configure(config: pytest.Config) -> None:
    os.environ["BASE_URL"] = BASE_URL
    os.environ["PORT"] = str(PORT)
    if os.getenv("BROWSER"):
        config.option.browser = [os.environ["BROWSER"]]


def _wait_for_health(url: str, process: subprocess.Popen[bytes] | None = None) -> None:
    deadline = time.time() + 60
    while time.time() < deadline:
        if process is not None and process.poll() is not None:
            raise RuntimeError("SUT process exited before becoming healthy")
        try:
            response = requests.get(f"{url}/health", timeout=2)
            if response.status_code == 200 and response.json().get("status") == "ok":
                return
        except requests.RequestException:
            time.sleep(0.2)
    raise RuntimeError(f"SUT did not become healthy at {url}")


@pytest.fixture(scope="session", autouse=True)
def live_server() -> Iterator[str]:
    """Provide a healthy SUT: either an external service or a local process."""
    if EXTERNAL_SUT_URL:
        _wait_for_health(EXTERNAL_SUT_URL)
        yield EXTERNAL_SUT_URL
        return

    env = os.environ.copy()
    env["PORT"] = str(PORT)
    # SQLite persists between runs; start each local session from a clean DB
    # so tests are idempotent and parallel workers stay isolated.
    db_path = (
        Path(env.get("SHOP_EASE_DB", ""))
        if env.get("SHOP_EASE_DB")
        else Path(tempfile.gettempdir()) / f"shopease_{PORT}.sqlite3"
    )
    db_path.unlink(missing_ok=True)
    process = subprocess.Popen(
        [sys.executable, str(ROOT / "app" / "store.py")],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_for_health(BASE_URL, process)
        yield BASE_URL
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()


@pytest.fixture
def context(browser: Browser, request: pytest.FixtureRequest) -> Iterator[BrowserContext]:
    """One isolated browser context per test, with video recording enabled."""
    from config.settings import TIMEOUT, VIDEOS

    VIDEOS.mkdir(parents=True, exist_ok=True)
    browser_context = browser.new_context(
        viewport={"width": 1366, "height": 900},
        record_video_dir=str(VIDEOS),
    )
    browser_context.set_default_timeout(TIMEOUT)
    browser_context.set_default_navigation_timeout(TIMEOUT)
    yield browser_context
    # Collect video handles before closing: the page list is cleared on close.
    videos = [page.video for page in browser_context.pages if page.video is not None]
    browser_context.close()
    if getattr(request.node, "rep_call", None) is not None and request.node.rep_call.failed:
        for video in videos:
            if video is None:
                continue
            try:
                path = video.path()
                if path and Path(path).exists():
                    allure.attach(
                        Path(path).read_bytes(),
                        name=f"video_{_safe(request.node.nodeid)}.webm",
                        attachment_type=allure.attachment_type.WEBM,
                    )
            except Exception:
                pass


@pytest.fixture
def page(context: BrowserContext) -> Iterator[Page]:
    page = context.new_page()
    yield page


def _safe(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value)[-100:]


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: object) -> Generator[None, object, None]:
    outcome = yield
    report = outcome.get_result()  # type: ignore[attr-defined]
    setattr(item, f"rep_{report.when}", report)
    if report.when != "call" or not report.failed:
        return
    driver = getattr(item, "funcargs", {}).get("page")
    if driver is None:
        return
    from config.settings import SCREENSHOTS

    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    filename = f"{_safe(item.nodeid)}.png"
    target = SCREENSHOTS / filename
    try:
        driver.screenshot(path=str(target), full_page=True)
        allure.attach(
            target.read_bytes(),
            name=f"screenshot_{filename}",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception:
        pass


@pytest.fixture
def catalog_page(page: Page):
    from tests.pages.catalog_page import CatalogPage

    return CatalogPage(page, base_url=BASE_URL)


@pytest.fixture
def product_page(page: Page):
    from tests.pages.product_page import ProductPage

    return ProductPage(page, base_url=BASE_URL)


@pytest.fixture
def cart_page(page: Page):
    from tests.pages.cart_page import CartPage

    return CartPage(page, base_url=BASE_URL)


@pytest.fixture
def checkout_page(page: Page):
    from tests.pages.checkout_page import CheckoutPage

    return CheckoutPage(page, base_url=BASE_URL)


@pytest.fixture
def login_page(page: Page):
    from tests.pages.login_page import LoginPage

    return LoginPage(page, base_url=BASE_URL)


@pytest.fixture
def register_page(page: Page):
    from tests.pages.register_page import RegisterPage

    return RegisterPage(page, base_url=BASE_URL)


@pytest.fixture
def orders_page(page: Page):
    from tests.pages.orders_page import OrdersPage

    return OrdersPage(page, base_url=BASE_URL)


@pytest.fixture
def confirmation_page(page: Page):
    from tests.pages.order_confirmation_page import OrderConfirmationPage

    return OrderConfirmationPage(page, base_url=BASE_URL)
