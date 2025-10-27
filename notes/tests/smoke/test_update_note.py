from collections.abc import Callable

import pytest

from notes.helpers.api_client import ApiClient


@pytest.mark.notes
@pytest.mark.api
@pytest.mark.smoke
def test_update_note(
    api_client_auth: ApiClient, note_cleanup: Callable[[str], None]
) -> None:
    response_create = api_client_auth.create_note(
        "test title POST", "test description POST"
    )
    note_id = response_create["data"]["id"]
    note_cleanup(note_id)

    created_at = response_create["data"]["created_at"]
    response_update = api_client_auth.update_note(
        note_id, "test title PUT", "test description PUT", True, "Home"
    )
    assert response_update["success"] is True, "Note updated successfully"
    assert response_update["data"]["id"] == note_id, "Note ID matches created value"
    assert (
        response_update["data"]["title"] == "test title PUT"
    ), "Title matches updated value"
    assert (
        response_update["data"]["description"] == "test description PUT"
    ), "Description matches updated value"
    assert (
        response_update["data"]["completed"] is True
    ), "Completed matches updated value"
    assert (
        response_update["data"]["category"] == "Home"
    ), "Category matches updated value"
    assert (
        response_update["data"]["created_at"] == created_at
    ), "Created at matches created value"
