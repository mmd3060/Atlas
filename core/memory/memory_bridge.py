"""
Advanced Memory Persistence — Bridge between AdvancedMemory and SQLite.
"""

import json
import sqlite3
from typing import Any, Dict, List, Optional
from core.memory.advanced_memory import AdvancedMemory


class MemoryBridge:
    """
    Bridges the 3-layer AdvancedMemory to persistent SQLite storage.
    """

    def __init__(self, db_path: str = "atlas_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the extended memory tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Episodic Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodic_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event_type TEXT,
                content TEXT,
                context TEXT,
                importance REAL,
                outcome TEXT
            )
        ''')
        
        # Semantic Table (Knowledge Graph)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS semantic_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                predicate TEXT,
                object TEXT,
                confidence REAL
            )
        ''')
        
        # Procedural Table (How-to)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS procedural_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                steps TEXT,
                success_rate REAL
            )
        ''')
        
        conn.commit()
        conn.close()

    def save_episode(self, episode_data: Dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO episodic_memory (timestamp, event_type, content, context, importance, outcome)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            episode_data['timestamp'],
            episode_data['event_type'],
            episode_data['content'],
            json.dumps(episode_data.get('context', {})),
            episode_data.get('importance', 0.5),
            episode_data.get('outcome', "")
        ))
        conn.commit()
        conn.close()

    def save_fact(self, subject: str, predicate: str, obj: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO semantic_memory (subject, predicate, object, confidence)
            VALUES (?, ?, ?, ?)
        ''', (subject.lower(), predicate.lower(), obj.lower(), 1.0))
        conn.commit()
        conn.close()

    def save_procedure(self, name: str, steps: List[str]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO procedural_memory (name, steps, success_rate)
            VALUES (?, ?, ?)
        ''', (name.lower(), json.dumps(steps), 1.0))
        conn.commit()
        conn.close()

    def load_all(self, memory_obj: AdvancedMemory):
        """Load all data from SQLite into the AdvancedMemory object."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load Episodes
        cursor.execute('SELECT * FROM episodic_memory ORDER BY timestamp DESC LIMIT 100')
        for row in cursor.fetchall():
            memory_obj.episodic.record_event(
                event_type=row[2],
                content=row[3],
                context=json.loads(row[4]),
                importance=row[5],
                outcome=row[6]
            )
            
        # Load Semantic
        cursor.execute('SELECT subject, predicate, object FROM semantic_memory')
        for row in cursor.fetchall():
            memory_obj.semantic.add_fact(row[0], row[1], row[2])
            
        # Load Procedural
        cursor.execute('SELECT name, steps FROM procedural_memory')
        for row in cursor.fetchall():
            memory_obj.procedural.record_procedure(row[0], json.loads(row[1]))
            
        conn.close()
