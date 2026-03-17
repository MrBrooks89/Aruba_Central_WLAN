import os
import urllib.parse
import json
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


def ensure_dict(data):
    """Helper to ensure API response is a dictionary."""
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {"code": 500, "msg": data}
    return data


# List of group names, GUIDs, or serial numbers
group_identifiers = [
    "Store 002",
    "Store 003",
    "Store 004",
    "Store 005",
    "Store 006",
    "Store 007",
    "Store 008",
    "Store 009",
    "Store 011",
    "Store 013",
    "Store 015",
    "Store 017",
    "Store 018",
    "Store 019",
    "Store 020",
    "Store 021",
    "Store 022",
    "Store 024",
    "Store 025",
    "Store 026",
    "Store 028",
    "Store 030",
    "Store 035",
    "Store 036",
    "Store 037-470",
    "Store 039",
    "Store 045",
    "Store 047",
    "Store 049",
    "Store 050",
    "Store 051",
    "Store 054",
    "Store 056",
    "Store 060",
    "Store 061",
    "Store 064",
    "Store 066",
    "Store 067",
    "Store 068",
    "Store 071",
    "Store 075",
    "Store 078",
    "Store 079",
    "Store 080",
    "Store 082",
    "Store 089",
    "Store 094",
    "Store 097",
    "Store 107",
    "Store 108",
    "Store 109",
    "Store 110",
    "Store 118",
    "Store 119",
    "Store 125",
    "Store 126",
    "Store 127",
    "Store 133",
    "Store 137",
    "Store 138",
    "Store 139",
]

# Specify the SSID to update
ssid_to_update = "Super1Foods Public WIFI"
encoded_ssid_to_update = urllib.parse.quote(ssid_to_update)

# Define the WLAN configuration body
wlan_body = {
    "wlan": {
        "essid": ssid_to_update,
        "type": "guest",
        "access_rules": [{"action": "allow"}],
        "captive_profile_name": "Super1 Captive Portal",
        "bandwidth_limit_peruser_up": "3072",
        "bandwidth_limit_peruser_down": "3072",
    }
}

# Loop through each group and make the API request
for group_identifier in group_identifiers:
    encoded_group_identifier = urllib.parse.quote(group_identifier)
    apiPath = (
        f"/configuration/v2/wlan/{encoded_group_identifier}/{encoded_ssid_to_update}"
    )
    apiMethod = "PATCH"

    print(f"\nUpdating SSID '{ssid_to_update}' in group: {group_identifier}")

    try:
        base_resp = central.command(
            apiMethod=apiMethod, apiPath=apiPath, apiData=wlan_body
        )
        base_resp = ensure_dict(base_resp)

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
                base_resp = ensure_dict(base_resp)

        if base_resp.get("code") == 200:
            print(f"  [SUCCESS] Group {group_identifier} updated.")
        else:
            print(
                f"  [FAILED] Group {group_identifier} failed: {base_resp.get('code')} - {base_resp.get('msg')}"
            )

    except Exception as e:
        print(f"Error occurred updating group {group_identifier}: {e}")
