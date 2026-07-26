"""
SQLite Backend — persistent storage for Atlas OS Memory System.

Implements MemoryBackend ABC with SQLite.

Features:
  - Persistent storage (survives restart)
  - Full-text search (FTS5)
  - JSON metadata storage
  - TTL support
  - Thread-safe (WAL mode)

Usage:
    backend = SQLiteBackend(db_path="data/atlas_memory.db")
    backend.open()
    backend.put(record)
"""

import json
import sqlite3
import time
from typing import List, Optional

from core.memory.types import MemoryRecord
from core.memory.backend import MemoryBackend


class SQLiteBackend(MemoryBackend):
    """
    SQLite implementation of MemoryBackend.

    Stores MemoryRecord objects in a SQLite database.
    Uses FTS5 for full-text search.
    """

    def __init__(self, db_path: str = "data/atlas_memory.db"):
        """
        Args:
            db_path: Path to SQLite database file
        """
        self._db_path = db_path
        self._conn = None

    # ═══════════════════════════════════════════════
    #  LIFECYCLE
    # ═══════════════════════════════════════════════

    def open(self) -> None:
        """Open database connection and create tables."""
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._create_tables()

    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def health(self) -> bool:
        """Return True if connection is open."""
        return self._conn is not None

    # ═══════════════════════════════════════════════
    #  SCHEMA
    # ═══════════════════════════════════════════════

    def _create_tables(self) -> None:
        """Create memories table and FTS5 index."""
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_type TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                importance REAL DEFAULT 0.5,
                source TEXT DEFAULT 'unknown',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                access_count INTEGER DEFAULT 0,
                tags TEXT DEFAULT '[]',
                ttl REAL,
                metadata TEXT DEFAULT '{}',
                UNIQUE(memory_type, key)
            );

            CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type);
            CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance DESC);
            CREATE INDEX IF NOT EXISTS idx_created_at ON memories(created_at DESC);

            -- FTS5 for full-text search
            CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                key,
                value,
                content='memories',
                content_rowid='id'
            );

            -- Triggers to keep FTS in sync
            CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
                INSERT INTO memories_fts(rowid, key, value)
                VALUES (new.id, new.key, new.value);
            END;

            CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
                INSERT INTO memories_fts(memories_fts, rowid, key, value)
                VALUES ('delete', old.id, old.key, old.value);
            END;

            CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
                INSERT INTO memories_fts(memories_fts, rowid, key, value)
                VALUES ('delete', old.id, old.key, old.value);
                INSERT INTO memories_fts(rowid, key, value)
                VALUES (new.id, new.key, new.value);
            END;
        """)
        self._conn.commit()

    # ═══════════════════════════════════════════════
    #  CRUD
    # ═══════════════════════════════════════════════

    def put(self, record: MemoryRecord) -> None:
        """Insert or overwrite a record."""
        self._conn.execute("""
            INSERT OR REPLACE INTO memories
            (memory_type, key, value, importance, source, created_at, updated_at,
             access_count, tags, ttl, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.memory_type,
            record.key,
            self._serialize_value(record.value),
            record.importance,
            record.source,
            record.created_at,
            record.updated_at,
            record.access_count,
            json.dumps(record.tags),
            record.ttl,
            json.dumps(record.metadata),
        ))
        self._conn.commit()

    def get(self, memory_type: str, key: str) -> Optional[MemoryRecord]:
        """Retrieve a single record."""
        row = self._conn.execute(
            "SELECT * FROM memories WHERE memory_type = ? AND key = ?",
            (memory_type, key)
        ).fetchone()

        if row is None:
            return None

        return self._row_to_record(row)

    def update(self, record: MemoryRecord) -> None:
        """Update an existing record."""
        self._conn.execute("""
            UPDATE memories SET
                value = ?, importance = ?, source = ?,
                updated_at = ?, access_count = ?,
                tags = ?, ttl = ?, metadata = ?
            WHERE memory_type = ? AND key = ?
        """, (
            self._serialize_value(record.value),
            record.importance,
            record.source,
            record.updated_at,
            record.access_count,
            json.dumps(record.tags),
            record.ttl,
            json.dumps(record.metadata),
            record.memory_type,
            record.key,
        ))
        self._conn.commit()

    def delete(self, memory_type: str, key: str) -> bool:
        """Delete a record. Return True if it existed."""
        cursor = self._conn.execute(
            "DELETE FROM memories WHERE memory_type = ? AND key = ?",
            (memory_type, key)
        )
        self._conn.commit()
        return cursor.rowcount > 0

    # ═══════════════════════════════════════════════
    #  QUERY
    # ═══════════════════════════════════════════════

    def list_records(
        self,
        memory_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[MemoryRecord]:
        """List records, optionally filtered by type."""
        if memory_type:
            rows = self._conn.execute(
                "SELECT * FROM memories WHERE memory_type = ? ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (memory_type, limit, offset)
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM memories ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset)
            ).fetchall()

        return [self._row_to_record(row) for row in rows]

    def search(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        min_importance: float = 0.0,
    ) -> List[MemoryRecord]:
        """Full-text search using FTS5."""
        # Build FTS query
        fts_query = self._build_fts_query(query)

        if memory_types:
            placeholders = ",".join("?" * len(memory_types))
            rows = self._conn.execute(f"""
                SELECT m.* FROM memories m
                JOIN memories_fts fts ON m.id = fts.rowid
                WHERE memories_fts MATCH ?
                AND m.memory_type IN ({placeholders})
                AND m.importance >= ?
                ORDER BY m.importance DESC
                LIMIT ?
            """, [fts_query] + memory_types + [min_importance, limit]).fetchall()
        else:
            rows = self._conn.execute("""
                SELECT m.* FROM memories m
                JOIN memories_fts fts ON m.id = fts.rowid
                WHERE memories_fts MATCH ?
                AND m.importance >= ?
                ORDER BY m.importance DESC
                LIMIT ?
            """, (fts_query, min_importance, limit)).fetchall()

        return [self._row_to_record(row) for row in rows]

    def count(self, memory_type: Optional[str] = None) -> int:
        """Count records, optionally per type."""
        if memory_type:
            row = self._conn.execute(
                "SELECT COUNT(*) FROM memories WHERE memory_type = ?",
                (memory_type,)
            ).fetchone()
        else:
            row = self._conn.execute("SELECT COUNT(*) FROM memories").fetchone()
        return row[0]

    # ═══════════════════════════════════════════════
    #  MAINTENANCE
    # ═══════════════════════════════════════════════

    def purge_expired(self) -> int:
        """Remove all expired records."""
        now = time.time()
        cursor = self._conn.execute(
            "DELETE FROM memories WHERE ttl IS NOT NULL AND (created_at + ttl) < ?",
            (now,)
        )
        self._conn.commit()
        return cursor.rowcount

    def clear(self, memory_type: Optional[str] = None) -> int:
        """Clear records, optionally per type."""
        if memory_type:
            cursor = self._conn.execute(
                "DELETE FROM memories WHERE memory_type = ?",
                (memory_type,)
            )
        else:
            cursor = self._conn.execute("DELETE FROM memories")
        self._conn.commit()
        return cursor.rowcount

    # ═══════════════════════════════════════════════
    #  HELPERS
    # ═══════════════════════════════════════════════

    def _row_to_record(self, row) -> MemoryRecord:
        """Convert a database row to MemoryRecord."""
        return MemoryRecord(
            key=row["key"],
            value=self._deserialize_value(row["value"]),
            memory_type=row["memory_type"],
            importance=row["importance"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            source=row["source"],
            access_count=row["access_count"],
            tags=json.loads(row["tags"]),
            ttl=row["ttl"],
            metadata=json.loads(row["metadata"]),
        )

    def _serialize_value(self, value) -> str:
        """Serialize value to JSON string."""
        if isinstance(value, str):
            return value
        return json.dumps(value)

    def _deserialize_value(self, raw: str):
        """Deserialize value from JSON string."""
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return raw

    def _build_fts_query(self, query: str) -> str:
        """Build FTS5 query from user input."""
        # Simple approach: split words and join with AND
        words = query.strip().split()
        if not words:
            return '""'
        # Escape special FTS5 characters
        cleaned = []
        for word in words:
            # Remove FTS5 special chars
            clean = "".join(c for c in word if c.isalnum() or c in "_-")
            if clean:
                cleaned.append(f'"{clean}"')
        return " AND ".join(cleaned) if cleaned else '""'
