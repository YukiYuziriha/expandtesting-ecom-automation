# conftest.py
import pytest
import json
from playwright.sync_api import Page
from pages.login_page import LoginPage
from pages.base_page import BasePage


@pytest.fixture(scope="session")
def test_users() -> dict:
    """Load test user credentials from JSON (read-only, session-scoped)."""
    with open("test_data/test_users.json") as f:
        return json.load(f)


@pytest.fixture()
def logged_in_page(page: Page, test_users: dict) -> BasePage:
    """
    Returns a BasePage in a logged-in state.
    Waits for post-login redirect to ensure stable state.
    """
    user = test_users["profile1"]
    login_page = LoginPage(page)
    login_page.load()
    login_page.login(user["email"], user["password"])

    page.wait_for_url("**/profile", timeout=10000)
    return BasePage(page)
