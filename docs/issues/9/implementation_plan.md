# Standardize CLI arguments for poll_evohome_standalone.py

Align the command-line interface of the Evohome polling script with the other polling scripts in the suite.

## Proposed Changes

### [Component Name] Standardizing poll_evohome_standalone.py

#### [MODIFY] [poll_evohome_standalone.py](file:///Users/divya/Documents/projects/homeautomation/monitor/scripts/poll_evohome_standalone.py)
- **Imports**: Add `argparse`, `re`, `select`, `threading`.
- **Helpers**:
  - Add `parse_interval(interval_str: str) -> float` to handle time suffixes (s, m).
  - Add `format_time_display(timestamp: str) -> str` for table view.
  - Add `display_table(data_rows, show_header)` to show a clean table of zone temperatures.
- **Main Loop**:
  - Replace hardcoded `interval` and `output_file` with `argparse` results.
  - Add support for `-i`, `-o`, `--overwrite`, and `--noshow`.
  - Implement the `read_keyboard` thread to handle the 'L' key for showing headers.
  - Update the polling loop to use a small sleep increment for responsive keyboard handling.

## Verification Plan

### Automated Tests
- N/A

### Manual Verification
1. Run `python scripts/poll_evohome_standalone.py --help` to verify the new options.
2. Run with different intervals (e.g., `-i 30s`) and check frequency.
3. Verify output is correctly written to the specified CSV and SQLite database.
4. Test `--noshow` to ensure it runs silently in the background.
5. Test 'L' key during execution to toggle the header in the table view.
