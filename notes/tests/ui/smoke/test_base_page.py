import pytest
from playwright.sync_api import expect
from notes.pages.login_page import LoginPage
from notes.pages.home_page import HomePage


@pytest.mark.notes
@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.seq_only
def test_logout_button(
    page, notes_logged_in_page: HomePage, notes_session_invalidator_cleanup
):
    notes_logged_in_page.logout_button.click()
    login_page = LoginPage(notes_logged_in_page.page)

    expect(login_page.logged_out_marker).to_be_visible(timeout=7000)
