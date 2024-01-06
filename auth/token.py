import os
import requests


def get_token(
    url=f"https://{os.environ['AUTH0_DOMAIN']}/oauth/token",
    client_id=os.environ["AUTH0_CLIENT_ID"],
    client_secret=os.environ["AUTH0_CLIENT_SECRET"],
    audience=os.environ["AUTH0_AUDIENCE"],
    grant_type="client_credentials",
):
    # Define the request body
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": audience,
        "grant_type": grant_type,
    }
    # Make a request to the API to get the OAuth token
    response = requests.post(url, json=data)
    oauth_token = response.json()["access_token"]

    # Set the environment variable
    os.environ["OAUTH_TOKEN"] = oauth_token
