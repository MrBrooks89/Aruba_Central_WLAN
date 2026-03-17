# Aruba Central API Automation

Scripts for automating WLAN/SSID management in Aruba Central.

## Setup
1. Clone the repository.
2. Create a `.env` file with your Aruba Central API credentials:
   ```env
   ARUBA_CLIENT_ID=your_id
   ARUBA_CLIENT_SECRET=your_secret
   ARUBA_ACCESS_TOKEN=initial_token
   ARUBA_REFRESH_TOKEN=initial_refresh_token
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Secure your .env file: To protect your credentials, set the file permissions so that only your user can read it:
   ```
   chmod 600 .env
   ```

## Usage
All scripts (except `GetGroups.py`) now use command-line arguments. Use `--help` on any script for full details.

- **Get All Groups**: `python GetGroups.py`
  - *Automatically loops through all groups in your account using pagination.*
- **Get Simplified WLAN Details**: `python GetWLAN.py --group "Store 028" --ssid "Public WiFi"`
  - *Retrieves a clean view of WLAN settings for a specific SSID.*
- **Get Full WLAN Details**: `python GetWLANFull.py --group "Store 028" --ssid "RetailWiFi"`
  - *Retrieves the full WLAN configuration (filtered for non-empty values).*
- **Batch Edit SSIDs**: `python EditExistingWLANLoop.py --ssid "Guest WiFi" --groups "Store 001,Store 002"`
  - *Updates SSID settings across the specified comma-separated list of groups OR a .txt file (e.g., `--groups my_stores.txt` with one group per line).*
*IMPORTANT:* *You must manually edit the wlan_body dictionary within EditExistingWLANLoop.py to set the desired bandwidth, captive portal, or access rules before execution. To discover all available fields, refer to the official documentation or run GetWLANFull.py. For a concise list of common fields, use GetWLAN.py.*
## Key Features
- **Automatic Pagination**: `GetGroups.py` automatically handles accounts with more than 100 groups.
- **Workflow Flexibility**: Use `GetWLAN.py` to grab a known-good configuration, copy the `wlan_body` output, and paste it into `EditExistingWLANLoop.py` for batch updates.

## Official Documentation
- **Aruba Central Developer Portal**: [https://developer.arubanetworks.com/central/docs/python-using-api-sdk](https://developer.arubanetworks.com/central/docs/python-using-api-sdk)
