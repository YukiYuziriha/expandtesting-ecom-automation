# conftest.py
import json
import os
import re
from pathlib import Path
from typing import Iterator

import pytest
from filelock import FileLock

from playwright.sync_api import Page, Route, Browser

from bookstore.pages.login_page import LoginPage
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


TEST_USERS_FILE = Path("shared/test_data/test_users.json")


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register custom CLI options for the test suite."""
    parser.addoption(
        "--profile",
        action="store",
        default="profile1",
        help="Name of the test user profile to use (default: profile1).",
    )


@pytest.fixture(scope="session")
def profile_name(pytestconfig: pytest.Config, test_users: dict) -> str:
    """Resolve the active profile name from CLI options and validate it exists."""
    profile = pytestconfig.getoption("profile")
    if profile not in test_users:
        available = ", ".join(sorted(test_users))
        raise pytest.UsageError(
            f"Unknown profile '{profile}'. Available profiles: {available}."
        )
    return profile


@pytest.fixture(scope="session")
def test_users() -> dict:
    """Load test user credentials from an env var or JSON fixture."""
    raw = os.getenv("TEST_USERS_JSON")
    if raw:
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("TEST_USERS_JSON secret is not valid JSON.") from exc

    if TEST_USERS_FILE.is_file():
        with TEST_USERS_FILE.open() as f:
            return json.load(f)

    raise FileNotFoundError(
        "Test user credentials were not provided. Set the TEST_USERS_JSON env "
        "variable or create shared/test_data/test_users.json."
    )


@pytest.fixture(scope="session")
def auth_file(browser: Browser, test_users: dict, profile_name: str) -> Path:
    """
    Session-scoped fixture to log in once and save state.
    Reuses existing state if available. Safe for parallel execution.
    """
    auth_path = (
        AUTH_FILE
        if profile_name == "profile1"
        else AUTH_FILE.with_name(f"{AUTH_FILE.stem}_{profile_name}{AUTH_FILE.suffix}")
    )
    auth_path.parent.mkdir(exist_ok=True)
    lock_path = auth_path.with_suffix(".lock")

    with FileLock(lock_path):
        if auth_path.is_file():
            # Reuse existing auth state — no login needed
            return auth_path

        # Otherwise, log in and save state
        page = browser.new_page()
        user = test_users[profile_name]
        login_page = LoginPage(page)
        login_page.load()
        login_page.login(user["email"], user["password"])
        page.wait_for_url("**/profile", timeout=10000)
        page.context.storage_state(path=auth_path)
        page.close()

    return auth_path


@pytest.fixture()
def logged_in_page(browser: Browser, auth_file: Path) -> Iterator[ProfilePage]:
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


@pytest.fixture()
def orders_cleanup(logged_in_page: ProfilePage) -> Iterator[None]:
    """For tests that create orders, clear them before and after the run."""
    yield

    logged_in_page.load()
    logged_in_page.delete_all_orders_if_present()
