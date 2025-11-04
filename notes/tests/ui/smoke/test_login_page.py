import pytest
from playwright.sync_api import Page, expect
from notes.pages.login_page import LoginPage


@pytest.mark.notes
@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.no_auth
def test_valid_credentials(page: Page, test_users: dict, profile_name: str) -> None:
    login_page = LoginPage(page)
    login_page.load()

    user = test_users[profile_name]
    login_page.login(user["email"], user["password"])

    page.wait_for_url("**/notes/**")
    expect(login_page.logged_in_marker).to_be_visible(timeout=10000)


@pytest.mark.notes
@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.no_auth
def test_invalid_credentials(page: Page) -> None:
    login_page = LoginPage(page)
    login_page.load()

    login_page.login("invalid@example.com", "invalidpassword")
    expect(login_page.credentials_error_message).to_be_visible(timeout=10000)
