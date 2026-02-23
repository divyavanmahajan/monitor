# Architecture Documentation Plan

## Goal
Create a comprehensive `docs/Architecture.md` that explains the new `dvm_mesura` unified monitoring suite.

## Proposed Structure for Architecture.md
1. **Introduction / High-Level Overview**:
   - The Home Automation Monitor suite orchestrates multiple data-gathering monitors into a unified, asynchronous execution loop.
2. **Core Components**:
   - **Monitors** (`dvm_mesura.monitors.*`): Standardized interface for fetching data (Energy, Weather, Evohome).
   - **Backends** (`dvm_mesura.backends.*`): Standardized interface for storing data (SQLite, CSV).
   - **Controllers** (`dvm_mesura.core.controller`): Manage the polling loop and data dispatch.
   - **Main Entrypoint** (`dvm_mesura.main`): Wires dependency injection based on CLI and `.env` settings.
3. **Data Flow**:
   - Monitor `fetch()` -> Controller -> Backends `write()`.
4. **Concurrency & Thread Safety**:
   - Built on Python's `asyncio` for non-blocking network I/O.
   - Database writes are handled using `asyncio.to_thread` and an `asyncio.Lock()` to ensure thread-safe SQLite operations, with `WAL` mode enabled for performance.

## User Review Required
Does this outline cover everything you'd like to see in the new Architecture document? Are there any specific diagrams or additional details you'd like included?
