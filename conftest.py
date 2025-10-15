# conftest.py
import pytest
import json
import re
from playwright.sync_api import Page, Route

from pages.login_page import LoginPage
from pages.base_page import BasePage

AD_DOMAINS = [
    "enshrouded.com",
    "googleads.g.doubleclick.net",
    "pagead2.googlesyndication.com",
]


def handle_route(route: Route):
    """Intercept and block requests to ad domains."""
    if any(re.search(domain, route.request.url) for domain in AD_DOMAINS):
        return route.abort()
    return route.continue_()


@pytest.fixture
def page(page: Page):
    """
    Override the default Playwright page fixture to block ads.
    """
    page.route("**/*", handle_route)
    yield page


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
