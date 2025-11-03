from collections.abc import Iterator
from pathlib import Path

import pytest
from filelock import FileLock
from playwright.sync_api import Browser

from bookstore.pages.login_page import LoginPage
from bookstore.pages.profile_page import ProfilePage
from shared.helpers.ad_blocker import block_ads_on_context

BOOKSTORE_AUTH_DIR = Path(".auth/bookstore")
BOOKSTORE_AUTH_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def auth_file(browser: Browser, test_users: dict, profile_name: str) -> Path:
    """
    Session-scoped fixture to log in once and save the bookstore auth state.
    Reuses existing state if available. Safe for parallel execution.
    """
    auth_path = BOOKSTORE_AUTH_DIR / f"storage_state_{profile_name}.json"
    lock_path = auth_path.with_suffix(".lock")

    with FileLock(lock_path):
        if auth_path.is_file():
            return auth_path

        page = browser.new_page()
        user = test_users[profile_name]
        login_page = LoginPage(page)
        login_page.load()
        login_page.login(user["email"], user["password"])
        page.wait_for_url("**/profile", timeout=10_000)
        page.context.storage_state(path=auth_path)
        page.close()

    return auth_path


@pytest.fixture()
def logged_in_page(browser: Browser, auth_file: Path) -> Iterator[ProfilePage]:
    """
    Return a ProfilePage instance backed by a new, pre-authenticated context.
    """
    context = browser.new_context(storage_state=auth_file)
    block_ads_on_context(context)
    page = context.new_page()

    profile_page = ProfilePage(page)
    profile_page.load()

    try:
        yield profile_page
    finally:
        context.close()


@pytest.fixture()
def orders_cleanup(logged_in_page: ProfilePage) -> Iterator[None]:
    """For tests that create orders, clear them before and after the run."""
    yield

    logged_in_page.load()
    logged_in_page.delete_all_orders_if_present()
