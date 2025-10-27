from collections.abc import Callable

import pytest

from notes.helpers.api_client import ApiClient


@pytest.mark.notes
@pytest.mark.api
@pytest.mark.smoke
def test_create_note(
    api_client_auth: ApiClient, note_cleanup: Callable[[str], None]
) -> None:
    response = api_client_auth.create_note("test title", "test description")

    assert response["success"] is True, "Note created successfully"
    assert "id" in response["data"], "Note ID is present"
    assert response["data"]["title"] == "test title", "Title is correct"

    note_cleanup(response["data"]["id"])
