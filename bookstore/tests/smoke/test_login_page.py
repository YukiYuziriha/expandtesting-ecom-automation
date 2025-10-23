# tests/smoke/test_login_page.py
import pytest
from playwright.sync_api import Page, expect
from bookstore.pages.login_page import LoginPage


@pytest.mark.bookstore
@pytest.mark.ui
@pytest.mark.smoke
def test_login_rejects_empty_credentials(page: Page) -> None:
    """Smoke: Login form shows error when both fields are empty."""
    login_page = LoginPage(page)
    login_page.load()
    login_page.login("", "")

    expect(login_page.credentials_error_message).to_be_visible(timeout=10000)


@pytest.mark.bookstore
@pytest.mark.ui
@pytest.mark.smoke
def test_login_rejects_invalid_credentials(page: Page) -> None:
    """Smoke: Login form shows error for malformed email and short password."""
    login_page = LoginPage(page)
    login_page.load()
    login_page.login("not-an-email", "123")  # clearly invalid

    expect(login_page.credentials_error_message).to_be_visible(timeout=10000)


@pytest.mark.bookstore
@pytest.mark.ui
@pytest.mark.smoke
def test_login_success_with_valid_credentials(
    page: Page, test_users: dict, profile_name: str
) -> None:
    """Smoke: Valid credentials redirect to profile page."""
    login_page = LoginPage(page)
    login_page.load()

    user = test_users[profile_name]
    login_page.login(user["email"], user["password"])

    page.wait_for_url("**/profile")
    expect(page.get_by_role("heading", name="Profile")).to_be_visible()
    expect(page.get_by_role("heading", name="My Orders")).to_be_visible()
