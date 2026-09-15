"""
Deterministic Event Replay & Journaling Engine (FEAT-008-02)
Domain: Agentic Protocols & Distributed State
Author: Russell Alan Powers
"""
import time
import json
import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mainframe.db"

class EventJournal:
    """Production-grade cryptographic append-only event ledger with SQLite durability."""

    GENESIS_HASH = "GENESIS_HASH_0000000000000000"

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._journal: List[Dict[str, Any]] = []
        self._last_hash = self.GENESIS_HASH
        self._init_db()
        self._load_from_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS event_journal (
                    idx INTEGER PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    source TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    entry_hash TEXT NOT NULL
                )
            """)
            conn.commit()

    def _load_from_db(self) -> None:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM event_journal ORDER BY idx ASC")
            rows = cur.fetchall()
            self._journal = []
            for r in rows:
                self._journal.append({
                    "index": r["idx"],
                    "event_type": r["event_type"],
                    "source": r["source"],
                    "timestamp": r["timestamp"],
                    "data": json.loads(r["data_json"]),
                    "previous_hash": r["previous_hash"],
                    "entry_hash": r["entry_hash"]
                })
            if self._journal:
                self._last_hash = self._journal[-1]["entry_hash"]
            else:
                self._last_hash = self.GENESIS_HASH

    def append_event(self, event_type: str, source: str, data: Dict[str, Any]) -> Dict[str, Any]:
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        index = len(self._journal)
        data_str = json.dumps(data, sort_keys=True)
        raw = f"{index}:{event_type}:{source}:{data_str}:{self._last_hash}:{now}"
        entry_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

        entry = {
            "index": index,
            "event_type": event_type,
            "source": source,
            "timestamp": now,
            "data": data,
            "previous_hash": self._last_hash,
            "entry_hash": entry_hash
        }

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO event_journal (idx, event_type, source, timestamp, data_json, previous_hash, entry_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (index, event_type, source, now, data_str, self._last_hash, entry_hash))
            conn.commit()

        self._journal.append(entry)
        self._last_hash = entry_hash

        return {
            "success": True,
            "index": index,
            "entry_hash": entry_hash,
            "previous_hash": entry["previous_hash"],
            "journal_length": len(self._journal),
            "timestamp": now
        }

    def replay(self, from_index: int = 0, to_index: Optional[int] = None) -> Dict[str, Any]:
        end = to_index if to_index is not None else len(self._journal)
        sliced = self._journal[from_index:end]
        return {
            "success": True,
            "replayed_count": len(sliced),
            "from_index": from_index,
            "to_index": end,
            "events": sliced,
            "integrity_verified": self.verify_integrity()
        }

    def verify_integrity(self) -> bool:
        prev = self.GENESIS_HASH
        for e in self._journal:
            data_str = json.dumps(e["data"], sort_keys=True)
            raw = f"{e['index']}:{e['event_type']}:{e['source']}:{data_str}:{prev}:{e['timestamp']}"
            expected = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            if e["entry_hash"] != expected or e["previous_hash"] != prev:
                return False
            prev = e["entry_hash"]
        return True

    def audit_trail(self) -> Dict[str, Any]:
        is_valid = self.verify_integrity()
        return {
            "total_events": len(self._journal),
            "head_hash": self._last_hash,
            "genesis_hash": self.GENESIS_HASH,
            "integrity_valid": is_valid,
            "status": "SECURE" if is_valid else "TAMPER_DETECTED"
        }
