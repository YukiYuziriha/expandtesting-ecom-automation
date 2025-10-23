# notes/tests/smoke/test_get_all_notes.py
from notes.helpers.api_client import ApiClient
import pytest


@pytest.mark.notes
@pytest.mark.api
@pytest.mark.smoke
def test_get_all_notes(api_client_auth: ApiClient):
    try:
        note_id = api_client_auth.create_note("test title GET", "test descriptiom")[
            "data"
        ]["id"]
        response = api_client_auth.get_all_notes()
        note_ids = [note["id"] for note in response["data"]]

        assert note_id in note_ids, f"Created note {note_id} not in list of notes"

        my_note = next(
            (note for note in response["data"] if note["id"] == note_id), None
        )

        assert my_note is not None, f"Could not find note with id {note_id}"
        assert my_note["title"] == "test title GET", "Title matches created value"

    finally:
        if note_id:
            api_client_auth.delete_note(note_id)
