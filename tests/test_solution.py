import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.fsm_engine import ProtocolFSM
from src.event_journal import EventJournal
from src.p2p_message_bus import P2PMessageBus
from src.task_router import TaskDecompositionRouter
from src.rpg_loop import RPGGameLoop
from src.core import CoreEngine

class TestMainframeSolution(unittest.TestCase):
    def test_fsm_valid_transition(self):
        fsm = ProtocolFSM("IDLE")
        res = fsm.transition("TASK_DECOMPOSING", "INCIDENT_ALERT")
        self.assertTrue(res["success"])
        self.assertEqual(res["current_state"], "TASK_DECOMPOSING")
        self.assertIn("TR-", res["transition"]["transition_id"])

    def test_fsm_invalid_transition(self):
        fsm = ProtocolFSM("IDLE")
        res = fsm.transition("JOURNAL_COMMITTED", "ILLEGAL_JUMP")
        self.assertFalse(res["success"])
        self.assertEqual(fsm.state, "IDLE")

    def test_journal_append_and_integrity(self):
        journal = EventJournal()
        r1 = journal.append_event("TEST_A", "audit", {"key": "val1"})
        r2 = journal.append_event("TEST_B", "audit", {"key": "val2"})
        self.assertTrue(r1["success"])
        self.assertEqual(r2["index"], 1)
        self.assertTrue(journal.verify_integrity())

    def test_journal_replay(self):
        journal = EventJournal()
        journal.append_event("BOOT", "kernel", {"boot": True})
        journal.append_event("READY", "kernel", {"ready": True})
        replay = journal.replay()
        self.assertTrue(replay["success"])
        self.assertEqual(replay["replayed_count"], 2)

    def test_p2p_message_dispatch(self):
        bus = P2PMessageBus()
        res = bus.dispatch("AgentA", "AgentB", "test.topic", {"msg": "hello"})
        self.assertTrue(res["success"])
        self.assertTrue(res["delivered"])
        inbox = bus.poll_inbox("AgentB")
        self.assertEqual(inbox["message_count"], 1)
        self.assertEqual(inbox["messages"][0]["payload"]["msg"], "hello")

    def test_task_decomposition_router(self):
        router = TaskDecompositionRouter()
        res = router.decompose_objective("Mitigate thermal hardware crash dump", "HIGH")
        self.assertTrue(res["success"])
        self.assertGreater(res["subtasks_count"], 0)
        self.assertIn("SentinelSRE", res["assigned_personas"])

    def test_rpg_game_tick(self):
        rpg = RPGGameLoop()
        res = rpg.evaluate_tick(delta_ms=500)
        self.assertTrue(res["success"])
        self.assertEqual(res["tick"], 1)
        self.assertIn("TICK-", res["tick_token"])

    def test_core_engine_health(self):
        engine = CoreEngine()
        health = engine.health_check()
        self.assertEqual(health["status"], "HEALTHY")
        self.assertEqual(health["port"], 8765)

if __name__ == "__main__":
    unittest.main()
