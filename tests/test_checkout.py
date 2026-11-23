"""Checkout and order history scenarios."""

from __future__ import annotations

import pytest

from tests.pages.cart_page import CartPage
from tests.pages.catalog_page import CatalogPage
from tests.pages.checkout_page import CheckoutPage
from tests.pages.order_confirmation_page import OrderConfirmationPage
from tests.pages.login_page import LoginPage
from tests.pages.orders_page import OrdersPage

pytestmark = pytest.mark.regression


def _add_item(catalog_page: CatalogPage) -> None:
    catalog_page.open()
    catalog_page.add_to_cart("Smart Watch")


@pytest.mark.smoke
def test_successful_checkout(
    catalog_page: CatalogPage, checkout_page: CheckoutPage, confirmation_page: OrderConfirmationPage
) -> None:
    _add_item(catalog_page)
    checkout_page.open()
    checkout_page.fill()
    checkout_page.submit()
    confirmation_page.expect_confirmed()
    assert confirmation_page.order_id()


def test_checkout_clears_cart(
    catalog_page: CatalogPage,
    checkout_page: CheckoutPage,
    confirmation_page: OrderConfirmationPage,
    cart_page: CartPage,
) -> None:
    _add_item(catalog_page)
    checkout_page.open()
    checkout_page.fill()
    checkout_page.submit()
    confirmation_page.expect_confirmed()
    cart_page.open()
    cart_page.expect_empty()


def test_order_appears_in_history(
    catalog_page: CatalogPage,
    checkout_page: CheckoutPage,
    confirmation_page: OrderConfirmationPage,
    orders_page: OrdersPage,
) -> None:
    _add_item(catalog_page)
    checkout_page.open()
    checkout_page.fill()
    checkout_page.submit()
    order_id = confirmation_page.order_id()
    orders_page.open()
    orders_page.expect_order(order_id)


def test_order_detail_opens(
    catalog_page: CatalogPage,
    checkout_page: CheckoutPage,
    confirmation_page: OrderConfirmationPage,
    orders_page: OrdersPage,
) -> None:
    _add_item(catalog_page)
    checkout_page.open()
    checkout_page.fill()
    checkout_page.submit()
    order_id = confirmation_page.order_id()
    orders_page.open()
    orders_page.open_order(order_id)
    assert order_id in orders_page.page.content()


def test_checkout_requires_valid_form(
    catalog_page: CatalogPage, checkout_page: CheckoutPage
) -> None:
    _add_item(catalog_page)
    checkout_page.open()
    checkout_page.fill(email="not-an-email")
    checkout_page.submit()
    checkout_page.expect_validation_error()


def test_empty_cart_redirects_from_checkout(checkout_page: CheckoutPage) -> None:
    checkout_page.navigate("/checkout")
    checkout_page.page.wait_for_url("**/")
    assert "/checkout" not in checkout_page.page.url


def test_order_history_requires_login(orders_page: OrdersPage, login_page: LoginPage) -> None:
    orders_page.navigate("/orders")
    orders_page.page.wait_for_url("**/login")
    assert "/login" in orders_page.page.url
    login_page.expect_validation_blocked()


def test_registered_user_checkout(
    catalog_page: CatalogPage,
    register_page,
    checkout_page: CheckoutPage,
    confirmation_page: OrderConfirmationPage,
    orders_page: OrdersPage,
) -> None:
    register_page.open()
    register_page.register("UI Tester", "ui-tester@example.com", "UiTestPass123")
    _add_item(catalog_page)
    checkout_page.open()
    checkout_page.fill(name="UI Tester", email="ui-tester@example.com")
    checkout_page.submit()
    order_id = confirmation_page.order_id()
    orders_page.open()
    orders_page.expect_order(order_id)
