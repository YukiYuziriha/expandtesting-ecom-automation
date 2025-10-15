# tests/conftest.py
import re
import pytest
from playwright.sync_api import Page, Route

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
