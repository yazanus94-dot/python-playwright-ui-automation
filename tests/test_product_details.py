"""Product detail scenarios."""

from __future__ import annotations

import pytest

from tests.pages.product_page import ProductPage

PRODUCTS = [
    (1, "Wireless Bluetooth Headphones", 79.99),
    (2, "Protective Phone Case", 24.99),
    (3, "Stainless Steel Water Bottle", 32.50),
    (4, "Mechanical Keyboard", 119.99),
    (5, "Running Shoes Air Cushion", 89.99),
    (6, "Webcam 1080p", 59.99),
    (7, "Aluminum Laptop Stand", 45.00),
    (8, "Programmable Coffee Maker", 69.99),
    (9, "Non-Slip Yoga Mat", 29.99),
    (10, "Smart Watch", 199.99),
]
pytestmark = pytest.mark.regression


@pytest.mark.parametrize("product_id,name,price", PRODUCTS)
def test_product_details(
    product_page: ProductPage, product_id: int, name: str, price: float
) -> None:
    product_page.open(product_id)
    assert product_page.title() == name
    assert product_page.price() == price


def test_invalid_product_returns_404(product_page: ProductPage) -> None:
    product_page.open_unknown(99999)
    product_page.expect_not_found()


def test_default_quantity_is_one(product_page: ProductPage) -> None:
    product_page.open(1)
    assert product_page.page.get_by_test_id("quantity").input_value() == "1"


@pytest.mark.smoke
def test_add_to_cart_from_product_page(product_page: ProductPage, cart_page) -> None:
    product_page.open(1)
    product_page.add_to_cart()
    cart_page.open()
    assert cart_page.items() == 1
    assert cart_page.item_subtotal() == 79.99


def test_product_page_price_matches_catalog(product_page: ProductPage, catalog_page) -> None:
    catalog_page.open()
    catalog_page.open_product("Smart Watch")
    assert product_page.title() == "Smart Watch"
    assert product_page.price() == 199.99
