# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.4] - 2026-02-23

### Added
- `--env-check` option to `mesura-daemon` to troubleshoot environment variables, showing `.env` path, raw file contents, and active process variables.

## [1.1.3] - 2026-02-23

### Added
- `--start` option to `mesura-daemon` to reload and start the LaunchDaemon if it was previously unloaded.

## [1.1.2] - 2026-02-23

### Changed
- `mesura-daemon --install` now always runs the configuration wizard to ensure environment variables are up-to-date before starting the service.

## [1.1.1] - 2026-02-23

### Added
- Integrated setup wizard into `mesura-daemon --install` to automatically create `.env` if missing.
- Post-installation summary in `mesura-daemon` indicating the absolute path where monitoring data files will reside.
- Ability for `setup_wizard` to target a specific `.env` path.

## [1.1.0] - 2026-02-23

### Added
- `mesura-daemon` CLI tool for seamlessly deploying and managing macOS LaunchDaemons running `mesura-all` in the background.
- Support for `uvx` isolated ephemeral environments natively within `mesura-daemon` via the `--uvx` flag. 
- Integrated macOS Privacy (TCC) folder restriction warnings for protected boundaries like `~/Documents` and `~/Desktop` within `mesura-daemon`.
- `DAEMON-MAC.md` detailed instruction file mapped out with automated deployment vs manual routines.
- `mesura-show` script to display recent unified database records (`monitor.db`) formatted purely as CSV for fast inspections.
- `export_csv.py` and `mesura-export-csv` command to reverse-export the unified sqlite tracking instances natively back into original static standalone CSV files.
- `combine_csv.py` and `mesura-combine-csv` CLI hooks designed to merge sprawling, legacy CSV databases efficiently into the main `monitor.db`. 
- `combine_db.py` transitioned internally into `mesura-combine-db` to systematically swallow and import legacy disconnected DB archives safely based on strict timestamps.

## [1.0.0] - 2026-02-23

### Added
- Unified package format transitioning from single-script configurations to a robust `pyproject.toml` definition under the toolchain `uv`.
- GitHub Actions CI/CD to fully orchestrate automatic packaging and uploading to PyPI using Trusted Publisher architectures.
- Built-in dynamic `.env` handling paired with `monitor.db` consolidation to store `energy`, `weather`, and `evohome` inside a single unified SQLite file cleanly avoiding duplicates.
- Central execution script `mesura-all` alongside dedicated `mesura-energy`, `mesura-evohome`, and `mesura-weather` console hooks.
- Extensively reorganized `docs/` logic explicitly delineating user walkthroughs and legacy operations.
