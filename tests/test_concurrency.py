import pytest
import asyncio
import sqlite3
import random
from pathlib import Path
from dvm_mesura.backends.sqlite import SQLiteBackend

@pytest.mark.asyncio
async def test_sqlite_concurrency(tmp_path):
    """Test multiple concurrent writes to the same SQLite database."""
    db_path = tmp_path / "concurrency.db"
    num_tasks = 20
    writes_per_task = 10
    
    # Use multiple instances to verify class-level locking
    backends = [SQLiteBackend(db_path) for _ in range(num_tasks)]
    
    async def task_worker(task_id: int):
        backend = backends[task_id]
        for i in range(writes_per_task):
            data = {
                "timestamp": f"2026-02-23T11:00:{task_id:02d}.{i:02d}Z",
                "task_id": task_id,
                "iteration": i,
                "random_val": random.random()
            }
            # Slightly offset tasks to increase chance of overlap
            await asyncio.sleep(random.uniform(0, 0.01))
            await backend.write(data, "stress_test")

    # Start all tasks concurrently
    await asyncio.gather(*(task_worker(i) for i in range(num_tasks)))
    
    # Verify results
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM stress_test")
        total_rows = cursor.fetchone()[0]
        assert total_rows == num_tasks * writes_per_task
        
        # Verify no data corruption (all iterations present)
        for t_id in range(num_tasks):
            cursor.execute("SELECT count(*) FROM stress_test WHERE task_id=?", (t_id,))
            assert cursor.fetchone()[0] == writes_per_task
