"""
Finite State Machine Protocol Engine (FEAT-008-01)
Domain: Agentic Protocols & Distributed State
Author: Russell Alan Powers
"""
import time
import json
import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mainframe.db"

class ProtocolFSM:
    """Multi-session deterministic protocol finite state machine with SQLite persistence."""

    VALID_STATES: Set[str] = {
        "UNINITIALIZED", "IDLE", "TASK_DECOMPOSING", "AGENT_DISPATCHING",
        "AWAITING_CONSENSUS", "EXECUTING_REMEDIATION", "JOURNAL_COMMITTED", "ERROR_ESCALATION"
    }

    ALLOWED_TRANSITIONS: Dict[str, List[str]] = {
        "UNINITIALIZED": ["IDLE", "ERROR_ESCALATION"],
        "IDLE": ["TASK_DECOMPOSING", "ERROR_ESCALATION"],
        "TASK_DECOMPOSING": ["AGENT_DISPATCHING", "IDLE", "ERROR_ESCALATION"],
        "AGENT_DISPATCHING": ["AWAITING_CONSENSUS", "ERROR_ESCALATION"],
        "AWAITING_CONSENSUS": ["EXECUTING_REMEDIATION", "JOURNAL_COMMITTED", "ERROR_ESCALATION"],
        "EXECUTING_REMEDIATION": ["JOURNAL_COMMITTED", "ERROR_ESCALATION"],
        "JOURNAL_COMMITTED": ["IDLE"],
        "ERROR_ESCALATION": ["IDLE", "UNINITIALIZED"]
    }

    def __init__(self, default_state: str = "IDLE", db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.default_state = default_state if default_state in self.VALID_STATES else "IDLE"
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS protocol_fsm_sessions (
                    session_id TEXT PRIMARY KEY,
                    current_state TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS protocol_transitions (
                    transition_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    previous_state TEXT NOT NULL,
                    new_state TEXT NOT NULL,
                    trigger_event TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    context_json TEXT NOT NULL
                )
            """)
            conn.commit()

    def _ensure_session(self, session_id: str) -> str:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT current_state FROM protocol_fsm_sessions WHERE session_id = ?", (session_id,))
            row = cur.fetchone()
            if row:
                return row["current_state"]
            now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            conn.execute(
                "INSERT INTO protocol_fsm_sessions (session_id, current_state, updated_at) VALUES (?, ?, ?)",
                (session_id, self.default_state, now)
            )
            conn.commit()
            return self.default_state

    def transition(
        self,
        target_state: str,
        trigger_event: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: str = "default"
    ) -> Dict[str, Any]:
        context = context or {}
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        current_state = self._ensure_session(session_id)

        if target_state not in self.VALID_STATES:
            return {
                "success": False,
                "session_id": session_id,
                "error": f"Invalid state '{target_state}'. Valid states: {sorted(list(self.VALID_STATES))}",
                "current_state": current_state
            }

        allowed = self.ALLOWED_TRANSITIONS.get(current_state, [])
        if target_state not in allowed:
            return {
                "success": False,
                "session_id": session_id,
                "error": f"Illegal transition from '{current_state}' to '{target_state}'. Allowed transitions: {allowed}",
                "current_state": current_state
            }

        token_raw = f"{session_id}:{current_state}->{target_state}:{trigger_event}:{now}"
        token = hashlib.sha256(token_raw.encode("utf-8")).hexdigest()[:16]
        transition_id = f"TR-{token}"

        record = {
            "transition_id": transition_id,
            "session_id": session_id,
            "previous_state": current_state,
            "new_state": target_state,
            "trigger_event": trigger_event,
            "timestamp": now,
            "context": context
        }

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO protocol_transitions (transition_id, session_id, previous_state, new_state, trigger_event, timestamp, context_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (transition_id, session_id, current_state, target_state, trigger_event, now, json.dumps(context, sort_keys=True)))

            conn.execute("""
                UPDATE protocol_fsm_sessions
                SET current_state = ?, updated_at = ?
                WHERE session_id = ?
            """, (target_state, now, session_id))
            conn.commit()

        return {
            "success": True,
            "session_id": session_id,
            "transition": record,
            "current_state": target_state,
            "allowed_next_states": self.ALLOWED_TRANSITIONS.get(target_state, [])
        }

    def get_state(self, session_id: str = "default") -> Dict[str, Any]:
        state = self._ensure_session(session_id)
        with self._get_connection() as conn:
            cur = conn.execute(
                "SELECT COUNT(*) AS cnt FROM protocol_transitions WHERE session_id = ?",
                (session_id,)
            )
            history_count = cur.fetchone()["cnt"]

        return {
            "session_id": session_id,
            "current_state": state,
            "history_count": history_count,
            "allowed_next_states": self.ALLOWED_TRANSITIONS.get(state, [])
        }

    def get_history(self, session_id: str = "default", limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.execute(
                "SELECT * FROM protocol_transitions WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                (session_id, limit)
            )
            rows = cur.fetchall()
            return [
                {
                    "transition_id": r["transition_id"],
                    "session_id": r["session_id"],
                    "previous_state": r["previous_state"],
                    "new_state": r["new_state"],
                    "trigger_event": r["trigger_event"],
                    "timestamp": r["timestamp"],
                    "context": json.loads(r["context_json"])
                }
                for r in rows
            ]

    def list_sessions(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT session_id, current_state, updated_at FROM protocol_fsm_sessions ORDER BY updated_at DESC")
            return [dict(r) for r in cur.fetchall()]

    @property
    def state(self) -> str:
        """Backward compatibility for existing test assertions checking fsm.state."""
        return self._ensure_session("default")

    @state.setter
    def state(self, value: str):
        if value in self.VALID_STATES:
            now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO protocol_fsm_sessions (session_id, current_state, updated_at)
                    VALUES ('default', ?, ?)
                    ON CONFLICT(session_id) DO UPDATE SET current_state = ?, updated_at = ?
                """, (value, now, value, now))
                conn.commit()
