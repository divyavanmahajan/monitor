# Issue 015: Write Architecture.md

## Description
The previous documentation files (Architecture.md, UserGuide.md, etc.) have been cleaned up because they reflected the old, fragmented architecture with separate polling scripts.
The project now uses a unified `dvm_mesura` module running on `asyncio`.
We need to write a new `docs/Architecture.md` that describes this new system accurately.

## Tasks
- [x] Create `docs/Architecture.md` describing the core components (Main, Controller, Monitors, Backends).
- [x] Describe the data flow (Monitors -> Controller -> Backends).
- [x] Describe the concurrency model (`asyncio`, `to_thread`, SQLite WAL + Locks).
- [ ] Review documentation with the user.
- [ ] Commit changes referencing issue #15.
- [ ] Close issue 015.
