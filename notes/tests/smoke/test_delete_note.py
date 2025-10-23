# notes/tests/smoke/test_delete_note.py
from notes.helpers.api_client import ApiClient
import pytest
import requests


@pytest.mark.notes
@pytest.mark.api
@pytest.mark.smoke
def test_delete_note(api_client_auth: ApiClient):
    note_id = api_client_auth.create_note("test title", "test description")["data"][
        "id"
    ]
    response = api_client_auth.delete_note(note_id)

    assert response["success"] is True, "Note deleted successfully"

    with pytest.raises(requests.exceptions.HTTPError) as ei:
        api_client_auth.delete_note(note_id)

    status = ei.value.response.status_code
    # docs show 400 for bad request, but prod returns 404
    assert status in {400, 404}, f"Expected 400/404 on second DELETE, got {status}"
