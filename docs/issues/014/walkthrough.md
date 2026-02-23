# Walkthrough - CLI Enhancements (Setup & Separate DBs)

I have added two significant features to the monitoring suite to improve configuration and data storage flexibility.

## Changes Made

### 1. Interactive Setup Wizard (`--setup`)
Created a new module `src/dvm_mesura/setup.py` that provides an interactive CLI wizard.
- Prompts for API keys, credentials, and coordinates.
- Uses current `.env` values as defaults if they exist.
- Saves configuration securely to `.env`.

### 2. Flexible Database Storage and Location Overrides
Refactored the backend initialization in `main.py` to allow for individual database files and location overrides.
- **Separate Databases**: If `--separate` is used, monitors create individual files: `energy.db`, `weather.db`, and `evohome.db`.
- **Location Overrides**: Latitude and Longitude can now be passed via the CLI (`--lat`, `--lon`), overriding `.env` settings.
- **Environment Parity**: Full synchronization between CLI arguments and `.env` settings. All options (intervals, data directory, separate DB flag) can now be configured via either method.
- **Enhanced Setup**: The `--setup` wizard now covers every available configuration option.
- **Credential Overrides**: All sensitive settings (API keys, passwords) can now be provided via CLI flags like `--weather-key`, `--evohome-user`, and `--evohome-pass`.
- **Default (Shared)**: All monitors write to `monitor.db`.
- **Separate**: If `--separate` is used, monitors create individual files: `energy.db`, `weather.db`, and `evohome.db`.
- This provides better data isolation if required by the user.

## Verification Results

### Setup Wizard Test
```bash
=== DVM Mesura Setup Wizard ===
Press Enter to keep the default value [shown in brackets].

Energy Meter API URL [http://p1meter-231dbe.local./api/v1/data]:
...
Configuration saved to .env
```

### Separate DB Verification
Running with `--separate` successfully created:
- `data/energy.db`
- `data/weather.db`
- `data/evohome.db`

All concurrency protections (Locking/WAL) remain active for both shared and separate modes.
