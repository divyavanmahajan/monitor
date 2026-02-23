# Issue 016: Provide combine-db script

## Description
User wants a script to merge the data from separate SQLite databases (`energy.db`, `weather.db`, `rooms.db`) into the unified `monitor.db`.
The script must avoid duplicate timestamps.
Additionally, the README.md must be updated to cover all options for the new scripts.

## Tasks
- [x] Inspect the schema of `energy.db`, `weather.db`, and `rooms.db`.
- [x] Create `scripts/combine_db.py`.
- [x] Ensure `scripts/combine_db.py` merges `rooms` table into `evohome` table in `monitor.db` (if schemas allow, or `rooms` -> `rooms`?). Need to map table names correctly. The unified script uses `energy`, `weather`, `evohome`. Wait, did `poll_rooms.py` save to `rooms` table? Needs verification. 
- [x] Ensure the script uses `INSERT OR IGNORE` or similar upsert approach based on timestamps to avoid duplicates. Since there might not be a UNIQUE constraint on `timestamp`, we might need to create it or do conditional inserts.
- [x] Update `README.md` to document the scripts options (`uv run mesura-all`, the python scripts, and `scripts/combine_db.py`).
- [ ] Request user review.
- [ ] Commit and close issue 016.
