"""Order confirmation page object."""

from __future__ import annotations

from playwright.sync_api import expect

from tests.pages.base_page import BasePage


class OrderConfirmationPage(BasePage):
    def expect_confirmed(self) -> None:
        expect(self.page.get_by_role("heading", name="Order Placed Successfully!")).to_be_visible()

    def order_id(self) -> str:
        return self.page.get_by_test_id("order-id").inner_text().strip()

    def go_to_orders(self) -> None:
        self.page.get_by_role("link", name="View My Orders").click()
