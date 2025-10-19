# shared/helpers/api_client.py
import requests


class ApiClient:
    def __init__(self, BASE_URL_API: str) -> None:
        self.base_url = BASE_URL_API

    def login_user(self, email: str, password: str) -> dict:
        url = f"{self.base_url}/users/login"

        data = {"email": email, "password": password}

        response = requests.post(url, data=data)
        response.raise_for_status()

        return response.json()
