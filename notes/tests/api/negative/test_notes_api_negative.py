from uuid import uuid4

import pytest
import requests

from config import BASE_URL_API
from notes.helpers.api_client import ApiClient


@pytest.mark.notes
@pytest.mark.api
def test_login_rejects_invalid_credentials(test_users: dict, profile_name: str) -> None:
    client = ApiClient(BASE_URL_API)
    user = test_users[profile_name]

    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        client.login_user(user["email"], "wrong-password")

    assert excinfo.value.response is not None
    assert excinfo.value.response.status_code == 401


@pytest.mark.notes
@pytest.mark.api
@pytest.mark.parametrize(
    "operation",
    ("create_note", "get_all_notes", "get_note_by_id", "delete_note", "update_note"),
)
def test_requires_authentication_for_note_operations(operation: str) -> None:
    client = ApiClient(BASE_URL_API)

    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        if operation == "create_note":
            client.create_note("unauth note", "should fail")
        elif operation == "get_all_notes":
            client.get_all_notes()
        elif operation == "get_note_by_id":
            client.get_note_by_id("unauthorized-id")
        elif operation == "delete_note":
            client.delete_note("unauthorized-id")
        elif operation == "update_note":
            client.update_note("unauthorized-id", "title", "description", True, "Home")
        else:
            pytest.fail(f"Unhandled operation: {operation}")

    assert excinfo.value.response is not None
    assert excinfo.value.response.status_code == 401


@pytest.mark.notes
@pytest.mark.api
def test_get_note_by_id_not_found(
    api_client_auth: ApiClient,
) -> None:
    missing_note_id = f"missing-{uuid4().hex}"

    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        api_client_auth.get_note_by_id(missing_note_id)

    assert excinfo.value.response is not None
    assert excinfo.value.response.status_code in {400, 404}


@pytest.mark.notes
@pytest.mark.api
def test_create_note_rejects_invalid_category(
    api_client_auth: ApiClient,
) -> None:
    invalid_category = "Travel"

    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        api_client_auth.create_note("invalid cat title", "desc", invalid_category)

    assert excinfo.value.response is not None
    assert excinfo.value.response.status_code in {400, 422}
