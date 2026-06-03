import requests
import os
from dotenv import load_dotenv, set_key

# Load environment variables from .env
load_dotenv()

# Aruba Central Constants
CLIENT_ID = os.getenv("ARUBA_CLIENT_ID")
CLIENT_SECRET = os.getenv("ARUBA_CLIENT_SECRET")
BASE_URL = "https://apigw-prod2.central.arubanetworks.com"

def refresh_aruba_token():
    """Refreshes the access token using the refresh token and updates .env."""
    print("Access token expired. Attempting to refresh...")
    refresh_token = os.getenv("ARUBA_REFRESH_TOKEN")

    if not all([CLIENT_ID, CLIENT_SECRET, refresh_token]):
        print("Error: Missing CLIENT_ID, CLIENT_SECRET, or REFRESH_TOKEN in .env")
        return None

    url = f"{BASE_URL}/oauth2/token"
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            data = response.json()
            new_access = data["access_token"]
            new_refresh = data.get("refresh_token", refresh_token)

            # Update .env file and current session environment
            set_key(".env", "ARUBA_ACCESS_TOKEN", new_access)
            set_key(".env", "ARUBA_REFRESH_TOKEN", new_refresh)
            os.environ["ARUBA_ACCESS_TOKEN"] = new_access
            os.environ["ARUBA_REFRESH_TOKEN"] = new_refresh

            print("Token refreshed successfully and .env updated.")
            return new_access
        else:
            print(f"Failed to refresh token: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception during token refresh: {e}")
        return None
