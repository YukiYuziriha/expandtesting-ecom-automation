# conftest.py
import json
import os
import re
from pathlib import Path

import pytest

from playwright.sync_api import Page, Route

AD_DOMAINS = [
    # Google Ad Services (the main culprits)
    "googleads.g.doubleclick.net",
    "pagead2.googlesyndication.com",
    "ad.doubleclick.net",
    "googleadservices.com",
    "googlesyndication.com",
    "doubleclick.net",
    "ads.google.com",
    "adservice.google.com",
    # Analytics/Tracking
    "google-analytics.com",
    "analytics.google.com",
    # Other common ad networks
    "taboola.com",
    "outbrain.com",
    "adnxs.com",
    "ads.yahoo.com",
    "ads.bing.com",
    "adserver.org",
    "adtech.com",
    "advertising.com",
    "atdmt.com",
    "exponential.com",
    "fastclick.net",
    "media.net",
    "openx.net",
    "pubmatic.com",
    "rubiconproject.com",
    "smartadserver.com",
    "yieldmanager.com",
    "google_vignette",
    "enshrouded.com",
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
