import os
import urllib.parse
from dotenv import load_dotenv
from pycentral.base import ArubaCentralBase
from pprint import pprint

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

# List of group names, GUIDs, or serial numbers
group_identifiers = [
    "Store 802",
    "Store 803",
    "Store 804",
    "Store 805",
]

# Specify the SSID to update
ssid_to_update = "Fresh Public WiFi"
encoded_ssid_to_update = urllib.parse.quote(ssid_to_update)

# Define the WLAN configuration body
wlan_body = {
    "wlan": {
        "essid": ssid_to_update,
        "type": "guest",
        "access_rules": [{"action": "allow"}],
        "captive_profile_name": "Captive Portal",
        "bandwidth_limit_peruser_up": "1512",
        "bandwidth_limit_peruser_down": "1512",
    }
}

# Loop through each group and make the API request
for group_identifier in group_identifiers:
    encoded_group_identifier = urllib.parse.quote(group_identifier)
    apiPath = (
        f"/configuration/v2/wlan/{encoded_group_identifier}/{encoded_ssid_to_update}"
    )
    apiMethod = "PATCH"

    print(f"Updating SSID '{ssid_to_update}' in group: {group_identifier}")

    try:
        base_resp = central.command(
            apiMethod=apiMethod, apiPath=apiPath, apiData=wlan_body
        )

        # Check if the token is expired (401) and refresh it
        if isinstance(base_resp, dict) and base_resp.get("code") == 401:
            new_token = refresh_aruba_token()
            if new_token:
                # Update the central object's token for the retry
                central.central_info["token"]["access_token"] = new_token
                # Retry the original request
                base_resp = central.command(
                    apiMethod=apiMethod, apiPath=apiPath, apiData=wlan_body
                )

        # pprint(base_resp)
    except Exception as e:
        print(f"Error occurred updating group {group_identifier}: {e}")
