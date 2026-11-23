"""Shared page-object behaviour."""

from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from config.settings import BASE_URL, TIMEOUT


class BasePage:
    def __init__(self, page: Page, base_url: str = BASE_URL) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    def navigate(self, path: str = "/") -> None:
        self.page.goto(f"{self.base_url}{path}")

    def expect_title_contains(self, text: str) -> None:
        expect(self.page).to_have_title(re.compile(re.escape(text)))

    def expect_url_contains(self, fragment: str) -> None:
        expect(self.page).to_have_url(f"**{fragment}**", timeout=TIMEOUT)

    def expect_visible(self, test_id: str) -> None:
        expect(self.page.get_by_test_id(test_id)).to_be_visible(timeout=TIMEOUT)

    def price(self, text: str) -> float:
        return float(text.replace("$", "").strip())

    @property
    def cart_count(self) -> int:
        return int(self.page.get_by_test_id("cart-count").inner_text())
