"""Shopping cart page object."""

from __future__ import annotations

import re

from playwright.sync_api import expect

from tests.pages.base_page import BasePage


class CartPage(BasePage):
    def open(self) -> None:
        self.navigate("/cart")
        expect(self.page.get_by_role("heading", name="Shopping Cart")).to_be_visible()

    def items(self) -> int:
        return self.page.get_by_test_id("cart-item").count()

    def expect_item(self, name: str) -> None:
        expect(self.page.locator(".cart-item", has_text=name)).to_be_visible()

    def set_quantity(self, index: int, quantity: int) -> None:
        self.page.get_by_test_id("cart-quantity").nth(index).fill(str(quantity))
        with self.page.expect_navigation(wait_until="load"):
            self.page.get_by_test_id("update-qty").nth(index).click()
        expect(self.page.get_by_test_id("cart-quantity").nth(index)).to_have_value(str(quantity))

    def remove_item(self, index: int = 0) -> None:
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.page.get_by_test_id("remove-item").nth(index).click()

    def item_subtotal(self, index: int = 0) -> float:
        text = self.page.get_by_test_id("item-subtotal").nth(index).inner_text()
        return float(text.replace("$", "").strip())

    def total(self) -> float:
        text = self.page.get_by_test_id("cart-total").inner_text()
        return float(re.findall(r"\d+\.\d+", text)[0])

    def expect_empty(self) -> None:
        expect(self.page.get_by_test_id("cart-item")).to_have_count(0)

    def go_to_checkout(self) -> None:
        self.page.get_by_test_id("checkout-button").click()
