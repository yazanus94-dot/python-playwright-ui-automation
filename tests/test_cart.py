"""Cart scenarios with subtotal and total verification."""

from __future__ import annotations

import pytest

from tests.pages.cart_page import CartPage
from tests.pages.catalog_page import CatalogPage

pytestmark = pytest.mark.regression


@pytest.mark.smoke
def test_add_single_item(catalog_page: CatalogPage, cart_page: CartPage) -> None:
    catalog_page.open()
    catalog_page.add_to_cart("Mechanical Keyboard")
    cart_page.open()
    cart_page.expect_item("Mechanical Keyboard")
    assert cart_page.total() == 119.99


def test_cart_count_matches_quantity(catalog_page: CatalogPage, cart_page: CartPage) -> None:
    catalog_page.open()
    catalog_page.add_to_cart("Smart Watch")
    cart_page.open()
    assert cart_page.cart_count == 1


def test_multiple_products_and_total(catalog_page: CatalogPage, cart_page: CartPage) -> None:
    catalog_page.open()
    catalog_page.add_to_cart("Mechanical Keyboard")
    catalog_page.add_to_cart("Non-Slip Yoga Mat")
    cart_page.open()
    assert cart_page.items() == 2
    assert cart_page.total() == 119.99 + 29.99


def test_update_quantity_recalculates(catalog_page: CatalogPage, cart_page: CartPage) -> None:
    catalog_page.open()
    catalog_page.add_to_cart("Smart Watch")
    cart_page.open()
    cart_page.set_quantity(0, 2)
    assert cart_page.item_subtotal() == 399.98
    assert cart_page.total() == 399.98


def test_quantity_one_allowed(catalog_page: CatalogPage, cart_page: CartPage) -> None:
    catalog_page.open()
    catalog_page.add_to_cart("Webcam 1080p")
    cart_page.open()
    cart_page.set_quantity(0, 1)
    assert cart_page.total() == 59.99


def test_remove_item(catalog_page: CatalogPage, cart_page: CartPage) -> None:
    catalog_page.open()
    catalog_page.add_to_cart("Webcam 1080p")
    cart_page.open()
    cart_page.remove_item(0)
    cart_page.expect_empty()


def test_empty_cart_total_is_zero(cart_page: CartPage) -> None:
    cart_page.open()
    cart_page.expect_empty()
    assert cart_page.total() == 0.0


def test_add_same_product_twice_increments_quantity(
    catalog_page: CatalogPage, cart_page: CartPage
) -> None:
    catalog_page.open()
    catalog_page.add_to_cart("Webcam 1080p")
    catalog_page.add_to_cart("Webcam 1080p")
    cart_page.open()
    assert cart_page.items() == 1
    assert cart_page.item_subtotal() == 119.98
