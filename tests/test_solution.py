import sys
import unittest
import tempfile
import json
from pathlib import Path
from http.server import HTTPServer

# Add solution root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.fsm_engine import ProtocolFSM
from src.event_journal import EventJournal
from src.p2p_message_bus import P2PMessageBus
from src.task_router import TaskDecompositionRouter
from src.rpg_loop import RPGGameLoop
from src.core import CoreEngine
from n8n.webhook_adapter import MainframeHandler

class TestMainframeSolution(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_mainframe.db"

    def tearDown(self):
        self.temp_dir.cleanup()

    # --- FSM Engine Tests ---
    def test_fsm_valid_transition(self):
        fsm = ProtocolFSM("IDLE", db_path=str(self.db_path))
        res = fsm.transition("TASK_DECOMPOSING", "INCIDENT_ALERT")
        self.assertTrue(res["success"])
        self.assertEqual(res["current_state"], "TASK_DECOMPOSING")
        self.assertIn("TR-", res["transition"]["transition_id"])

    def test_fsm_invalid_transition(self):
        fsm = ProtocolFSM("IDLE", db_path=str(self.db_path))
        res = fsm.transition("JOURNAL_COMMITTED", "ILLEGAL_JUMP")
        self.assertFalse(res["success"])
        self.assertEqual(fsm.state, "IDLE")

    def test_fsm_multi_session_isolation(self):
        fsm = ProtocolFSM("IDLE", db_path=str(self.db_path))
        r1 = fsm.transition("TASK_DECOMPOSING", "ALERT_1", session_id="session_alpha")
        r2 = fsm.transition("ERROR_ESCALATION", "ALERT_2", session_id="session_beta")
        self.assertTrue(r1["success"])
        self.assertTrue(r2["success"])
        self.assertEqual(fsm.get_state("session_alpha")["current_state"], "TASK_DECOMPOSING")
        self.assertEqual(fsm.get_state("session_beta")["current_state"], "ERROR_ESCALATION")

    def test_fsm_persistence_across_instances(self):
        fsm1 = ProtocolFSM("IDLE", db_path=str(self.db_path))
        fsm1.transition("TASK_DECOMPOSING", "ALERT_BOOT", session_id="sess_persistent")

        # Simulate fresh reboot
        fsm2 = ProtocolFSM(db_path=str(self.db_path))
        state = fsm2.get_state("sess_persistent")
        self.assertEqual(state["current_state"], "TASK_DECOMPOSING")
        self.assertEqual(state["history_count"], 1)

    # --- Event Journal Tests ---
    def test_journal_append_and_integrity(self):
        journal = EventJournal(db_path=str(self.db_path))
        r1 = journal.append_event("TEST_A", "audit", {"key": "val1"})
        r2 = journal.append_event("TEST_B", "audit", {"key": "val2"})
        self.assertTrue(r1["success"])
        self.assertEqual(r2["index"], 1)
        self.assertTrue(journal.verify_integrity())

    def test_journal_replay_and_slicing(self):
        journal = EventJournal(db_path=str(self.db_path))
        journal.append_event("BOOT", "kernel", {"boot": True})
        journal.append_event("READY", "kernel", {"ready": True})
        journal.append_event("SYNC", "kernel", {"sync": True})

        replay = journal.replay(from_index=1, to_index=3)
        self.assertTrue(replay["success"])
        self.assertEqual(replay["replayed_count"], 2)
        self.assertEqual(replay["events"][0]["event_type"], "READY")

    def test_journal_persistence_and_reboot(self):
        j1 = EventJournal(db_path=str(self.db_path))
        j1.append_event("STEP_1", "worker", {"step": 1})
        j1.append_event("STEP_2", "worker", {"step": 2})

        # Fresh instance on same DB
        j2 = EventJournal(db_path=str(self.db_path))
        self.assertEqual(len(j2._journal), 2)
        self.assertTrue(j2.verify_integrity())
        r3 = j2.append_event("STEP_3", "worker", {"step": 3})
        self.assertEqual(r3["index"], 2)
        self.assertTrue(j2.verify_integrity())

    def test_journal_tamper_detection(self):
        journal = EventJournal(db_path=str(self.db_path))
        journal.append_event("A", "src", {"v": 1})
        journal.append_event("B", "src", {"v": 2})
        self.assertTrue(journal.verify_integrity())

        # Tamper directly with the SQLite database row
        with journal._get_connection() as conn:
            conn.execute("UPDATE event_journal SET data_json = '{\"v\": 999}' WHERE idx = 0")
            conn.commit()

        # Fresh journal load
        tampered_journal = EventJournal(db_path=str(self.db_path))
        self.assertFalse(tampered_journal.verify_integrity())
        audit = tampered_journal.audit_trail()
        self.assertEqual(audit["status"], "TAMPER_DETECTED")

    # --- P2P Message Bus Tests ---
    def test_p2p_message_dispatch_and_inbox(self):
        bus = P2PMessageBus(db_path=str(self.db_path))
        res = bus.dispatch("AgentA", "AgentB", "test.topic", {"msg": "hello"})
        self.assertTrue(res["success"])
        self.assertTrue(res["delivered"])
        inbox = bus.poll_inbox("AgentB")
        self.assertEqual(inbox["message_count"], 1)
        self.assertEqual(inbox["messages"][0]["payload"]["msg"], "hello")

    def test_p2p_acknowledgment_lifecycle(self):
        bus = P2PMessageBus(db_path=str(self.db_path))
        disp = bus.dispatch("Supervisor", "Worker", "task.do", {"id": 101})
        msg_id = disp["message_id"]
        ack_token = disp["ack_token"]

        ack_res = bus.acknowledge(msg_id, ack_token)
        self.assertTrue(ack_res["success"])
        self.assertEqual(ack_res["status"], "ACKNOWLEDGED")

    # --- Task Decomposition Tests ---
    def test_task_decomposition_router(self):
        router = TaskDecompositionRouter()
        res = router.decompose_objective("Mitigate thermal hardware crash dump", "HIGH")
        self.assertTrue(res["success"])
        self.assertGreater(res["subtasks_count"], 0)
        self.assertIn("SentinelSRE", res["assigned_personas"])
        self.assertEqual(res["classified_intent"], "REMEDIATION")
        self.assertIn("dag_edges", res)

    def test_task_decomposition_security_intent(self):
        router = TaskDecompositionRouter()
        res = router.decompose_objective("Conduct zero-trust security audit and vulnerability assessment", "MEDIUM")
        self.assertTrue(res["success"])
        self.assertEqual(res["classified_intent"], "SECURITY_AUDIT")
        self.assertIn("Hunter", res["assigned_personas"])

    # --- RPG Simulation Loop Tests ---
    def test_rpg_game_tick(self):
        rpg = RPGGameLoop(db_path=str(self.db_path))
        res = rpg.evaluate_tick(delta_ms=500)
        self.assertTrue(res["success"])
        self.assertEqual(res["tick"], 1)
        self.assertIn("TICK-", res["tick_token"])
        self.assertEqual(res["protocol_level"], "1_GENESIS_INIT")

    def test_rpg_persistence_and_drift(self):
        rpg1 = RPGGameLoop(db_path=str(self.db_path))
        for _ in range(5):
            rpg1.evaluate_tick()

        # Reboot instance
        rpg2 = RPGGameLoop(db_path=str(self.db_path))
        self.assertEqual(rpg2.tick_count, 5)
        tick6 = rpg2.evaluate_tick()
        self.assertEqual(tick6["tick"], 6)

    # --- Core Engine Unified Dispatcher Tests ---
    def test_core_engine_health(self):
        engine = CoreEngine(db_path=str(self.db_path))
        health = engine.health_check()
        self.assertEqual(health["status"], "HEALTHY")
        self.assertEqual(health["port"], 8765)
        self.assertIn("persistence", health)
        self.assertIn("journal_audit", health)

    def test_core_engine_execute_actions(self):
        engine = CoreEngine(db_path=str(self.db_path))

        # 1. FSM action
        fsm_res = engine.execute_action("transition_protocol_state", {
            "target_state": "TASK_DECOMPOSING",
            "trigger_event": "START_AGENT",
            "session_id": "test_exec"
        })
        self.assertTrue(fsm_res["success"])

        # 2. Journal action
        j_res = engine.execute_action("journal_agent_events", {
            "event_type": "AUDIT_TEST",
            "source": "unit_test",
            "data": {"foo": "bar"}
        })
        self.assertTrue(j_res["success"])

        # 3. P2P action
        p2p_res = engine.execute_action("dispatch_agent_message", {
            "sender": "Agent1",
            "recipient": "Agent2",
            "topic": "test",
            "payload": {"hello": "world"}
        })
        self.assertTrue(p2p_res["success"])

        # 4. Task action
        task_res = engine.execute_action("route_subagent_task", {
            "objective": "Investigate database latency spike",
            "complexity": "HIGH"
        })
        self.assertTrue(task_res["success"])

        # 5. RPG tick action
        rpg_res = engine.execute_action("evaluate_rpg_game_tick", {"delta_ms": 1000})
        self.assertTrue(rpg_res["success"])

    def test_core_engine_unknown_action(self):
        engine = CoreEngine(db_path=str(self.db_path))
        res = engine.execute_action("non_existent_action_xyz")
        self.assertFalse(res["success"])
        self.assertIn("supported_actions", res)

if __name__ == "__main__":
    unittest.main()
