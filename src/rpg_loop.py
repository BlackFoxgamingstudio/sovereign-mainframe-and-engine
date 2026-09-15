"""
RPG Game Loop & State Evaluator (FEAT-008-05)
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

class RPGGameLoop:
    """Production-grade discrete-event simulation engine with SQLite tick persistence and 12-level protocol state evolution."""

    PROTOCOL_LEVELS = [
        "1_GENESIS_INIT", "2_METRIC_SENSING", "3_TELEMETRY_ANALYSIS", "4_THREAT_ASSESSMENT",
        "5_DEFENSE_PROTOCOL", "6_ANOMALY_TRIAGE", "7_FSM_SYNCHRONIZATION", "8_P2P_SWARM_CONSENSUS",
        "9_RESOURCE_ALLOCATION", "10_TASK_EXECUTION", "11_JOURNAL_SEALING", "12_AUTONOMOUS_EQUILIBRIUM"
    ]

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.tick_count = 0
        self.world_state: Dict[str, Any] = {
            "power_grid_level": 100,
            "thermal_headroom": 85,
            "defense_shields": 100,
            "threat_level": "NOMINAL",
            "protocol_level": self.PROTOCOL_LEVELS[0],
            "active_anomalies": []
        }
        self._init_db()
        self._load_latest_tick()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rpg_world_state (
                    tick INTEGER PRIMARY KEY,
                    tick_token TEXT NOT NULL,
                    delta_ms INTEGER NOT NULL,
                    world_state_json TEXT NOT NULL,
                    events_json TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()

    def _load_latest_tick(self) -> None:
        with self._get_connection() as conn:
            cur = conn.execute("SELECT * FROM rpg_world_state ORDER BY tick DESC LIMIT 1")
            row = cur.fetchone()
            if row:
                self.tick_count = row["tick"]
                self.world_state = json.loads(row["world_state_json"])

    def evaluate_tick(
        self,
        delta_ms: int = 1000,
        active_entities: Optional[List[str]] = None,
        environmental_telemetry: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        self.tick_count += 1
        entities = active_entities or ["MainframeCore", "SentinelSRE", "HunterDefend"]
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Advance Protocol Level deterministically through the 12-level cycle
        level_idx = (self.tick_count - 1) % len(self.PROTOCOL_LEVELS)
        self.world_state["protocol_level"] = self.PROTOCOL_LEVELS[level_idx]

        # Apply Environmental Telemetry if provided, else apply realistic deterministic drift
        events = []
        if environmental_telemetry:
            if "temperature_c" in environmental_telemetry:
                temp = environmental_telemetry["temperature_c"]
                self.world_state["thermal_headroom"] = max(0, min(100, int(100 - (temp - 20) * 1.5)))
            if "power_watts" in environmental_telemetry:
                self.world_state["power_grid_level"] = max(10, min(100, int(100 - (environmental_telemetry["power_watts"] / 20))))

        # Periodic automated events & dynamic hazard generation
        if self.tick_count % 10 == 0:
            events.append({
                "event": "ROUTINE_SECURITY_PATROL",
                "status": "COMPLETED",
                "auditor": "Hunter",
                "tick": self.tick_count
            })

        if self.tick_count % 25 == 0:
            # Thermal pulse hazard simulation
            self.world_state["thermal_headroom"] = max(20, self.world_state["thermal_headroom"] - 25)
            events.append({
                "event": "THERMAL_PULSE_DETECTED",
                "severity": "WARNING",
                "headroom_pct": self.world_state["thermal_headroom"]
            })

        # Dynamic state evaluations
        if self.world_state["thermal_headroom"] < 50:
            self.world_state["threat_level"] = "ELEVATED"
            events.append({
                "event": "COOLING_OVERDRIVE_ENGAGED",
                "status": "ACTIVE",
                "target_delta": "+15% headroom"
            })
            # Automated recovery actuator
            self.world_state["thermal_headroom"] = min(85, self.world_state["thermal_headroom"] + 15)
        elif self.world_state["thermal_headroom"] >= 70:
            self.world_state["threat_level"] = "NOMINAL"

        # Shield recharge logic
        if self.world_state["defense_shields"] < 100:
            self.world_state["defense_shields"] = min(100, self.world_state["defense_shields"] + 5)

        tick_token_raw = f"TICK:{self.tick_count}:{self.world_state['protocol_level']}:{now}"
        tick_token = "TICK-" + hashlib.sha256(tick_token_raw.encode("utf-8")).hexdigest()[:12]

        # Persist tick to SQLite
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO rpg_world_state (tick, tick_token, delta_ms, world_state_json, events_json, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.tick_count, tick_token, delta_ms, json.dumps(self.world_state, sort_keys=True), json.dumps(events, sort_keys=True), now))
            conn.commit()

        return {
            "success": True,
            "tick": self.tick_count,
            "tick_token": tick_token,
            "delta_ms": delta_ms,
            "active_entities": entities,
            "world_state": self.world_state,
            "events_triggered": events,
            "protocol_level": self.world_state["protocol_level"],
            "timestamp": now
        }

    def get_world_state(self) -> Dict[str, Any]:
        return {
            "tick": self.tick_count,
            "world_state": self.world_state,
            "protocol_levels": self.PROTOCOL_LEVELS
        }
