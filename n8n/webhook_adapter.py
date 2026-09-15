#!/usr/bin/env python3
"""
Zero-Dependency REST Microservice Adapter for sovereign-mainframe-and-engine
Port: 8765
Features: OpenAPI 3.1, Interactive Swagger UI (/docs), CloudEvents & n8n Custom Node Execution (/api/v1/execute)
Author: Russell Alan Powers
"""
import sys
import os
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

SOLUTION_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SOLUTION_ROOT))

from src.core import CoreEngine

PORT = int(os.environ.get("SBB_MAINFRAME_PORT", 8765))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [MainframeAdapter] %(message)s")
logger = logging.getLogger("MainframeAdapter")

engine = CoreEngine()

OPENAPI_SPEC = {
    "openapi": "3.1.0",
    "info": {
        "title": "SBB Solution 08: Sovereign Mainframe & Protocol State Machine API",
        "description": "Deterministic Multi-Agent Mainframe exposing FSM protocol transitions, cryptographically verified event replay, P2P agent routing, and RPG simulation loop with universal action execution.",
        "version": "1.0.0",
        "contact": {"name": "Russell Alan Powers", "email": "russell@sovereignbizbox.io"}
    },
    "servers": [{"url": f"http://127.0.0.1:{PORT}", "description": "Local Mainframe Service"}],
    "paths": {
        "/healthz": {
            "get": {
                "summary": "Service Health & State Summary",
                "responses": {"200": {"description": "Health status", "content": {"application/json": {"schema": {"type": "object"}}}}}
            }
        },
        "/api/v1/execute": {
            "post": {
                "summary": "Universal Action Execution Gateway (n8n Custom Node Integration)",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string", "example": "transition_protocol_state"},
                                    "payload": {"type": "object"}
                                },
                                "required": ["action"]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Action execution result"}}
            }
        },
        "/api/v1/fsm/transition": {
            "post": {
                "summary": "FEAT-008-01: Transition FSM Protocol State",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "target_state": {"type": "string", "example": "TASK_DECOMPOSING"},
                                    "trigger_event": {"type": "string", "example": "START_TRIAGE"},
                                    "session_id": {"type": "string", "example": "default"},
                                    "context": {"type": "object"}
                                },
                                "required": ["target_state"]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "State transition result"}}
            }
        },
        "/api/v1/journal/append": {
            "post": {
                "summary": "FEAT-008-02: Append Immutable Event to Journal",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "event_type": {"type": "string", "example": "INCIDENT_RESOLVED"},
                                    "source": {"type": "string", "example": "SentinelSRE"},
                                    "data": {"type": "object"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Appended record with integrity hash"}}
            }
        },
        "/api/v1/journal/replay": {
            "get": {
                "summary": "FEAT-008-02: Replay Event Journal & Verify Chain Integrity",
                "responses": {"200": {"description": "Replay stream"}}
            }
        },
        "/api/v1/p2p/dispatch": {
            "post": {
                "summary": "FEAT-008-03: Dispatch P2P Agent Message",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "sender": {"type": "string", "example": "SupervisorAgent"},
                                    "recipient": {"type": "string", "example": "SentinelSRE"},
                                    "topic": {"type": "string", "example": "thermal.alert"},
                                    "payload": {"type": "object"}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Message dispatch acknowledgment"}}
            }
        },
        "/api/v1/agent/route-task": {
            "post": {
                "summary": "FEAT-008-04: Decompose Autonomous Objective into Tasks",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "objective": {"type": "string", "example": "Resolve critical edge thermal runaway"},
                                    "complexity": {"type": "string", "example": "HIGH"},
                                    "max_subtasks": {"type": "integer", "example": 4}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Decomposed subtasks and assigned personas"}}
            }
        },
        "/api/v1/rpg/tick": {
            "post": {
                "summary": "FEAT-008-05: Evaluate RPG Game Loop & State Simulation Tick",
                "responses": {"200": {"description": "Evaluated world state"}}
            }
        }
    }
}

SWAGGER_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>SBB Solution 08 - Sovereign Mainframe API</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css" />
  <style>body {{ margin: 0; padding: 0; background: #fafafa; }} .topbar {{ display: none; }}</style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.onload = () => {{
      window.ui = SwaggerUIBundle({{
        url: '/openapi.json',
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [SwaggerUIBundle.presets.apis]
      }});
    }};
  </script>
</body>
</html>"""

class MainframeHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, data: dict):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/healthz", "/health", "/"):
            self._send_json(200, engine.health_check())
        elif self.path == "/openapi.json":
            self._send_json(200, OPENAPI_SPEC)
        elif self.path == "/docs":
            body = SWAGGER_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith("/api/v1/journal/replay"):
            self._send_json(200, engine.journal.replay())
        elif self.path.startswith("/api/v1/journal/audit"):
            self._send_json(200, engine.journal.audit_trail())
        elif self.path.startswith("/api/v1/fsm/sessions"):
            self._send_json(200, {"sessions": engine.fsm.list_sessions()})
        else:
            self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        auth_header = self.headers.get("X-SBB-Auth")
        expected_secret = os.environ.get("SBB_SHARED_SECRET", "sbb_local_dev_secret_2026")
        if auth_header and auth_header != expected_secret:
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Unauthorized: Invalid X-SBB-Auth header"}')
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            data = json.loads(body)
        except Exception:
            data = {}

        # Universal Action Execution Gateway (Used by n8n custom nodes)
        if self.path in ("/api/v1/execute", "/"):
            action = data.get("action", "fsm_get_state")
            payload = data.get("payload", {})
            result = engine.execute_action(action, payload)
            self._send_json(200, result)
            return

        # Explicit Specific Microservice Endpoints
        if self.path == "/api/v1/fsm/transition":
            target = data.get("target_state", "IDLE")
            event = data.get("trigger_event", "HTTP_REQUEST")
            ctx = data.get("context", {})
            session_id = data.get("session_id", "default")
            self._send_json(200, engine.fsm.transition(target, event, ctx, session_id=session_id))
        elif self.path == "/api/v1/journal/append":
            etype = data.get("event_type", "GENERIC_EVENT")
            src = data.get("source", "n8n")
            edata = data.get("data", data)
            self._send_json(200, engine.journal.append_event(etype, src, edata))
        elif self.path == "/api/v1/p2p/dispatch":
            snd = data.get("sender", "n8n_workflow")
            rcp = data.get("recipient", "SentinelSRE")
            topic = data.get("topic", "agent.message")
            payload = data.get("payload", data)
            self._send_json(200, engine.bus.dispatch(snd, rcp, topic, payload))
        elif self.path == "/api/v1/agent/route-task":
            obj = data.get("objective", "Autonomous system optimization")
            cplx = data.get("complexity", "MEDIUM")
            subtasks = int(data.get("max_subtasks", 4))
            self._send_json(200, engine.router.decompose_objective(obj, cplx, subtasks))
        elif self.path == "/api/v1/rpg/tick":
            delta_ms = int(data.get("delta_ms", 1000))
            entities = data.get("active_entities")
            telemetry = data.get("environmental_telemetry")
            self._send_json(200, engine.rpg.evaluate_tick(delta_ms, entities, telemetry))
        else:
            self._send_json(404, {"error": "Not Found"})

    def log_message(self, format, *args):
        pass

def run():
    server = HTTPServer(("0.0.0.0", PORT), MainframeHandler)
    logger.info("Mainframe Microservice listening on http://0.0.0.0:%d (Swagger UI at /docs)", PORT)
    server.serve_forever()

if __name__ == "__main__":
    run()
