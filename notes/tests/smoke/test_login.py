# notes/tests/smoke/test_login.py
import pytest
from notes.helpers.api_client import ApiClient
from config import BASE_URL_API


@pytest.mark.notes
@pytest.mark.api
@pytest.mark.smoke
def test_login(test_users: dict, profile_name: str) -> None:
    api_client = ApiClient(BASE_URL_API)
    user = test_users[profile_name]
    response = api_client.login_user(user["email"], user["password"])

    assert response["success"] is True, "Login successful"
    assert "token" in response["data"], "Token is present"
