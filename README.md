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

- **Get All Groups**: 
   ```
   python GetGroups.py
   ```
   *Automatically loops through all groups in your account using pagination.*
- **Get Simplified WLAN Details**: 
   ```
   python GetWLAN.py --group "Group1" --ssid "Public WiFi"
   ```
   *Retrieves a clean view of WLAN settings for a specific SSID.*
- **Get Full WLAN Details**: 
   ```
   python GetWLANFull.py --group "Group1" --ssid "Public WiFi"
   ```
   *Retrieves the full WLAN configuration (filtered for non-empty values).*
- **Batch Edit SSIDs**: 
   ```
   python EditExistingWLANLoop.py --ssid "Public WiFi" --groups "Group1,Group2" --wlan_file wlan_body.txt
   ```
   *Updates SSID settings across the specified comma-separated list of groups OR a .txt file (e.g., `--groups my_groups.txt` with one group per line). This requires a JSON file containing the WLAN configuration settings.*
**IMPORTANT:** *You must provide a JSON file (e.g., `wlan_body.txt`) with the desired settings (bandwidth, captive portal, access rules, etc.) using the `--wlan_file` argument. If you don't have one, use the provided `wlan_body.txt` example. To discover all available fields, run `GetWLANFull.py` or `GetWLAN.py`. You can also refer to the developer documentation.*
## Key Features
- **Automatic Pagination**: `GetGroups.py` automatically handles accounts with more than 100 groups.
- **Workflow Flexibility**: Use `GetWLAN.py` to grab a known-good configuration, save it to a JSON file (e.g., `wlan_body.txt`), and use it with `EditExistingWLANLoop.py` for batch updates.

## Official Documentation
- **Aruba Central Developer Portal**: [https://developer.arubanetworks.com/central/docs/python-using-api-sdk](https://developer.arubanetworks.com/central/docs/python-using-api-sdk)
