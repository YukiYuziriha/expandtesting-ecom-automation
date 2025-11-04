import pytest
from playwright.sync_api import expect
from notes.pages.login_page import LoginPage
from notes.pages.home_page import HomePage


@pytest.mark.notes
@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.seq_only
@pytest.mark.skip(
    reason="Disabled: upstream logout flow invalidates cached session state and causes cascading failures."
)
def test_logout_button(
    page, notes_logged_in_page: HomePage, notes_session_invalidator_cleanup
):
    # Wait for button to stop detaching (Firefox issue)
    logout_btn = notes_logged_in_page.logout_button
    logout_btn.wait_for(state="attached", timeout=10_000)

    logout_btn.click()
    login_page = LoginPage(notes_logged_in_page.page)

    expect(login_page.logged_out_marker).to_be_visible(timeout=7000)
