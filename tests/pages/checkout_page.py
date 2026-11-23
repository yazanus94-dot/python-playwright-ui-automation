"""Checkout page object."""

from __future__ import annotations

from playwright.sync_api import expect

from tests.pages.base_page import BasePage


class CheckoutPage(BasePage):
    def open(self) -> None:
        self.navigate("/checkout")
        expect(self.page.get_by_role("heading", name="Checkout")).to_be_visible()

    def fill(
        self,
        name: str = "QA Customer",
        email: str = "qa@example.com",
        address: str = "1 Test Street",
    ) -> None:
        self.page.get_by_test_id("customer-name").fill(name)
        self.page.get_by_test_id("customer-email").fill(email)
        self.page.get_by_test_id("customer-address").fill(address)

    def submit(self) -> None:
        with self.page.expect_navigation(wait_until="load"):
            self.page.get_by_test_id("place-order").click()

    def expect_validation_error(self) -> None:
        expect(self.page.get_by_test_id("checkout-error")).to_contain_text("complete all fields")
