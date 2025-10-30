from collections.abc import Callable
from typing import Any

import pytest

from notes.helpers.api_client import ApiClient


@pytest.mark.notes
@pytest.mark.api
@pytest.mark.smoke
def test_get_all_notes(
    api_client_auth: ApiClient, note_factory: Callable[..., dict[str, Any]]
) -> None:
    response_create = note_factory(
        title="test title GET", description="test descriptiom"
    )
    note_id = response_create["data"]["id"]

    response = api_client_auth.get_all_notes()
    note_ids = [note["id"] for note in response["data"]]

    assert note_id in note_ids, f"Created note {note_id} not in list of notes"

    my_note = next((note for note in response["data"] if note["id"] == note_id), None)

    assert my_note is not None, f"Could not find note with id {note_id}"
    assert my_note["title"] == "test title GET", "Title matches created value"
    assert (
        my_note["description"] == "test descriptiom"
    ), "Description matches created value"
    assert my_note["category"] == "Home", "Category defaults to Home"
    assert isinstance(my_note["completed"], bool), "Completed flag is boolean"
