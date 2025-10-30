from collections.abc import Callable
from typing import Any

import pytest

from notes.helpers.api_client import ApiClient


@pytest.mark.notes
@pytest.mark.api
@pytest.mark.smoke
def test_get_note_by_id(
    api_client_auth: ApiClient, note_factory: Callable[..., dict[str, Any]]
) -> None:
    response_create = note_factory(
        title="test title GET ID", description="test description"
    )
    note_id = response_create["data"]["id"]

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
