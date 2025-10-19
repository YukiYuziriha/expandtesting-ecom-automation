# conftest.py
import pytest
import json
import re
from pathlib import Path
from typing import Iterator
from filelock import FileLock

from playwright.sync_api import Page, Route, Browser

from bookstore.pages.login_page import LoginPage
from bookstore.pages.base_page import BasePage
from bookstore.pages.profile_page import ProfilePage

AUTH_FILE = Path(".auth/storage_state.json")
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
    """Override the default Playwright page fixture to block ads."""
    page.route("**/*", handle_route)
    yield page


@pytest.fixture(scope="session")
def test_users() -> dict:
    """Load test user credentials from JSON (read-only, session-scoped)."""
    with open("bookstore/test_data/test_users.json") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def auth_file(
    browser: Browser, test_users: dict, request: pytest.FixtureRequest
) -> Path:
    """
    Session-scoped fixture to log in once and save state.
    Reuses existing state if available. Safe for parallel execution.
    """
    AUTH_FILE.parent.mkdir(exist_ok=True)
    lock_path = AUTH_FILE.with_suffix(".lock")

    with FileLock(lock_path):
        if AUTH_FILE.is_file():
            # Reuse existing auth state — no login needed
            return AUTH_FILE

        # Otherwise, log in and save state
        page = browser.new_page()
        user = test_users["profile1"]
        login_page = LoginPage(page)
        login_page.load()
        login_page.login(user["email"], user["password"])
        page.wait_for_url("**/profile", timeout=10000)
        page.context.storage_state(path=AUTH_FILE)
        page.close()

    return AUTH_FILE


@pytest.fixture()
def logged_in_page(browser: Browser, auth_file: Path) -> Iterator[BasePage]:
    """
    Returns a BasePage instance from a new, pre-authenticated
    browser context. The page is navigated to the profile page
    to ensure it is in a valid, ready-to-use state.
    """
    context = browser.new_context(storage_state=auth_file)
    page = context.new_page()

    profile_page = ProfilePage(page)
    profile_page.load()

    yield profile_page
    context.close()
