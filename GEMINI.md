# Aruba Central API Project

This project contains scripts for automating configuration changes in Aruba Central, specifically focusing on WLAN/SSID management across multiple groups.

## Project Architecture

### Core Files
- `utils.py`: Shared utility script that manages OAuth2 token refreshing and `.env` updates.
- `EditExistingWLANLoop.py`: Script for updating SSID configurations across multiple groups using `pycentral`.
- `GetWLAN.py`: Utility script to retrieve a **simplified/clean** view of WLAN configurations for a specific SSID in a group.
- `GetWLANFull.py`: Utility script to retrieve the **full (100+ fields) and filtered** WLAN configuration for a specific SSID, extracting only non-empty values for easier consumption.
- `GetGroups.py`: Utility script to list Aruba Central groups.
- `.env`: Contains sensitive API credentials and tokens.

### Authentication Flow
The project uses OAuth2.0 with a "Refresh-on-401" strategy:
1. Scripts use `pycentral.base.ArubaCentralBase` to interact with the API.
2. If a `401 Unauthorized` response is detected (code 401), the script calls `refresh_aruba_token()` from `utils.py`.
3. `utils.py` uses `requests` to exchange the `ARUBA_REFRESH_TOKEN` for a new access token.
4. The `.env` file is updated automatically using `dotenv.set_key`.
5. The script updates its `ArubaCentralBase` object with the new token and retries the request.

## Reference Documentation
For all API schema, endpoints, and SDK usage, refer to the official documentation:
- **Aruba Central API Reference**: [https://developer.arubanetworks.com/central/reference/apifull_wlanupdate_wlan](https://developer.arubanetworks.com/central/reference/apifull_wlanupdate_wlan)
- **Python SDK Guide**: [https://developer.arubanetworks.com/central/docs/python-using-api-sdk](https://developer.arubanetworks.com/central/docs/python-using-api-sdk)

## Environment Variables
Ensure these are present in your `.env` file:
- `ARUBA_ACCESS_TOKEN`: Current bearer token.
- `ARUBA_REFRESH_TOKEN`: Token used to generate a new access token.
- `ARUBA_CLIENT_ID`: API Gateway Client ID.
- `ARUBA_CLIENT_SECRET`: API Gateway Client Secret.

## Development Guidelines

### API Constraints
- **Base URL**: Managed in `utils.py` (default: `https://apigw-prod2.central.arubanetworks.com`)
- **Encoding**: Always use `urllib.parse.quote()` for group names and SSIDs in URLs.
- **Library Choice**: Use `pycentral` for all standard API calls (`GET`, `PATCH`, `POST`). Use `requests` in `utils.py` for OAuth2 flows.

### Libraries
- `pycentral`: Main library for configuration tasks.
- `requests`: Used ONLY for OAuth2 token refreshing in `utils.py`.
- `python-dotenv`: Used for managing and programmatically updating the `.env` file.
