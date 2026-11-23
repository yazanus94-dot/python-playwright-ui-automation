"""Product detail page object."""

from __future__ import annotations

from playwright.sync_api import expect

from tests.pages.base_page import BasePage


class ProductPage(BasePage):
    def open(self, product_id: int) -> None:
        self.navigate(f"/product/{product_id}")
        expect(self.page.get_by_test_id("product-title")).to_be_visible()

    def title(self) -> str:
        return self.page.get_by_test_id("product-title").inner_text()

    def price(self) -> float:
        return self.price_text(self.page.get_by_test_id("product-price").inner_text())

    @staticmethod
    def price_text(text: str) -> float:
        return float(text.replace("$", "").strip())

    def set_quantity(self, quantity: int | str) -> None:
        self.page.get_by_test_id("quantity").fill(str(quantity))

    def add_to_cart(self) -> None:
        before = self.cart_count
        self.page.get_by_test_id("add-to-cart").click()
        expect(self.page.get_by_test_id("cart-count")).to_have_text(str(before + 1))

    def open_unknown(self, product_id: int = 99999) -> None:
        self.navigate(f"/product/{product_id}")

    def expect_not_found(self) -> None:
        expect(self.page.get_by_role("heading", name="404")).to_be_visible()
