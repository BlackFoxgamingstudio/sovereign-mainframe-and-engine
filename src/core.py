"""
Unified Mainframe & Protocol State Engine Orchestrator
Author: Russell Alan Powers
Domain: Agentic Protocols & Distributed State
"""
from typing import Dict, Any
from .fsm_engine import ProtocolFSM
from .event_journal import EventJournal
from .p2p_message_bus import P2PMessageBus
from .task_router import TaskDecompositionRouter
from .rpg_loop import RPGGameLoop

class CoreEngine:
    def __init__(self):
        self.fsm = ProtocolFSM()
        self.journal = EventJournal()
        self.bus = P2PMessageBus()
        self.router = TaskDecompositionRouter()
        self.rpg = RPGGameLoop()

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY",
            "service": "sovereign-mainframe-and-engine",
            "port": 8765,
            "fsm_state": self.fsm.get_state(),
            "journal_length": len(self.journal._journal),
            "rpg_tick": self.rpg.tick_count,
            "version": "1.0.0"
        }
