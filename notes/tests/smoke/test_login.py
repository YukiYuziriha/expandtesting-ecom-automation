# notes/tests/smoke/test_login.py
from notes.helpers.api_client import ApiClient
from config import BASE_URL_API


def test_login(test_users: dict) -> None:
    api_client = ApiClient(BASE_URL_API)
    user = test_users["profile1"]
    response = api_client.login_user(user["email"], user["password"])

    assert response["success"] is True, "Login successful"
    assert "token" in response["data"], "Token is present"
