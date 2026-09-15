"""
Unified Mainframe & Protocol State Engine Orchestrator
Author: Russell Alan Powers
Domain: Agentic Protocols & Distributed State
"""
import time
import os
from pathlib import Path
from typing import Dict, Any, Optional

from .fsm_engine import ProtocolFSM
from .event_journal import EventJournal
from .p2p_message_bus import P2PMessageBus
from .task_router import TaskDecompositionRouter
from .rpg_loop import RPGGameLoop

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mainframe.db"

class CoreEngine:
    """Unified Orchestrator tying together FSM, Event Journal, P2P Message Bus, Task Router, and RPG Simulation."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.started_at = time.time()
        self.version = "1.0.0"
        self.service_name = "sovereign-mainframe-and-engine"
        self.port = int(os.environ.get("SBB_MAINFRAME_PORT", 8765))

        # Initialize sub-engines sharing the persistence path
        self.journal = EventJournal(db_path=str(self.db_path))
        self.fsm = ProtocolFSM(db_path=str(self.db_path))
        self.bus = P2PMessageBus(db_path=str(self.db_path))
        self.router = TaskDecompositionRouter()
        self.rpg = RPGGameLoop(db_path=str(self.db_path))

    def execute_action(self, action: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Universal action dispatcher compatible with n8n custom nodes, CLI, and REST endpoints."""
        payload = payload or {}
        action_clean = action.strip().lower()

        # 1. Finite State Machine (FSM)
        if action_clean in ("transition_protocol_state", "fsm_transition", "fsm.transition"):
            target_state = payload.get("target_state") or payload.get("toState") or "TASK_DECOMPOSING"
            trigger = payload.get("trigger_event") or payload.get("event") or "N8N_ACTION"
            context = payload.get("context") or payload.get("payloadJson") or {}
            session_id = payload.get("session_id") or payload.get("sessionId") or "default"
            result = self.fsm.transition(target_state, trigger, context, session_id=session_id)
            if result.get("success"):
                # Automatically seal successful state transition into immutable Event Journal
                self.journal.append_event(
                    event_type="PROTOCOL_STATE_TRANSITION",
                    source=f"MainframeFSM:{session_id}",
                    data={"transition": result["transition"], "target_state": target_state}
                )
            return result

        elif action_clean in ("fsm_get_state", "fsm.get_state", "fsm_status"):
            session_id = payload.get("session_id") or payload.get("sessionId") or "default"
            return self.fsm.get_state(session_id=session_id)

        elif action_clean in ("fsm_list_sessions", "fsm.list_sessions"):
            return {"success": True, "sessions": self.fsm.list_sessions()}

        # 2. Cryptographic Event Journal
        elif action_clean in ("journal_agent_events", "journal_append", "journal.append"):
            event_type = payload.get("event_type") or payload.get("journalTopic") or "SYSTEM_EVENT"
            source = payload.get("source") or payload.get("fromNode") or "n8n_agent"
            data = payload.get("data") or payload.get("journalPayload") or payload
            return self.journal.append_event(event_type, source, data)

        elif action_clean in ("journal_replay", "journal.replay"):
            from_idx = int(payload.get("from_index", 0))
            to_idx = payload.get("to_index")
            to_idx = int(to_idx) if to_idx is not None else None
            return self.journal.replay(from_idx, to_idx)

        elif action_clean in ("journal_verify", "journal_audit", "journal.audit"):
            return self.journal.audit_trail()

        # 3. P2P Inter-Agent Message Bus
        elif action_clean in ("dispatch_agent_message", "p2p_dispatch", "p2p.send"):
            sender = payload.get("sender") or payload.get("fromNode") or "system_operator"
            recipient = payload.get("recipient") or payload.get("toNode") or "SentinelSRE"
            topic = payload.get("topic") or payload.get("p2pTopic") or "general.dispatch"
            msg_payload = payload.get("payload") or payload.get("p2pPayload") or {}
            return self.bus.dispatch(sender, recipient, topic, msg_payload)

        elif action_clean in ("p2p_poll", "p2p.poll", "p2p_inbox"):
            agent_id = payload.get("agent_id") or payload.get("toNode") or "SentinelSRE"
            purge = bool(payload.get("purge", False))
            return self.bus.poll_inbox(agent_id, purge=purge)

        elif action_clean in ("p2p_acknowledge", "p2p.ack"):
            msg_id = payload.get("message_id", "")
            ack_token = payload.get("ack_token", "")
            return self.bus.acknowledge(msg_id, ack_token)

        # 4. Autonomous Task Decomposition Router
        elif action_clean in ("route_subagent_task", "task_decompose", "task.decompose"):
            objective = payload.get("objective") or payload.get("taskObjective") or "Resolve system thermal degradation"
            complexity = payload.get("complexity") or payload.get("taskPriority") or "HIGH"
            max_tasks = int(payload.get("max_subtasks", 4))
            return self.router.decompose_objective(objective, complexity, max_tasks)

        # 5. RPG Simulation Loop
        elif action_clean in ("evaluate_rpg_game_tick", "rpg_tick", "rpg.tick"):
            delta_ms = int(payload.get("delta_ms") or payload.get("deltaMs") or 1000)
            entities = payload.get("active_entities")
            telemetry = payload.get("environmental_telemetry")
            return self.rpg.evaluate_tick(delta_ms, entities, telemetry)

        elif action_clean in ("rpg_get_state", "rpg.state"):
            return self.rpg.get_world_state()

        # Fallback / Informational
        return {
            "success": False,
            "error": f"Unknown action '{action}'.",
            "supported_actions": [
                "transition_protocol_state", "fsm_get_state", "fsm_list_sessions",
                "journal_agent_events", "journal_replay", "journal_verify",
                "dispatch_agent_message", "p2p_poll", "p2p_acknowledge",
                "route_subagent_task",
                "evaluate_rpg_game_tick", "rpg_get_state"
            ]
        }

    def health_check(self) -> Dict[str, Any]:
        """Comprehensive microservice health reporting across all 5 capabilities."""
        db_size_bytes = 0
        if self.db_path.exists():
            db_size_bytes = self.db_path.stat().st_size

        mailbox_stats = self.bus.get_mailbox_stats()

        return {
            "status": "HEALTHY",
            "service": self.service_name,
            "port": self.port,
            "uptime_seconds": round(time.time() - self.started_at, 2),
            "version": self.version,
            "persistence": {
                "db_path": str(self.db_path),
                "db_size_bytes": db_size_bytes
            },
            "fsm_state": self.fsm.get_state(),
            "journal_length": len(self.journal._journal),
            "journal_audit": self.journal.audit_trail(),
            "mailbox_stats": mailbox_stats,
            "rpg_simulation": {
                "tick_count": self.rpg.tick_count,
                "protocol_level": self.rpg.world_state.get("protocol_level"),
                "threat_level": self.rpg.world_state.get("threat_level")
            }
        }
