# dvm-mesura - Home Automation Monitoring Suite

A robust, unified monitoring solution for home automation systems. It tracks energy usage (HomeWizard), weather data (OpenWeatherMap), and heating/room temperatures (Honeywell Evohome) while storing everything in a centralized SQLite database.

## Table of Contents
- [Installation](#installation)
- [Setup Wizard & Configuration](#setup_wizard)
- [Usage & CLI Options](#usage)
- [macOS Background Daemon](#macos_daemon)
- [Auxiliary Utilities](#auxiliary_utilities)
- [Testing](#testing)

---

<a name="installation"></a>
## 📦 Installation

This project uses [uv](https://github.com/astral-sh/uv) for high-performance dependency management.

### Method 1: Global Tool (Recommended)
Install `dvm-mesura` as a global CLI tool on your system:
```bash
uv tool install dvm-mesura
```

### Method 2: Local Development
Clone the repository and sync dependencies:
```bash
uv sync
```

---

<a name="setup_wizard"></a>
## 🛠 Setup Wizard & Configuration

The suite requires configuration for API keys and credentials. You can handle this easily using the interactive **Setup Wizard**.

### Running the Wizard
```bash
# If installed as a tool
mesura-all --setup

# If running locally
uv run mesura-all --setup
```

The wizard will guide you through:
- **Energy Meter**: API URL and polling interval.
- **Weather**: OpenWeatherMap API Key, coordinates, and interval.
- **Evohome**: Username/Email, Password, and interval.
- **Data Storage**: Preferred directory and database mode (Unified vs. Separate).

### Configuration Variables
All settings are stored in a `.env` file in the project directory.

| Environment Variable | Description | CLI Override | Default |
|----------------------|-------------|--------------|---------|
| `DATA_DIR` | Directory for databases/CSVs | `--data-dir` | `data` |
| `ENERGY_API_URL` | HomeWizard P1 API URL | `--energy-api` | `http://p1meter-231dbe.local./api/v1/data` |
| `ENERGY_INTERVAL` | Polling frequency | `--energy-interval` | `1m` |
| `OPENWEATHER_API_KEY`| OpenWeatherMap API Key | `--weather-key` | [None] |
| `WEATHER_INTERVAL` | Polling frequency | `--weather-interval`| `10m` |
| `LATITUDE` | Site latitude | `--lat` | `50.83172` |
| `LONGITUDE` | Site longitude | `--lon` | `5.76712` |
| `EVOHOME_USERNAME` | Honeywell TCC Username | `--evohome-user` | [None] |
| `EVOHOME_PASSWORD` | Honeywell TCC Password | `--evohome-pass` | [None] |
| `EVOHOME_INTERVAL` | Polling frequency | `--evohome-interval`| `5m` |
| `SEPARATE_DBS` | Store data in separate files| `--separate` | `false` |

---

<a name="usage"></a>
## 🚀 Usage & CLI Options

### Running the Suite
The primary entry point is `mesura-all`, which starts all configured monitors concurrently.

```bash
# Start all monitors
mesura-all

# Run with overrides
mesura-all --energy-interval 30s --separate
```

### Individual Monitors
You can also run monitors independently:
- `mesura-energy`: Only Energy Meter
- `mesura-weather`: Only OpenWeatherMap
- `mesura-evohome`: Only Honeywell Evohome

### Inspecting Data
Use `mesura-show` to quickly view recent database records in CSV format.
```bash
# Show last 5 rows of all tables
mesura-show

# Show last 10 rows of weather data
mesura-show --table weather -n 10
```

---

<a name="macos_daemon"></a>
## 🖥 macOS Background Daemon

To run `mesura-all` continuously in the background (even after restarts), use the built-in `mesura-daemon` tool.

### 1. Installation
During installation, the wizard will run to ensure your variables are correct. It will also ask if you want to **embed settings** directly into the system plist (useful for headless environments).

```bash
# Standard install
mesura-daemon --install

# Install if using uvx
uvx dvm-mesura mesura-daemon --install --uvx
```

### 2. Management Commands
| Command | Action |
|---------|--------|
| `mesura-daemon --check` | Verify if the daemon is running |
| `mesura-daemon --logs` | Tail the last 20 lines of daemon output/errors |
| `mesura-daemon --unload`| Temporarily stop the daemon |
| `mesura-daemon --start` | Restart an unloaded daemon |
| `mesura-daemon --uninstall`| Completely remove the daemon from macOS |
| `mesura-daemon --env-check`| **Troubleshoot**: Show .env path and active variables |

### 3. Troubleshooting: "Operation not permitted"
macOS **TCC** (Privacy Protections) blocks background daemons from reading sensitive folders like `~/Documents`, `~/Desktop`, or `~/Downloads`.

If your logs show `PermissionError: [Errno 1] Operation not permitted`, **move your project folder** to a non-protected location:
```bash
mv ~/Documents/projects/monitor ~/mesura
cd ~/mesura
mesura-daemon --install
```

---

<a name="auxiliary_utilities"></a>
## 🛠 Auxiliary Utilities

### Migration Tools
- **`mesura-combine-db`**: Migrates historical data from legacy `.db` files (`weatherdata.db`, etc.) into the unified `monitor.db`.
- **`mesura-combine-csv`**: Imports existing CSV logs into the SQLite database while skipping duplicates.

### Export Tools
- **`mesura-export-csv`**: Extract SQLite data back into original CSV format for backups or external analysis.

---

<a name="testing"></a>
## 🧪 Testing

Run the comprehensive test suite using `pytest`:
```bash
uv run pytest
```

The suite includes coverage for polling logic, database schema evolution, and API mocking.
