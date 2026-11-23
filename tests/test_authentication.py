"""Authentication scenarios."""

from __future__ import annotations

import pytest

from config.settings import DEMO_EMAIL, DEMO_PASSWORD
from tests.pages.catalog_page import CatalogPage
from tests.pages.login_page import LoginPage
from tests.pages.register_page import RegisterPage

pytestmark = pytest.mark.regression


@pytest.mark.smoke
def test_valid_login(login_page: LoginPage, catalog_page: CatalogPage) -> None:
    login_page.open()
    login_page.login(DEMO_EMAIL, DEMO_PASSWORD)
    catalog_page.expect_title_contains("ShopEase")
    assert catalog_page.page.get_by_role("link", name="Logout").count() == 1


def test_invalid_email(login_page: LoginPage) -> None:
    login_page.open()
    login_page.login("unknown@example.com", DEMO_PASSWORD)
    login_page.expect_invalid_credentials()


def test_invalid_password(login_page: LoginPage) -> None:
    login_page.open()
    login_page.login(DEMO_EMAIL, "WrongPassword123")
    login_page.expect_invalid_credentials()


def test_empty_credentials_blocked(login_page: LoginPage) -> None:
    login_page.open()
    login_page.login("", "", wait_for_navigation=False)
    login_page.expect_validation_blocked()


def test_registration(register_page: RegisterPage, catalog_page: CatalogPage) -> None:
    register_page.open()
    register_page.register("New User", "new-user@example.com", "NewUserPass123")
    assert catalog_page.page.get_by_role("link", name="Logout").count() == 1


def test_duplicate_email_rejected(register_page: RegisterPage) -> None:
    register_page.open()
    register_page.register("Demo User", DEMO_EMAIL, "SomePass123")
    register_page.expect_error("Email already registered")


def test_short_password_rejected(register_page: RegisterPage) -> None:
    register_page.open()
    register_page.register("Short Pass", "short@example.com", "abc")
    register_page.expect_error("Invalid registration data")


def test_logout(catalog_page: CatalogPage, login_page: LoginPage) -> None:
    login_page.open()
    login_page.login(DEMO_EMAIL, DEMO_PASSWORD)
    catalog_page.page.get_by_role("link", name="Logout").click()
    assert catalog_page.page.get_by_role("link", name="Login").count() == 1
