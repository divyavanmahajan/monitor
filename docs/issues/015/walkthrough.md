# Issue 015 Walkthrough: Architecture Documentation Update

## Goal Achieved
The previous documentation in the `docs/` folder (such as the old `Architecture.md` and `Poll*.md` instructions) had been deleted as part of the transition away from independent bash scripts (`monitor_all.sh`) toward a modern Python `asyncio` architecture. 

This issue successfully tracked the creation of a brand new `Architecture.md` file that accurately describes the newly unified monitoring suite (`dvm_mesura`).

## Changes Made
- Created `docs/Architecture.md`.
- Documented the **High-Level Overview** of the unified suite.
- Documented the **Core Components**:
  - `dvm_mesura.main` (Entrypoint and Dependency Injection).
  - `dvm_mesura.core.controller` (Polling logic, execution loop).
  - `dvm_mesura.monitors.*` (Energy, Weather, Evohome data fetchers).
  - `dvm_mesura.backends.*` (SQLite and CSV storage adapters).
- Documented the **Data Flow** cycle with a Mermaid flowchart diagram to visualize how a fetching cycle writes to multiple backends.
- Documented the **Concurrency & Thread Safety** mechanisms specifically detailing how Python `asyncio` interacts with `sqlite3` using Locks, `to_thread` offloading, and the `WAL` journal mode to prevent "database is locked" errors.

## Validation
- The `Architecture.md` accurately represents the current source code under `src/dvm_mesura/`.
- The new document replaces the previously confusing and fragmented legacy scripts documentation.
