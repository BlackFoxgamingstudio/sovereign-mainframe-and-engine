"""
P2P Inter-Agent Messaging Bus (FEAT-008-03)
Domain: Agentic Protocols & Distributed State
Author: Russell Alan Powers
"""
import time
import hashlib
from typing import Dict, Any, List

class P2PMessageBus:
    def __init__(self):
        self._inbox: Dict[str, List[Dict[str, Any]]] = {}

    def dispatch(self, sender: str, recipient: str, topic: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        token_raw = f"{sender}:{recipient}:{topic}:{now}"
        msg_id = "MSG-" + hashlib.sha256(token_raw.encode("utf-8")).hexdigest()[:16]

        envelope = {
            "message_id": msg_id,
            "sender": sender,
            "recipient": recipient,
            "topic": topic,
            "timestamp": now,
            "payload": payload,
            "ack_token": "ACK-" + hashlib.sha256(f"ACK:{msg_id}".encode("utf-8")).hexdigest()[:12]
        }

        if recipient not in self._inbox:
            self._inbox[recipient] = []
        self._inbox[recipient].append(envelope)

        return {
            "success": True,
            "message_id": msg_id,
            "recipient": recipient,
            "delivered": True,
            "ack_token": envelope["ack_token"],
            "timestamp": now
        }

    def poll_inbox(self, agent_id: str, purge: bool = False) -> Dict[str, Any]:
        messages = self._inbox.get(agent_id, [])
        if purge:
            self._inbox[agent_id] = []
        return {
            "agent_id": agent_id,
            "message_count": len(messages),
            "messages": messages
        }
