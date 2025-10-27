from collections.abc import Callable

import pytest

from notes.helpers.api_client import ApiClient


@pytest.mark.notes
@pytest.mark.api
@pytest.mark.smoke
def test_get_note_by_id(
    api_client_auth: ApiClient, note_cleanup: Callable[[str], None]
) -> None:
    response_create = api_client_auth.create_note(
        "test title GET ID", "test description"
    )
    note_id = response_create["data"]["id"]
    note_cleanup(note_id)

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
