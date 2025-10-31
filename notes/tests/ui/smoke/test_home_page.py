import pytest
from uuid import uuid4
from playwright.sync_api import expect

from notes.pages.home_page import HomePage


@pytest.mark.notes
@pytest.mark.ui
@pytest.mark.smoke
def test_create_note(notes_logged_in_page: HomePage, ui_note_cleanup) -> None:
    title = f"UI Auto Note {uuid4().hex[:8]}"
    description = f"UI Auto Description {uuid4().hex[:8]}"

    notes_logged_in_page.create_note(
        title=title,
        description=description,
        category="Home",
        completed=False,
    )

    note_card = notes_logged_in_page.get_note_by_title(title)
    expect(note_card).to_be_visible()
    expect(notes_logged_in_page.get_note_card_title(note_card)).to_have_text(title)
    expect(notes_logged_in_page.get_note_card_description(note_card)).to_contain_text(
        description
    )


@pytest.mark.notes
@pytest.mark.ui
@pytest.mark.smoke
def test_delete_note(notes_logged_in_page: HomePage, ui_note_factory) -> None:
    note = ui_note_factory()
    title = note["title"]
    notes_logged_in_page.delete_note(title)

    expect(
        notes_logged_in_page.note_card.filter(
            has=notes_logged_in_page.note_card_title.filter(has_text=title)
        )
    ).to_have_count(0)
