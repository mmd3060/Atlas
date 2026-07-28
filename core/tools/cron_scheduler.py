"""
Cron Job System — Scheduled tasks for Atlas OS.

Features:
  - Register recurring tasks
  - Execute tasks at intervals
  - Background timer (no external deps)
  - Task history & status

Usage:
    scheduler = CronScheduler()
    scheduler.register("backup", "every 1h", backup_function)
    scheduler.start()  # runs in background thread
"""

import threading
import time
import json
from typing import Any, Dict, List, Optional
from datetime import datetime


class CronJob:
    """A single scheduled job."""
    def __init__(self, name: str, interval_sec: int, func, repeat: bool = True):
        self.name = name
        self.interval_sec = interval_sec
        self.func = func
        self.repeat = repeat
        self.last_run = 0
        self.run_count = 0
        self.last_result = None
        self.enabled = True

    def should_run(self) -> bool:
        if not self.enabled:
            return False
        return (time.time() - self.last_run) >= self.interval_sec

    def execute(self) -> Any:
        try:
            result = self.func()
            self.last_result = {"status": "success", "result": str(result)[:200]}
        except Exception as e:
            self.last_result = {"status": "error", "error": str(e)}
        self.last_run = time.time()
        self.run_count += 1
        return self.last_result


class CronScheduler:
    """
    Background scheduler for Atlas OS.
    Runs in a separate thread, checking jobs every second.
    """

    CHECK_INTERVAL = 1  # seconds between checks

    def __init__(self):
        self._jobs: Dict[str, CronJob] = {}
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()

    def register(self, name: str, interval_sec: int, func, repeat: bool = True):
        """Register a new scheduled job."""
        with self._lock:
            self._jobs[name] = CronJob(name, interval_sec, func, repeat)

    def unregister(self, name: str):
        """Remove a job."""
        with self._lock:
            self._jobs.pop(name, None)

    def enable(self, name: str):
        """Enable a job."""
        if name in self._jobs:
            self._jobs[name].enabled = True

    def disable(self, name: str):
        """Disable a job."""
        if name in self._jobs:
            self._jobs[name].enabled = False

    def list_jobs(self) -> List[Dict]:
        """List all jobs and their status."""
        jobs = []
        for name, job in self._jobs.items():
            jobs.append({
                "name": name,
                "interval_sec": job.interval_sec,
                "enabled": job.enabled,
                "run_count": job.run_count,
                "last_result": job.last_result,
                "last_run": datetime.fromtimestamp(job.last_run).isoformat() if job.last_run else None,
            })
        return jobs

    def start(self):
        """Start the scheduler in background."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the scheduler."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)

    def _run_loop(self):
        """Main scheduler loop."""
        while self._running:
            with self._lock:
                jobs = list(self._jobs.values())

            for job in jobs:
                if job.should_run():
                    job.execute()

            time.sleep(self.CHECK_INTERVAL)
