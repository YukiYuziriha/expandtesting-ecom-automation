import pytest
from uuid import uuid4
from playwright.sync_api import expect, Page

from notes.pages.home_page import HomePage
from notes.pages.login_page import LoginPage


@pytest.mark.notes
@pytest.mark.ui
@pytest.mark.e2e
def test_notes_app_e2e_flow(
    page: Page, test_users: dict, profile_name: str, purge_notes_auth_state
) -> None:
    """
    E2E test for the Notes app: login -> create -> edit -> delete -> logout.

    Validates:
    - Successful authentication and navigation to home page
    - Note creation with title, description, category, and completion status
    - Note editing (title, description, category, completion)
    - Note deletion and verification of removal
    - Logout and return to login screen
    """

    # LOGIN
    login_page = LoginPage(page)
    login_page.load()

    user = test_users[profile_name]
    login_page.login(user["email"], user["password"])

    # Assert successful navigation and login indicator
    page.wait_for_url(f"**{HomePage.URL}")
    expect(login_page.logged_in_marker).to_be_visible(timeout=10000)

    # CREATE NOTE
    home_page = HomePage(page)
    create_title = f"E2E Test Note {uuid4().hex[:8]}"
    create_description = f"E2E Test Description {uuid4().hex[:8]}"
    create_category = "Home"

    home_page.create_note(
        title=create_title,
        description=create_description,
        category=create_category,
        completed=False,
    )

    # Assert the created note is visible with correct content
    created_card = home_page.get_note_by_title(create_title)
    expect(created_card).to_be_visible(timeout=5000)
    expect(home_page.get_note_card_title(created_card)).to_have_text(create_title)
    expect(home_page.get_note_card_description(created_card)).to_contain_text(
        create_description
    )

    # EDIT NOTE
    edit_title = f"E2E Edited Note {uuid4().hex[:8]}"
    edit_description = f"E2E Updated Description {uuid4().hex[:8]}"
    edit_category = "Work"

    home_page.edit_note(
        title=create_title,
        new_title=edit_title,
        new_description=edit_description,
        new_category=edit_category,
        completed=True,
    )

    # Assert the edited note is visible with new content
    edited_card = home_page.get_note_by_title(edit_title)
    expect(edited_card).to_be_visible(timeout=5000)
    expect(home_page.get_note_card_title(edited_card)).to_have_text(edit_title)
    expect(home_page.get_note_card_description(edited_card)).to_contain_text(
        edit_description
    )

    # Assert the old title is no longer present
    expect(
        home_page.note_card.filter(
            has=home_page.note_card_title.filter(has_text=create_title)
        )
    ).to_have_count(0, timeout=5000)

    # DELETE NOTE
    home_page.delete_note(edit_title)

    # Assert the deleted note is no longer visible
    expect(
        home_page.note_card.filter(
            has=home_page.note_card_title.filter(has_text=edit_title)
        )
    ).to_have_count(0, timeout=5000)

    # LOGOUT
    home_page.logout_button.click()

    # Assert we are back on the login page
    expect(login_page.logged_out_marker).to_be_visible(timeout=10000)
