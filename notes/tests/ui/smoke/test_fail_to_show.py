import pytest
from playwright.sync_api import Page, expect


@pytest.mark.smoke
@pytest.mark.ui
def test_fail_to_show(page: Page, test_users: dict, profile_name: str) -> None:
    """
    Test that the fail to show page is displayed when the user is not authenticated.
    """
    page.goto("https://www.google.com")
    expect(page.get_by_text("Fail to show")).to_be_visible(timeout=100)
