# Import necessary modules
import argparse
import urllib.parse
import os
import json
from dotenv import load_dotenv
from pycentral.base import ArubaCentralBase
from pprint import pprint

# Import shared constants and refresh function from project utils
from utils import refresh_aruba_token, BASE_URL, CLIENT_ID, CLIENT_SECRET

# Set up command-line arguments
parser = argparse.ArgumentParser(description="Get full WLAN configuration for a specific SSID in an Aruba Central group.")
parser.add_argument("--group", required=True, help="Aruba Central group name")
parser.add_argument("--ssid", required=True, help="SSID name to fetch configuration for")
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

# Use values from command-line arguments
group_identifier = args.group
ssid_name = args.ssid

encoded_group_identifier = urllib.parse.quote(group_identifier)
encoded_ssid_name = urllib.parse.quote(ssid_name)

# THE FULL_WLAN ENDPOINT
apiPath = f"/configuration/full_wlan/{encoded_group_identifier}/{encoded_ssid_name}"
apiMethod = "GET"


def ensure_dict(data):
    """Helper to ensure API response is a dictionary."""
    if isinstance(data, str):
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {"code": 500, "msg": data}
    return data


def extract_simple_value(data):
    """Recursively extracts the 'value' key or returns data if not a dict with 'value'."""
    if isinstance(data, dict) and "value" in data:
        return extract_simple_value(
            data["value"]
        )  # Recurse in case value itself is a dict with value
    if isinstance(data, dict):
        # If it's a dict but no 'value' key, process its items
        return {
            k: extract_simple_value(v)
            for k, v in data.items()
            if extract_simple_value(v) not in [None, "", [], {}]
        }
    if isinstance(data, list):
        # If it's a list, process each item
        return [
            extract_simple_value(item)
            for item in data
            if extract_simple_value(item) not in [None, "", [], {}]
        ]
    return data


try:
    # Make the API call using pycentral
    base_resp = central.command(apiMethod=apiMethod, apiPath=apiPath)
    base_resp = ensure_dict(base_resp)

    # Token Refresh Logic
    if isinstance(base_resp, dict) and base_resp.get("code") == 401:
        new_token = refresh_aruba_token()
        if new_token:
            central.central_info["token"]["access_token"] = new_token
            base_resp = central.command(apiMethod=apiMethod, apiPath=apiPath)
            base_resp = ensure_dict(base_resp)

    # Handle the successful response
    if isinstance(base_resp, dict) and base_resp.get("code") == 200:
        msg = base_resp.get("msg", {})

        if isinstance(msg, str):
            try:
                msg = json.loads(msg)
            except:
                pass

        wlan_data = msg.get("wlan", {}) if isinstance(msg, dict) else {}

        print(f"\n--- WLAN CONFIGURATION: {ssid_name} ({group_identifier}) ---")

        # 1. Print WLAN Fields (Filtered for non-empty and extracting 'value')
        if isinstance(wlan_data, dict):
            print("\n[ WLAN SETTINGS ]")
            for key, value in sorted(wlan_data.items()):
                extracted = extract_simple_value(value)
                if extracted not in [None, "", [], {}]:
                    print(f"  {key}: {extracted}")

        # 2. Print Access Rules (Filtered for non-empty and extracting 'value')
        if isinstance(msg, dict):
            rule = msg.get("access_rule") or msg.get("access_rules")
            if rule:
                if isinstance(rule, list):
                    rule = rule[0]  # Take the first rule if it's a list
                print("\n[ ACCESS RULE ]")
                if isinstance(rule, dict):
                    extracted_rule = extract_simple_value(rule)
                    if isinstance(extracted_rule, dict):
                        for r_key, r_val in sorted(extracted_rule.items()):
                            if r_val not in [None, "", [], {}]:
                                print(f"  {r_key}: {r_val}")
                    elif extracted_rule not in [None, "", [], {}]:
                        print(f"  rule_data: {extracted_rule}")

        print("\n" + "-" * 50)
    else:
        print(
            f"\n[!] Error fetching Full WLAN Details: {base_resp.get('code', 'Unknown')}"
        )
        pprint(base_resp)

except Exception as e:
    print(f"\n[!] An unexpected error occurred: {e}")
