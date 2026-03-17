# Import necessary modules
import urllib.parse
import os
from dotenv import load_dotenv
from pycentral.base import ArubaCentralBase
from pprint import pprint
import json  # Added for json.dumps

# Import shared constants and refresh function from project utils
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

# Specify the group name and the specific SSID name
group_identifier = "Store 028"
ssid_name = "Brookshires Public WiFi"

encoded_group_identifier = urllib.parse.quote(group_identifier)
encoded_ssid_name = urllib.parse.quote(ssid_name)

# GET specific WLAN details from Group from Aruba Central (v2 for clean fields)
apiPath = f"/configuration/v2/wlan/{encoded_group_identifier}/{encoded_ssid_name}"
apiMethod = "GET"

try:
    base_resp = central.command(apiMethod=apiMethod, apiPath=apiPath)

    # Check if the token is expired (401) and refresh it
    if isinstance(base_resp, dict) and base_resp.get("code") == 401:
        new_token = refresh_aruba_token()
        if new_token:
            # Update the central object's token for the retry
            central.central_info["token"]["access_token"] = new_token
            # Retry the original request
            base_resp = central.command(apiMethod=apiMethod, apiPath=apiPath)

    # Debug print removed, focusing on copy-paste format

    # Prepare for clean, copy-paste friendly output
    if isinstance(base_resp, dict) and base_resp.get("code") == 200:
        msg = base_resp.get("msg", {})
        wlan_raw = msg.get("wlan", {})

        print("\n" + "=" * 80)
        print(f" WLAN CONFIGURATION for: {ssid_name} (Group: {group_identifier})")
        print("=" * 80)
        print(
            "\n# Copy and paste the 'wlan_body' dictionary below into EditExistingWLANLoop.py\n"
        )

        # Construct the wlan_body dictionary
        wlan_body_output = {
            "wlan": {
                "essid": wlan_raw.get("essid", ""),
                "name": wlan_raw.get("name", ""),
                "type": wlan_raw.get("type", ""),
                "vlan": wlan_raw.get("vlan", ""),
                "hide_ssid": wlan_raw.get("hide_ssid", False),
                "zone": wlan_raw.get("zone", ""),
                "captive_profile_name": wlan_raw.get("captive_profile_name", ""),
                "wpa_passphrase": wlan_raw.get("wpa_passphrase", ""),
                "bandwidth_limit_peruser_up": wlan_raw.get(
                    "bandwidth_limit_peruser_up", ""
                ),
                "bandwidth_limit_peruser_down": wlan_raw.get(
                    "bandwidth_limit_peruser_down", ""
                ),
                "bandwidth_limit_up": wlan_raw.get("bandwidth_limit_up", ""),
                "bandwidth_limit_down": wlan_raw.get("bandwidth_limit_down", ""),
            }
        }

        # Handle access_rules, which can be complex
        rules_raw = wlan_raw.get("access_rules", [])
        if rules_raw:
            processed_rules = []
            for rule in rules_raw:
                processed_rules.append(
                    {
                        "action": rule.get("action", ""),
                        "eport": rule.get("eport", ""),
                        "ipaddr": rule.get("ipaddr", ""),
                        "match": rule.get("match", ""),
                        "netmask": rule.get("netmask", ""),
                        "protocol": rule.get("protocol", ""),
                        "service_name": rule.get("service_name", ""),
                        "service_type": rule.get("service_type", ""),
                        "sport": rule.get("sport", ""),
                        "throttle_downstream": rule.get("throttle_downstream", ""),
                        "throttle_upstream": rule.get("throttle_upstream", ""),
                    }
                )
            wlan_body_output["wlan"]["access_rules"] = processed_rules

        # Use json.dumps to print the dictionary in a pretty, copy-paste format
        print(json.dumps(wlan_body_output, indent=4))

        print("\n" + "=" * 80)
    else:
        print(f"\n[!] Error fetching WLAN: {base_resp.get('code')}")
        # Retain pprint for error cases for debugging
        pprint(base_resp)

except Exception as e:
    print(f"Error occurred: {e}")
    if "base_resp" in locals():
        print("\nRaw response for debugging:")
        pprint(base_resp)
