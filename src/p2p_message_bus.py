"""
P2P Inter-Agent Messaging Bus (FEAT-008-03)
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

class P2PMessageBus:
    """Production-grade persistent P2P agent message bus with delivery tracking and acknowledgments."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS p2p_mailbox (
                    message_id TEXT PRIMARY KEY,
                    sender TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    ack_token TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'UNREAD'
                )
            """)
            conn.commit()

    def dispatch(self, sender: str, recipient: str, topic: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        token_raw = f"{sender}:{recipient}:{topic}:{now}:{json.dumps(payload, sort_keys=True)}"
        msg_id = "MSG-" + hashlib.sha256(token_raw.encode("utf-8")).hexdigest()[:16]
        ack_token = "ACK-" + hashlib.sha256(f"ACK:{msg_id}:{now}".encode("utf-8")).hexdigest()[:12]

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO p2p_mailbox (message_id, sender, recipient, topic, timestamp, payload_json, ack_token, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'UNREAD')
            """, (msg_id, sender, recipient, topic, now, json.dumps(payload, sort_keys=True), ack_token))
            conn.commit()

        return {
            "success": True,
            "message_id": msg_id,
            "sender": sender,
            "recipient": recipient,
            "topic": topic,
            "delivered": True,
            "ack_token": ack_token,
            "status": "UNREAD",
            "timestamp": now
        }

    def poll_inbox(self, agent_id: str, purge: bool = False, mark_read: bool = True) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cur = conn.execute("""
                SELECT * FROM p2p_mailbox
                WHERE recipient = ?
                ORDER BY timestamp ASC
            """, (agent_id,))
            rows = cur.fetchall()

            messages = []
            for r in rows:
                messages.append({
                    "message_id": r["message_id"],
                    "sender": r["sender"],
                    "recipient": r["recipient"],
                    "topic": r["topic"],
                    "timestamp": r["timestamp"],
                    "payload": json.loads(r["payload_json"]),
                    "ack_token": r["ack_token"],
                    "status": r["status"]
                })

            if purge:
                conn.execute("DELETE FROM p2p_mailbox WHERE recipient = ?", (agent_id,))
                conn.commit()
            elif mark_read and rows:
                conn.execute("UPDATE p2p_mailbox SET status = 'DELIVERED' WHERE recipient = ? AND status = 'UNREAD'", (agent_id,))
                conn.commit()

        return {
            "agent_id": agent_id,
            "message_count": len(messages),
            "messages": messages
        }

    def acknowledge(self, message_id: str, ack_token: str) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM p2p_mailbox WHERE message_id = ? AND ack_token = ?", (message_id, ack_token))
            row = cur.fetchone()
            if not row:
                return {
                    "success": False,
                    "error": "Message or ack_token mismatch",
                    "message_id": message_id
                }

            conn.execute("UPDATE p2p_mailbox SET status = 'ACKNOWLEDGED' WHERE message_id = ?", (message_id,))
            conn.commit()

        return {
            "success": True,
            "message_id": message_id,
            "status": "ACKNOWLEDGED"
        }

    def get_mailbox_stats(self) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT COUNT(*) as total, SUM(CASE WHEN status = 'UNREAD' THEN 1 ELSE 0 END) as unread FROM p2p_mailbox")
            r = cur.fetchone()
            return {
                "total_messages": r["total"] or 0,
                "unread_messages": r["unread"] or 0
            }
