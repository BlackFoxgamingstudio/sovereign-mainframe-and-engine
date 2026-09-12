# Sovereign Mainframe & Autonomous Protocol Engine — Developer Guide

## 1. Quick Start

### Prerequisites
- Python 3.10+ (Standard Library only — zero external pip packages required for core runtime!)
- curl / HTTP client
- (Optional) n8n instance for visual pipeline orchestration

### Installation & Standalone Run
```bash
cd solutions/sovereign-mainframe-and-engine
python3 -m unittest discover tests/
python3 n8n/webhook_adapter.py
```
The microservice starts on `http://127.0.0.1:8765` with interactive Swagger UI available at `http://127.0.0.1:8765/docs`.

## 2. CLI Tool Reference

The engine includes a multi-command CLI (`src/cli.py`):

```bash
# Execute an FSM State Transition
python3 src/cli.py fsm --session sess-101 --from idle --to active --user alice

# Append an Event to the Cryptographic Journal
python3 src/cli.py journal --topic io.sovereignbizbox.mainframe.task --payload '{"action":"deploy"}'

# Verify Cryptographic Journal Hash Chain
python3 src/cli.py verify-journal

# Send a Peer-to-Peer Inter-Agent Message
python3 src/cli.py p2p --from-node node-a --to-node node-b --subject "Ping" --body "Health check"

# Decompose a Complex Task
python3 src/cli.py task --goal "Deploy sovereign mesh" --complexity high

# Run an RPG Simulation Tick
python3 src/cli.py rpg-tick --delta 1.0
```

## 3. OpenAPI / REST Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Microservice liveness and active module status |
| `GET` | `/docs` | Interactive Swagger UI API playground |
| `GET` | `/openapi.json` | OpenAPI 3.1 schema specification |
| `POST` | `/api/v1/fsm/transition` | Enforce deterministic protocol state change |
| `POST` | `/api/v1/journal/append` | Cryptographically seal event into immutable ledger |
| `GET` | `/api/v1/journal/verify` | Verify Merkle/SHA-256 hash-chain integrity |
| `POST` | `/api/v1/p2p/send` | Deliver authenticated peer-to-peer message |
| `GET` | `/api/v1/p2p/inbox` | Retrieve queued messages for node ID |
| `POST` | `/api/v1/task/decompose` | Hierarchically split goal into sub-agent jobs |
| `POST` | `/api/v1/rpg/tick` | Advance discrete game simulation tick |

## 4. Running Tests

```bash
# Run pytest with coverage
pytest tests/ -v --cov=src

# Run standard library unittest
python3 -m unittest discover tests/
```
