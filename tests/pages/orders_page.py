"""Order history page object."""

from __future__ import annotations

from playwright.sync_api import expect

from tests.pages.base_page import BasePage


class OrdersPage(BasePage):
    def open(self) -> None:
        self.navigate("/orders")
        expect(self.page.get_by_role("heading", name="My Orders")).to_be_visible()

    def order_ids(self) -> list[str]:
        return self.page.locator('a[href^="/orders/"]').all_inner_texts()

    def expect_order(self, order_id: str) -> None:
        expect(self.page.get_by_role("link", name=order_id)).to_be_visible()

    def expect_empty(self) -> None:
        expect(self.page.get_by_role("link", name="Start Shopping")).to_be_visible()

    def open_order(self, order_id: str) -> None:
        self.page.get_by_role("link", name=order_id).click()
