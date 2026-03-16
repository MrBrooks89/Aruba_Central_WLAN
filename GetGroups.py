# Import necessary modules
import os
from dotenv import load_dotenv
from pycentral.base import ArubaCentralBase

# Import shared constants and refresh function
from utils import refresh_aruba_token, BASE_URL, CLIENT_ID, CLIENT_SECRET

load_dotenv()

# Get the initial access token
access_token = os.getenv("ARUBA_ACCESS_TOKEN")

if not access_token:
    raise ValueError("Environment variable ARUBA_ACCESS_TOKEN not set")

# Create an instance of ArubaCentralBase using API access token
central_info = {
    "base_url": BASE_URL,
    "token": {"access_token": access_token},
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
}
ssl_verify = True
central = ArubaCentralBase(central_info=central_info, ssl_verify=ssl_verify)

# GET groups from Aruba Central
apiPath = "/configuration/v2/groups"
apiMethod = "GET"
apiParams = {"limit": 20, "offset": 0}

try:
    base_resp = central.command(
        apiMethod=apiMethod, apiPath=apiPath, apiParams=apiParams
    )

    # Check if the token is expired (401) and refresh it
    if isinstance(base_resp, dict) and base_resp.get("code") == 401:
        new_token = refresh_aruba_token()
        if new_token:
            # Update the central object's token for the retry
            central.central_info["token"]["access_token"] = new_token
            # Retry the original request
            base_resp = central.command(
                apiMethod=apiMethod, apiPath=apiPath, apiParams=apiParams
            )

    # Clean up results for the end user
    if base_resp.get("code") == 200:
        msg = base_resp.get("msg", {})
        groups = msg.get("data", [])
        total = msg.get("total", 0)

        print(f"\n--- Aruba Central Groups (Showing {len(groups)} of {total}) ---")
        for group_info in groups:
            # Each entry in 'data' is a list [GroupName]
            print(f" • {group_info[0]}")
        print("-" * 50)
    else:
        print(f"Error fetching groups: {base_resp}")

except Exception as e:
    print(f"Error occurred: {e}")
