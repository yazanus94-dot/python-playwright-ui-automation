"""Registration page object."""

from __future__ import annotations

from playwright.sync_api import expect

from tests.pages.base_page import BasePage


class RegisterPage(BasePage):
    def open(self) -> None:
        self.navigate("/register")
        expect(self.page.get_by_role("heading", name="Create Account")).to_be_visible()

    def register(self, name: str, email: str, password: str) -> None:
        self.page.get_by_test_id("name").fill(name)
        self.page.get_by_test_id("email").fill(email)
        self.page.get_by_test_id("password").fill(password)
        with self.page.expect_navigation(wait_until="load"):
            self.page.get_by_role("button", name="Register").click()

    def expect_error(self, text: str) -> None:
        expect(self.page.locator(".error-message")).to_contain_text(text)
