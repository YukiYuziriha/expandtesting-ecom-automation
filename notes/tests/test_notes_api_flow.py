from collections.abc import Callable
from uuid import uuid4

import pytest
import requests

from notes.helpers.api_client import ApiClient


@pytest.mark.notes
@pytest.mark.api
@pytest.mark.e2e
def test_notes_api_flow(
    api_client_auth: ApiClient, note_cleanup: Callable[[str], None]
) -> None:
    # CREATE
    title = f"Full Flow Title {uuid4().hex[:8]}"
    description = "Full Flow Description"
    response_create = api_client_auth.create_note(title, description)
    assert response_create["success"] is True

    note_id = response_create["data"]["id"]
    note_cleanup(note_id)

    created_at = response_create["data"]["created_at"]
    assert response_create["data"]["completed"] is False

    # UPDATE (full PUT)
    updated_title = f"{title} - Updated"
    updated_description = "Updated Description"
    response_update = api_client_auth.update_note(
        note_id, updated_title, updated_description, True, "Work"
    )
    assert response_update["success"] is True
    assert response_update["data"]["id"] == note_id
    assert response_update["data"]["title"] == updated_title
    assert response_update["data"]["description"] == updated_description
    assert response_update["data"]["completed"] is True
    assert response_update["data"]["created_at"] == created_at
    if "updated_at" in response_update["data"]:
        assert response_update["data"]["updated_at"] >= created_at

    # GET BY ID
    response_get = api_client_auth.get_note_by_id(note_id)
    assert response_get["success"] is True
    assert response_get["data"]["id"] == note_id
    assert response_get["data"]["title"] == updated_title
    assert response_get["data"]["completed"] is True

    # LIST
    response_list = api_client_auth.get_all_notes()
    ids = [n["id"] for n in response_list["data"]]
    assert note_id in ids

    # DELETE + verify 404
    response_delete = api_client_auth.delete_note(note_id)
    assert response_delete["success"] is True

    with pytest.raises(requests.exceptions.HTTPError) as ei:
        api_client_auth.get_note_by_id(note_id)
    assert ei.value.response.status_code in {404, 400}
