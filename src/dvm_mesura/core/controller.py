from __future__ import annotations
import asyncio
import signal
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from .base import Backend, Monitor
from .helpers import parse_interval

class PollingController:
    """Manages the polling loop for a single monitor."""
    
    def __init__(self, monitor: Monitor, backends: List[Backend], interval_str: str):
        self.monitor = monitor
        self.backends = backends
        self.interval_seconds = parse_interval(interval_str)
        self.name = monitor.name

    async def run(self):
        """Infinite polling loop."""
        print(f"Starting controller for {self.name} (interval: {self.interval_seconds}s)")
        while True:
            try:
                start_time = asyncio.get_event_loop().time()
                
                # Fetch and process data
                raw_data = await self.monitor.fetch_data()
                processed_data = self.monitor.process_data(raw_data)
                
                # Add common metadata if not present
                if "timestamp" not in processed_data:
                    processed_data["timestamp"] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                
                # Write to all backends
                for backend in self.backends:
                    await backend.write(processed_data, self.name)
                
                # Calculate sleep time to maintain interval
                elapsed = asyncio.get_event_loop().time() - start_time
                sleep_time = max(0, self.interval_seconds - elapsed)
                await asyncio.sleep(sleep_time)
                
            except asyncio.CancelledError:
                print(f"Controller for {self.name} stopped.")
                break
            except Exception as e:
                print(f"Error in controller for {self.name}: {e}")
                await asyncio.sleep(min(60, self.interval_seconds)) # Wait before retry

class MasterController:
    """Manages multiple PollingControllers and runs them concurrently."""
    
    def __init__(self):
        self.controllers: List[PollingController] = []
        self.tasks: List[asyncio.Task] = []

    def add_controller(self, controller: PollingController):
        self.controllers.append(controller)

    async def run_all(self):
        """Run all controllers concurrently."""
        if not self.controllers:
            print("No controllers added.")
            return

        self.tasks = [asyncio.create_task(c.run()) for c in self.controllers]
        
        loop = asyncio.get_running_loop()
        stop_event = asyncio.Event()

        def handle_stop():
            print("\nShutdown requested...")
            stop_event.set()

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, handle_stop)
            except NotImplementedError:
                # Signal handlers not supported on some platforms (e.g. Windows)
                pass

        await stop_event.wait()
        
        print("Stopping all monitors...")
        for task in self.tasks:
            task.cancel()
        
        await asyncio.gather(*self.tasks, return_exceptions=True)
        print("All monitors stopped.")
