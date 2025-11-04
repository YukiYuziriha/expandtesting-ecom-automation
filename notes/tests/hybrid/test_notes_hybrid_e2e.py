import os
import requests
from uuid import uuid4

import pytest
from playwright.sync_api import expect

from notes.pages.home_page import HomePage
from notes.helpers.api_client import ApiClient


@pytest.mark.notes
@pytest.mark.ui
@pytest.mark.api
@pytest.mark.e2e
@pytest.mark.hybrid
@pytest.mark.skipif(
    os.getenv("NOTES_OFFLINE", "0") == "1",
    reason="Hybrid UI+API test requires live backend (NOTES_OFFLINE=0)",
)
def test_notes_hybrid_ui_api_flow(
    notes_logged_in_page: HomePage,
    api_client_auth: ApiClient,
    note_cleanup,
) -> None:
    """
    Hybrid E2E: Seed via API, verify/mutate via UI, mutate via API, verify via UI, delete via UI with API 404.
    """

    # Seed via API
    title1 = f"Hybrid Note {uuid4().hex[:8]}"
    desc1 = f"Hybrid Desc {uuid4().hex[:8]}"
    category1 = "Home"

    create_resp = api_client_auth.create_note(title1, desc1, category1)
    note_id = create_resp["data"]["id"]
    note_cleanup(note_id)

    # Verify in UI
    notes_logged_in_page.load()
    card1 = notes_logged_in_page.get_note_by_title(title1)
    expect(card1).to_be_visible()
    expect(notes_logged_in_page.get_note_card_title(card1)).to_have_text(title1)
    expect(notes_logged_in_page.get_note_card_description(card1)).to_contain_text(desc1)

    # Mutate in UI
    title2 = f"Hybrid Edited {uuid4().hex[:8]}"
    desc2 = f"Updated {uuid4().hex[:8]}"
    category2 = "Work"
    notes_logged_in_page.edit_note(
        title=title1,
        new_title=title2,
        new_description=desc2,
        new_category=category2,
        completed=True,
    )
    card2 = notes_logged_in_page.get_note_by_title(title2)
    expect(card2).to_be_visible()
    expect(notes_logged_in_page.get_note_card_title(card2)).to_have_text(title2)
    expect(notes_logged_in_page.get_note_card_description(card2)).to_contain_text(desc2)
    expect(
        notes_logged_in_page.note_card.filter(
            has=notes_logged_in_page.note_card_title.filter(has_text=title1)
        )
    ).to_have_count(0)

    # Mutate via API
    title3 = f"Hybrid API Update {uuid4().hex[:8]}"
    desc3 = f"API Updated {uuid4().hex[:8]}"
    category3 = "Home"
    api_client_auth.update_note(note_id, title3, desc3, False, category3)

    # Verify in UI after API mutation
    notes_logged_in_page.load()
    card3 = notes_logged_in_page.get_note_by_title(title3)
    expect(card3).to_be_visible()
    expect(notes_logged_in_page.get_note_card_title(card3)).to_have_text(title3)
    expect(notes_logged_in_page.get_note_card_description(card3)).to_contain_text(desc3)
    expect(
        notes_logged_in_page.note_card.filter(
            has=notes_logged_in_page.note_card_title.filter(has_text=title2)
        )
    ).to_have_count(0)

    # Delete in UI and verify absense
    notes_logged_in_page.delete_note(title3)
    expect(
        notes_logged_in_page.note_card.filter(
            has=notes_logged_in_page.note_card_title.filter(has_text=title3)
        )
    ).to_have_count(0)

    # Verify deletion via API
    with pytest.raises(requests.exceptions.HTTPError) as ei:
        api_client_auth.get_note_by_id(note_id)
    assert ei.value.response.status_code in {404, 400}
