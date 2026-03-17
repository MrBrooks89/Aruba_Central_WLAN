# Import necessary modules
import os
import argparse
from dotenv import load_dotenv
from pycentral.base import ArubaCentralBase

# Import shared constants and refresh function
from utils import refresh_aruba_token, BASE_URL, CLIENT_ID, CLIENT_SECRET

# Set up command-line arguments (even if none, for --help support)
parser = argparse.ArgumentParser(
    description="Fetch all group names from Aruba Central using pagination."
)
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

# GET groups from Aruba Central
apiPath = "/configuration/v2/groups"
apiMethod = "GET"
limit = 100
offset = 0
all_groups = []
total_groups = 0

try:
    while True:
        apiParams = {"limit": limit, "offset": offset}
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
            else:
                print("Failed to refresh token. Exiting loop.")
                break

        # Process successful response
        if base_resp.get("code") == 200:
            msg = base_resp.get("msg", {})
            groups_batch = msg.get("data", [])
            total_groups = msg.get("total", 0)

            all_groups.extend(groups_batch)

            # If we've collected all groups or if the last batch was empty, exit
            if len(all_groups) >= total_groups or not groups_batch:
                break

            # Increment offset for next page
            offset += limit
        else:
            print(f"Error fetching groups at offset {offset}: {base_resp}")
            break

    # Clean up results for the end user
    if all_groups:
        print(
            f"\n--- Aruba Central Groups (Showing {len(all_groups)} of {total_groups}) ---"
        )
        for group_info in all_groups:
            # Each entry in 'data' is a list [GroupName]
            print(f" {group_info[0]} ")
        print("-" * 50)
    elif not all_groups and total_groups == 0:
        print("\nNo groups found in Aruba Central.")
    else:
        print(f"Error fetching groups: {base_resp}")

except Exception as e:
    print(f"Error occurred: {e}")
