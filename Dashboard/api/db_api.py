import requests
from os import environ
from auth.token import get_token
from typing import Union


class DBApi:
    def __init__(self) -> None:
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer " + environ["OAUTH_TOKEN"],
        }

    def get(self, endpoint) -> dict:
        try:
            result = requests.get(environ["DB_API"] + endpoint, headers=self.headers)
            if result.status_code == 401:
                get_token()
                self.headers["Authorization"] = "Bearer " + environ["OAUTH_TOKEN"]
                return self.get(endpoint)

            if "error" in result.text:
                print(result.text)
            return result.json()

        except Exception as e:
            return {"error": e}

    def get_with_data(self, endpoint, data)-> Union[dict, list]:
        try:
            result = requests.get(
                environ["DB_API"] + endpoint,
                headers=self.headers,
                json=data,
            )
            if "error" in result.text:
                print(result.text)
            return result.json()
        except Exception as e:
            return {"error": e}

    def post(self, endpoint, data)-> Union[dict, list]:
        try:
            result = requests.post(
                environ["DB_API"] + endpoint,
                headers=self.headers,
                json=data,
            )
            if "error" in result.text:
                print(result.text)
            return result.json()
        except Exception as e:
            return {"error": e}
