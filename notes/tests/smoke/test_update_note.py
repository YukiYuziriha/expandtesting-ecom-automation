from collections.abc import Callable
from typing import Any

import pytest

from notes.helpers.api_client import ApiClient


@pytest.mark.notes
@pytest.mark.api
@pytest.mark.smoke
def test_update_note(
    api_client_auth: ApiClient, note_factory: Callable[..., dict[str, Any]]
) -> None:
    response_create = note_factory(
        title="test title POST", description="test description POST"
    )
    note_id = response_create["data"]["id"]

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
