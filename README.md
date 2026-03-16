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
- **Get Groups**: `python GetGroups.py` (Edit script limit to desired number currently set to 20)
- **Get Simplified WLAN Details**: `python GetWLAN.py` (Edit script to change group/SSID)
- **Get Full WLAN Details**: `python GetWLANFull.py` (Edit script to change group/SSID - outputs filtered non-empty values)
- **Batch Edit SSIDs**: `python EditExistingWLANLoop.py`

## Architecture
This project uses a modular design:
- **`utils.py`**: Handles shared configuration and automatic token refreshing. It updates the `.env` file automatically when tokens expire.
- **`pycentral`**: All Aruba Central configuration commands are performed via the `pycentral` library for consistency and better error handling.

## Official Documentation
- **Aruba Central Developer Portal**: [https://developer.arubanetworks.com/central/docs/python-using-api-sdk](https://developer.arubanetworks.com/central/docs/python-using-api-sdk)
