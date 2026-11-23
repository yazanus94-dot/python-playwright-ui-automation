"""Catalogue / homepage page object."""

from __future__ import annotations

from playwright.sync_api import expect

from tests.pages.base_page import BasePage


class CatalogPage(BasePage):
    SEARCH = "search-input"
    CATEGORY = "category-select"
    CARD = "product-card"
    ADD = "add-to-cart"

    def open(self) -> None:
        self.navigate("/")
        expect(self.page.get_by_test_id(self.CARD)).to_have_count(10)

    def _submit_search(self) -> None:
        with self.page.expect_navigation(wait_until="load"):
            self.page.get_by_role("button", name="Search").click()

    def search(self, query: str) -> None:
        self.page.get_by_test_id(self.SEARCH).fill(query)
        self._submit_search()

    def filter_category(self, category: str) -> None:
        self.page.get_by_test_id(self.CATEGORY).select_option(category)
        self._submit_search()

    def search_and_filter(self, query: str, category: str) -> None:
        self.page.get_by_test_id(self.SEARCH).fill(query)
        self.page.get_by_test_id(self.CATEGORY).select_option(category)
        self._submit_search()

    def card_count(self) -> int:
        return self.page.get_by_test_id(self.CARD).count()

    def product_names(self) -> list[str]:
        return self.page.locator(".product-name").all_inner_texts()

    def expect_product(self, name: str) -> None:
        expect(self.page.locator(".product-name", has_text=name).first).to_be_visible()

    def expect_no_results(self) -> None:
        expect(self.page.get_by_test_id(self.CARD)).to_have_count(0)

    def open_product(self, name: str) -> None:
        self.page.locator(".product-card", has_text=name).locator(".product-name a").click()

    def add_to_cart(self, name: str) -> None:
        before = self.cart_count
        self.page.locator(".product-card", has_text=name).get_by_test_id(self.ADD).click()
        expect(self.page.get_by_test_id("cart-count")).to_have_text(str(before + 1))

    def add_first_to_cart(self) -> str:
        name = self.product_names()[0]
        self.add_to_cart(name)
        return name

    def go_to_cart(self) -> None:
        self.page.get_by_role("link", name="Cart").click()

    def go_to_login(self) -> None:
        self.page.get_by_role("link", name="Login").click()

    def go_to_register(self) -> None:
        self.page.get_by_role("link", name="Register").click()

    def expect_cart_count(self, expected: int) -> None:
        expect(self.page.get_by_test_id("cart-count")).to_have_text(str(expected))
