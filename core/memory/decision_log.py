"""
Memory Decision Log v1 — Records WHY memory decisions were made.

This enables Reflection Engine to review past decisions and learn.

Usage:
    logger = DecisionLogger(backend=sqlite_backend)
    logger.log(memory_key="cpu", action="archive", reason="conflict with newer")
    history = logger.get_history(memory_key="cpu")
"""

import sqlite3
import time
from typing import Any, Dict, List, Optional


class DecisionLogger:
    """
    Records memory decisions for future reflection.

    Each log entry:
      - memory_key: which memory was affected
      - action: what was done (keep/promote/archive/delete)
      - reason: why it was done
      - confidence: how confident the decision was
      - timestamp: when the decision was made
    """

    def __init__(self, backend=None, db_path=None):
        """
        Args:
            backend: SQLiteBackend instance (for DB access)
            db_path: Direct DB path (if no backend)
        """
        if backend:
            self._conn = backend._conn
            self._create_table()
        elif db_path:
            self._conn = sqlite3.connect(db_path)
            self._conn.row_factory = sqlite3.Row
            self._create_table()
        else:
            raise ValueError("Either backend or db_path required")

    def _create_table(self):
        """Create decision_logs table."""
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS decision_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_key TEXT NOT NULL,
                action TEXT NOT NULL,
                reason TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                metadata TEXT DEFAULT '{}',
                timestamp REAL NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_logs_key ON decision_logs(memory_key);
            CREATE INDEX IF NOT EXISTS idx_logs_action ON decision_logs(action);
            CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON decision_logs(timestamp DESC);
        """)
        self._conn.commit()

    # ═══════════════════════════════════════════════
    #  LOGGING
    # ═══════════════════════════════════════════════

    def log(
        self,
        memory_key: str,
        action: str,
        reason: str,
        confidence: float = 0.5,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Log a memory decision.

        Args:
            memory_key: The memory that was affected
            action:     What was done (keep/promote/archive/delete/conflict)
            reason:     Why it was done
            confidence: How confident (0-1)
            metadata:   Optional extra data

        Returns:
            {status, timestamp, id}
        """
        import json
        now = time.time()
        cursor = self._conn.execute(
            """INSERT INTO decision_logs
               (memory_key, action, reason, confidence, metadata, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (memory_key, action, reason, confidence,
             json.dumps(metadata or {}), now)
        )
        self._conn.commit()

        return {
            "status": "logged",
            "timestamp": now,
            "id": cursor.lastrowid,
        }

    # ═══════════════════════════════════════════════
    #  QUERY
    # ═══════════════════════════════════════════════

    def get_history(
        self,
        memory_key: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get decision history for a specific memory."""
        rows = self._conn.execute(
            """SELECT * FROM decision_logs
               WHERE memory_key = ?
               ORDER BY timestamp DESC
               LIMIT ?""",
            (memory_key, limit)
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all recent decisions."""
        rows = self._conn.execute(
            """SELECT * FROM decision_logs
               ORDER BY timestamp DESC
               LIMIT ?""",
            (limit,)
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_by_action(
        self,
        action: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get all decisions with a specific action."""
        rows = self._conn.execute(
            """SELECT * FROM decision_logs
               WHERE action = ?
               ORDER BY timestamp DESC
               LIMIT ?""",
            (action, limit)
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_recent_decisions(
        self,
        hours: int = 24,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get decisions from the last N hours (for Reflection)."""
        cutoff = time.time() - (hours * 3600)
        rows = self._conn.execute(
            """SELECT * FROM decision_logs
               WHERE timestamp > ?
               ORDER BY timestamp DESC
               LIMIT ?""",
            (cutoff, limit)
        ).fetchall()
        return [self._row_to_dict(r) for r in rows]

    # ═══════════════════════════════════════════════
    #  STATS
    # ═══════════════════════════════════════════════

    def get_stats(self) -> Dict[str, Any]:
        """Get decision statistics."""
        total = self._conn.execute(
            "SELECT COUNT(*) FROM decision_logs"
        ).fetchone()[0]

        rows = self._conn.execute(
            """SELECT action, COUNT(*) as count
               FROM decision_logs
               GROUP BY action"""
        ).fetchall()

        by_action = {row["action"]: row["count"] for row in rows}

        return {
            "total": total,
            "by_action": by_action,
        }

    # ═══════════════════════════════════════════════
    #  LIFECYCLE
    # ═══════════════════════════════════════════════

    def close(self):
        """Close connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    # ═══════════════════════════════════════════════
    #  HELPERS
    # ═══════════════════════════════════════════════

    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert a Row to dict."""
        import json
        return {
            "id": row["id"],
            "memory_key": row["memory_key"],
            "action": row["action"],
            "reason": row["reason"],
            "confidence": row["confidence"],
            "metadata": json.loads(row["metadata"]),
            "timestamp": row["timestamp"],
        }
