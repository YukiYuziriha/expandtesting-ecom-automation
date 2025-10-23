# notes/tests/smoke/test_create_note.py
import pytest
from notes.helpers.api_client import ApiClient


@pytest.mark.notes
@pytest.mark.api
@pytest.mark.smoke
def test_create_note(api_client_auth: ApiClient) -> None:
    note_id: str | None = None
    try:
        response = api_client_auth.create_note("test title", "test description")

        assert response["success"] is True, "Note created successfully"
        assert "id" in response["data"], "Note ID is present"
        assert response["data"]["title"] == "test title", "Title is correct"

        note_id = response["data"]["id"]
    finally:
        if note_id:
            api_client_auth.delete_note(note_id)
