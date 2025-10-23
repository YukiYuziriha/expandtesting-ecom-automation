# notes/tests/smoke/test_get_note_by_id.py
import pytest
from notes.helpers.api_client import ApiClient


@pytest.mark.notes
@pytest.mark.api
@pytest.mark.smoke
def test_get_note_by_id(api_client_auth: ApiClient) -> None:
    note_id: str | None = None
    try:
        response_create = api_client_auth.create_note(
            "test title GET ID", "test description"
        )
        note_id = response_create["data"]["id"]
        assert note_id is not None  # Type narrowing for mypy
        response = api_client_auth.get_note_by_id(note_id)

        assert response["success"] is True, "Note retrieved successfully"
        assert response["data"]["id"] == note_id, "Note ID matches created value"
        assert (
            response["data"]["title"] == "test title GET ID"
        ), "Title matches created value"
        assert (
            response["data"]["description"] == "test description"
        ), "Description matches created value"
        assert response["data"]["category"] == "Home", "Category matches created value"

    finally:
        if note_id:
            api_client_auth.delete_note(note_id)
