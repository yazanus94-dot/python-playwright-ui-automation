"""Negative scenarios at HTTP and UI level."""

from __future__ import annotations

import pytest

from config.settings import BASE_URL
from tests.pages.product_page import ProductPage

pytestmark = [pytest.mark.negative, pytest.mark.regression]


@pytest.mark.parametrize("quantity", [0, -1, 11, 999])
def test_invalid_quantity_rejected(page, quantity: int) -> None:
    response = page.request.post(
        f"{BASE_URL}/cart/add", data={"product_id": 1, "quantity": quantity}
    )
    assert response.status == 400
    assert "Quantity" in response.json()["error"]


def test_unknown_product_add_rejected(page) -> None:
    response = page.request.post(f"{BASE_URL}/cart/add", data={"product_id": 99999})
    assert response.status == 404


def test_missing_product_id_rejected(page) -> None:
    response = page.request.post(f"{BASE_URL}/cart/add", data={"quantity": 1})
    assert response.status == 400


def test_non_numeric_product_rejected(page) -> None:
    response = page.request.post(f"{BASE_URL}/cart/add", data={"product_id": "abc"})
    assert response.status == 400


def test_unsupported_method_rejected(page) -> None:
    response = page.request.get(f"{BASE_URL}/cart/add")
    assert response.status == 405


def test_unknown_api_product(page) -> None:
    response = page.request.get(f"{BASE_URL}/api/products/99999")
    assert response.status == 404


def test_unknown_page_shows_404(product_page: ProductPage) -> None:
    product_page.open_unknown(123456)
    product_page.expect_not_found()


def test_cart_update_missing_item_rejected(page) -> None:
    response = page.request.post(
        f"{BASE_URL}/cart/update", data={"product_id": 99999, "quantity": 1}
    )
    assert response.status == 404
