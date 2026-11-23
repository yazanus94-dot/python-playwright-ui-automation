"""Homepage and catalogue scenarios."""

from __future__ import annotations

import pytest

from tests.pages.catalog_page import CatalogPage

pytestmark = pytest.mark.regression


@pytest.mark.smoke
def test_catalog_loads(catalog_page: CatalogPage) -> None:
    catalog_page.open()
    catalog_page.expect_title_contains("ShopEase")
    catalog_page.expect_visible("search-input")


def test_catalog_has_ten_products(catalog_page: CatalogPage) -> None:
    catalog_page.open()
    assert catalog_page.card_count() == 10


@pytest.mark.smoke
def test_guest_cart_starts_empty(catalog_page: CatalogPage) -> None:
    catalog_page.open()
    catalog_page.expect_cart_count(0)


def test_navigation_links_present(catalog_page: CatalogPage) -> None:
    catalog_page.open()
    for name in ("Home", "Cart", "Login", "Register"):
        assert catalog_page.page.get_by_role("link", name=name).count() >= 1


@pytest.mark.parametrize(
    "query,expected",
    [
        ("Headphones", "Wireless Bluetooth Headphones"),
        ("Keyboard", "Mechanical Keyboard"),
        ("Yoga", "Non-Slip Yoga Mat"),
    ],
)
def test_search_returns_matching_product(
    catalog_page: CatalogPage, query: str, expected: str
) -> None:
    catalog_page.open()
    catalog_page.search(query)
    catalog_page.expect_product(expected)


def test_search_is_case_insensitive(catalog_page: CatalogPage) -> None:
    catalog_page.open()
    catalog_page.search("headphones")
    catalog_page.expect_product("Wireless Bluetooth Headphones")


def test_search_no_results(catalog_page: CatalogPage) -> None:
    catalog_page.open()
    catalog_page.search("nonexistent-product-xyz")
    catalog_page.expect_no_results()


def test_empty_search_shows_all(catalog_page: CatalogPage) -> None:
    catalog_page.open()
    catalog_page.search("")
    assert catalog_page.card_count() == 10


@pytest.mark.parametrize(
    "category,expected",
    [
        ("Electronics", "Smart Watch"),
        ("Accessories", "Protective Phone Case"),
        ("Home & Kitchen", "Coffee Maker"),
        ("Sports", "Running Shoes"),
    ],
)
def test_category_filter(catalog_page: CatalogPage, category: str, expected: str) -> None:
    catalog_page.open()
    catalog_page.filter_category(category)
    catalog_page.expect_product(expected)


def test_combined_search_and_filter(catalog_page: CatalogPage) -> None:
    catalog_page.open()
    catalog_page.search_and_filter("Watch", "Electronics")
    assert catalog_page.card_count() == 1
    catalog_page.expect_product("Smart Watch")


@pytest.mark.smoke
def test_add_to_cart_from_catalog(catalog_page: CatalogPage) -> None:
    catalog_page.open()
    catalog_page.add_first_to_cart()
    catalog_page.expect_cart_count(1)


def test_product_prices_displayed(catalog_page: CatalogPage) -> None:
    catalog_page.open()
    prices = catalog_page.page.locator(".product-price").all_inner_texts()
    assert len(prices) == 10
    assert all(price.startswith("$") for price in prices)
