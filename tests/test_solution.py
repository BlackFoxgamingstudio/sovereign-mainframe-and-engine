import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
"""
Automated Test Suite for sovereign-mainframe-and-engine
Tests 100% of all 5 exported micro-tools.
"""
import pytest
from src.fsm_engine import ProtocolFSM
from src.event_journal import EventJournal
from src.p2p_message_bus import P2PMessageBus
from src.task_router import TaskDecompositionRouter
from src.rpg_loop import RPGGameLoop
from src.core import CoreEngine

def test_fsm_valid_transition():
    fsm = ProtocolFSM("IDLE")
    res = fsm.transition("TASK_DECOMPOSING", "INCIDENT_ALERT")
    assert res["success"] is True
    assert res["current_state"] == "TASK_DECOMPOSING"
    assert "TR-" in res["transition"]["transition_id"]

def test_fsm_invalid_transition():
    fsm = ProtocolFSM("IDLE")
    res = fsm.transition("JOURNAL_COMMITTED", "ILLEGAL_JUMP")
    assert res["success"] is False
    assert fsm.state == "IDLE"

def test_journal_append_and_integrity():
    journal = EventJournal()
    r1 = journal.append_event("TEST_A", "pytest", {"key": "val1"})
    r2 = journal.append_event("TEST_B", "pytest", {"key": "val2"})
    assert r1["success"] is True
    assert r2["index"] == 1
    assert journal.verify_integrity() is True

def test_journal_replay():
    journal = EventJournal()
    journal.append_event("BOOT", "kernel", {"boot": True})
    journal.append_event("READY", "kernel", {"ready": True})
    replay = journal.replay()
    assert replay["success"] is True
    assert replay["replayed_count"] == 2

def test_p2p_message_dispatch():
    bus = P2PMessageBus()
    res = bus.dispatch("AgentA", "AgentB", "test.topic", {"msg": "hello"})
    assert res["success"] is True
    assert res["delivered"] is True
    inbox = bus.poll_inbox("AgentB")
    assert inbox["message_count"] == 1
    assert inbox["messages"][0]["payload"]["msg"] == "hello"

def test_task_decomposition_router():
    router = TaskDecompositionRouter()
    res = router.decompose_objective("Mitigate thermal hardware crash dump", "HIGH")
    assert res["success"] is True
    assert res["subtasks_count"] > 0
    assert "SentinelSRE" in res["assigned_personas"]

def test_rpg_game_tick():
    rpg = RPGGameLoop()
    res = rpg.evaluate_tick(delta_ms=500)
    assert res["success"] is True
    assert res["tick"] == 1
    assert "TICK-" in res["tick_token"]

def test_core_engine_health():
    engine = CoreEngine()
    health = engine.health_check()
    assert health["status"] == "HEALTHY"
    assert health["port"] == 8765
