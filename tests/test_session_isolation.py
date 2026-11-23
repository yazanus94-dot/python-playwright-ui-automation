"""Session-isolation scenarios; each browser context must have private state."""

from __future__ import annotations

import pytest
from playwright.sync_api import Browser

from tests.pages.cart_page import CartPage
from tests.pages.catalog_page import CatalogPage
from tests.pages.checkout_page import CheckoutPage
from tests.pages.order_confirmation_page import OrderConfirmationPage

pytestmark = [pytest.mark.isolation, pytest.mark.regression]


@pytest.fixture
def two_contexts(browser: Browser):
    first = browser.new_context()
    second = browser.new_context()
    try:
        yield first.new_page(), second.new_page()
    finally:
        first.close()
        second.close()


def _catalog(page, base_url: str) -> CatalogPage:
    return CatalogPage(page, base_url=base_url)


def test_context_b_starts_empty(two_contexts, live_server: str) -> None:
    page_a, page_b = two_contexts
    catalog_a, catalog_b = _catalog(page_a, live_server), _catalog(page_b, live_server)
    catalog_a.open()
    catalog_a.add_to_cart("Smart Watch")
    catalog_b.open()
    catalog_b.expect_cart_count(0)


def test_context_b_cannot_see_orders(two_contexts, live_server: str) -> None:
    page_a, page_b = two_contexts
    catalog_a = _catalog(page_a, live_server)
    catalog_a.open()
    catalog_a.add_to_cart("Smart Watch")
    checkout = CheckoutPage(page_a, base_url=live_server)
    confirmation = OrderConfirmationPage(page_a, base_url=live_server)
    checkout.open()
    checkout.fill()
    checkout.submit()
    order_id = confirmation.order_id()

    page_b.goto(f"{live_server}/orders")
    assert order_id not in page_b.content()


def test_checkout_does_not_clear_other_cart(two_contexts, live_server: str) -> None:
    page_a, page_b = two_contexts
    catalog_a, catalog_b = _catalog(page_a, live_server), _catalog(page_b, live_server)
    catalog_a.open()
    catalog_a.add_to_cart("Smart Watch")
    catalog_b.open()
    catalog_b.add_to_cart("Webcam 1080p")

    checkout = CheckoutPage(page_a, base_url=live_server)
    checkout.open()
    checkout.fill()
    checkout.submit()

    cart_b = CartPage(page_b, base_url=live_server)
    cart_b.open()
    assert cart_b.items() == 1
    assert cart_b.total() == 59.99


def test_two_contexts_can_checkout_concurrently(two_contexts, live_server: str) -> None:
    page_a, page_b = two_contexts
    ids = []
    for page in (page_a, page_b):
        catalog = _catalog(page, live_server)
        catalog.open()
        catalog.add_to_cart("Webcam 1080p")
        checkout = CheckoutPage(page, base_url=live_server)
        confirmation = OrderConfirmationPage(page, base_url=live_server)
        checkout.open()
        checkout.fill(email=f"user-{len(ids)}@example.com")
        checkout.submit()
        ids.append(confirmation.order_id())
    assert len(set(ids)) == 2
