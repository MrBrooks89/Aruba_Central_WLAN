# Aruba Central API Project

This project contains scripts for automating configuration changes in Aruba Central, specifically focusing on WLAN/SSID management across multiple groups.

## Project Architecture

### Core Files
- `utils.py`: Shared utility script that manages OAuth2 token refreshing and `.env` updates.
- `EditExistingWLANLoop.py`: Script for updating SSID configurations across multiple groups. **Requires `--ssid` and `--groups` arguments.**
- `GetWLAN.py`: Utility script to retrieve a **simplified/clean** view of WLAN configurations. **Requires `--group` and `--ssid` arguments.**
- `GetWLANFull.py`: Utility script to retrieve the **full (100+ fields)** WLAN configuration. **Requires `--group` and `--ssid` arguments.**
- `GetGroups.py`: Utility script to list **all** Aruba Central groups using automatic pagination.

### Authentication Flow
The project uses OAuth2.0 with a "Refresh-on-401" strategy:
1. Scripts use `pycentral.base.ArubaCentralBase` to interact with the API.
2. If a `401 Unauthorized` response is detected (code 401), the script calls `refresh_aruba_token()` from `utils.py`.
3. `utils.py` uses `requests` to exchange the `ARUBA_REFRESH_TOKEN` for a new access token.
4. The `.env` file is updated automatically using `dotenv.set_key`.
5. The script updates its `ArubaCentralBase` object with the new token and retries the request.

## Usage Guidelines

### Command Line Arguments
Most scripts now require arguments to avoid manual code editing:
- `python GetWLAN.py --group "GroupName" --ssid "SSIDName"`
- `python EditExistingWLANLoop.py --ssid "SSIDName" --groups "Group1,Group2"`
- `python GetGroups.py` (Lists all groups)

Use the `--help` flag on any script to see available options.

### API Constraints
- **Base URL**: Managed in `utils.py` (default: `https://apigw-prod2.central.arubanetworks.com`)
- **Encoding**: Always use `urllib.parse.quote()` for group names and SSIDs in URLs.
- **Library Choice**: Use `pycentral` for all standard API calls (`GET`, `PATCH`, `POST`). Use `requests` in `utils.py` for OAuth2 flows.

### Libraries
- `pycentral`: Main library for configuration tasks.
- `requests`: Used ONLY for OAuth2 token refreshing in `utils.py`.
- `python-dotenv`: Used for managing and programmatically updating the `.env` file.
