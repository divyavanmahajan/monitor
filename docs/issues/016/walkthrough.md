# Issue 016 Walkthrough: `combine_db.py` Data Migration

## Goal Achieved
The user requested a script exposed in the project to migrate and combine historical discrete databases (`energy.db`, `weather.db`, `rooms.db`) into the newly unified `monitor.db` backend, guaranteeing that no duplicate rows are created based on timestamps. Additionally, `README.md` needed updating to document script options.

## Changes Made
- Created `scripts/combine_db.py`.
- **Intelligent Database Mapping**: The Python script automatically detects the presence of legacy and current detached databases and maps them to the appropriate `monitor.db` target tables:
  - `weatherdata.db` (legacy) -> `weather` table.
  - `rooms.db` (legacy) -> `evohome` table.
  - `energy.db` -> `energy` table.
- **Deduplication Logic**: When inserting mapped rows, the script checks the `dest_table` for conflicting timestamps and skips rows using an explicit `WHERE timestamp NOT IN (SELECT timestamp FROM {dest_table})` filter to completely avoid primary key locking requirements or duplicates.
- Updated `README.md` to cleanly separate "Unified vs Separate" database instructions and added an "Auxiliary Scripts" section explaining how to run `uv run python scripts/combine_db.py`.

## Validation
- Ran the `combine_db.py` script locally on the actual files stored in `data/`. 
- Successfully observed 2443 weather rows and 3236 evohome rows immediately transition into `data/monitor.db`, along with 4 recent energy reads. Subsequent runs correctly inserted exactly 0 duplicate rows.
