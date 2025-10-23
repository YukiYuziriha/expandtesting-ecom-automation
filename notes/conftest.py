# notes/conftest.py
import pytest
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
