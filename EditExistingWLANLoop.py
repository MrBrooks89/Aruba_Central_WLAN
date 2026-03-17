import os
import urllib.parse
import json
import argparse
from dotenv import load_dotenv
from pycentral.base import ArubaCentralBase
from pprint import pprint

# Import shared constants and refresh function
from utils import refresh_aruba_token, BASE_URL, CLIENT_ID, CLIENT_SECRET

# Set up command-line arguments
parser = argparse.ArgumentParser(
    description="Update SSID configuration across multiple Aruba Central groups. "
                "NOTE: You must provide a JSON file (e.g., wlan_body.txt) "
                "containing the SSID settings you want to apply using the --wlan_file argument."
)
parser.add_argument("--ssid", required=True, help="SSID name to update")
parser.add_argument("--groups", required=True, 
                    help="Comma-separated list of group names (e.g., 'Store 001,Store 002') "
                         "OR a path to a .txt file containing one group name per line.")
parser.add_argument("--wlan_file", required=True, 
                    help="Path to a JSON file containing the WLAN configuration (e.g., 'wlan_body.txt')")
args = parser.parse_args()

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

# Parse group list from required argument
if args.groups.endswith(".txt"):
    if not os.path.isfile(args.groups):
        raise FileNotFoundError(f"Group file not found: {args.groups}")
    with open(args.groups, "r") as f:
        # Read lines, strip whitespace, and ignore empty lines
        group_identifiers = [line.strip() for line in f if line.strip()]
    print(f"Loaded {len(group_identifiers)} groups from {args.groups}")
else:
    group_identifiers = [g.strip() for g in args.groups.split(",")]

# Specify the SSID to update from command line
ssid_to_update = args.ssid
encoded_ssid_to_update = urllib.parse.quote(ssid_to_update)

# Parse the WLAN configuration body from the JSON file
if not os.path.isfile(args.wlan_file):
    print("Sorry please provide wlan_body.txt with the requried fields if you don't have one use the example on the github repo.")
    exit(1)

try:
    with open(args.wlan_file, "r") as f:
        wlan_body = json.load(f)
except (json.JSONDecodeError, IOError):
    print("Sorry please provide wlan_body.txt with the requried fields if you don't have one use the example on the github repo.")
    exit(1)

# Ensure the SSID provided via --ssid is set in the configuration
if "wlan" in wlan_body:
    wlan_body["wlan"]["essid"] = ssid_to_update
else:
    # Handle the case where the JSON structure doesn't match the expected 'wlan' key
    print("Error: The provided WLAN configuration file must contain a 'wlan' key.")
    print("Sorry please provide wlan_body.txt with the requried fields if you don't have one use the example on the github repo.")
    exit(1)

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
