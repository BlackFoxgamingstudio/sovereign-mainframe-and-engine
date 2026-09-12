"""
Finite State Machine Protocol Engine (FEAT-008-01)
Domain: Agentic Protocols & Distributed State
Author: Russell Alan Powers
"""
import time
import hashlib
from typing import Dict, Any, List, Optional

class ProtocolFSM:
    VALID_STATES = {
        "UNINITIALIZED", "IDLE", "TASK_DECOMPOSING", "AGENT_DISPATCHING",
        "AWAITING_CONSENSUS", "EXECUTING_REMEDIATION", "JOURNAL_COMMITTED", "ERROR_ESCALATION"
    }

    ALLOWED_TRANSITIONS = {
        "UNINITIALIZED": ["IDLE", "ERROR_ESCALATION"],
        "IDLE": ["TASK_DECOMPOSING", "ERROR_ESCALATION"],
        "TASK_DECOMPOSING": ["AGENT_DISPATCHING", "IDLE", "ERROR_ESCALATION"],
        "AGENT_DISPATCHING": ["AWAITING_CONSENSUS", "ERROR_ESCALATION"],
        "AWAITING_CONSENSUS": ["EXECUTING_REMEDIATION", "JOURNAL_COMMITTED", "ERROR_ESCALATION"],
        "EXECUTING_REMEDIATION": ["JOURNAL_COMMITTED", "ERROR_ESCALATION"],
        "JOURNAL_COMMITTED": ["IDLE"],
        "ERROR_ESCALATION": ["IDLE", "UNINITIALIZED"]
    }

    def __init__(self, initial_state: str = "IDLE"):
        self.state = initial_state if initial_state in self.VALID_STATES else "IDLE"
        self.history: List[Dict[str, Any]] = []

    def transition(self, target_state: str, trigger_event: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = context or {}
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        if target_state not in self.VALID_STATES:
            return {
                "success": False,
                "error": f"Invalid state '{target_state}'. Valid: {sorted(list(self.VALID_STATES))}",
                "current_state": self.state
            }

        allowed = self.ALLOWED_TRANSITIONS.get(self.state, [])
        if target_state not in allowed:
            return {
                "success": False,
                "error": f"Illegal transition from '{self.state}' to '{target_state}'. Allowed: {allowed}",
                "current_state": self.state
            }

        prev_state = self.state
        self.state = target_state
        token_raw = f"{prev_state}->{target_state}:{trigger_event}:{now}"
        token = hashlib.sha256(token_raw.encode("utf-8")).hexdigest()[:16]

        record = {
            "transition_id": f"TR-{token}",
            "previous_state": prev_state,
            "new_state": target_state,
            "trigger_event": trigger_event,
            "timestamp": now,
            "context": context
        }
        self.history.append(record)

        return {
            "success": True,
            "transition": record,
            "current_state": self.state
        }

    def get_state(self) -> Dict[str, Any]:
        return {
            "current_state": self.state,
            "history_count": len(self.history),
            "allowed_next_states": self.ALLOWED_TRANSITIONS.get(self.state, [])
        }
