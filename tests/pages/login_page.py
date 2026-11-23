"""Login page object."""

from __future__ import annotations

from playwright.sync_api import expect

from tests.pages.base_page import BasePage


class LoginPage(BasePage):
    def open(self) -> None:
        self.navigate("/login")
        expect(self.page.get_by_role("heading", name="Login")).to_be_visible()

    def login(self, email: str, password: str, wait_for_navigation: bool = True) -> None:
        self.page.get_by_test_id("email").fill(email)
        self.page.get_by_test_id("password").fill(password)
        if wait_for_navigation:
            with self.page.expect_navigation(wait_until="load"):
                self.page.get_by_role("button", name="Login").click()
        else:
            # Native HTML5 validation blocks submission for empty credentials.
            self.page.get_by_role("button", name="Login").click()

    def expect_invalid_credentials(self) -> None:
        expect(self.page.locator(".error-message")).to_contain_text("Invalid credentials")

    def expect_validation_blocked(self) -> None:
        expect(self.page.get_by_role("heading", name="Login")).to_be_visible()
