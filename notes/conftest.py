# notes/conftest.py
from collections.abc import Callable, Iterator

import pytest
import requests

from notes.helpers.api_client import ApiClient
from config import BASE_URL_API


@pytest.fixture(
    scope="function"
)  # isolate auth/token per test; switch to session for speed if safe
def api_client_auth(test_users: dict, profile_name: str) -> ApiClient:
    """Create an API client for the notes API."""
    api_client = ApiClient(BASE_URL_API)
    user = test_users[profile_name]
    api_client.login_user(email=user["email"], password=user["password"])
    return api_client


@pytest.fixture
def note_cleanup(api_client_auth: ApiClient) -> Iterator[Callable[[str], None]]:
    """Register created note ids for automatic teardown."""
    note_ids: list[str] = []

    def register(note_id: str) -> None:
        note_ids.append(note_id)

    yield register

    while note_ids:
        note_id = note_ids.pop()
        try:
            api_client_auth.delete_note(note_id)
        except requests.exceptions.HTTPError as exc:
            if exc.response is None or exc.response.status_code not in {400, 404}:
                raise
