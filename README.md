# 🏛️ Sovereign Mainframe & Autonomous Protocol Engine

[![CI](https://github.com/BlackFoxgamingstudio/sovereign-mainframe-and-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/BlackFoxgamingstudio/sovereign-mainframe-and-engine/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Zero-Dependency](https://img.shields.io/badge/Dependencies-Standard%20Library-green.svg)](pyproject.toml)
[![OpenAPI 3.1](https://img.shields.io/badge/OpenAPI-3.1-orange.svg)](http://localhost:8765/openapi.json)
[![n8n Ready](https://img.shields.io/badge/n8n-Workflow%20Packaged-ff6d5a.svg)](n8n/workflow.json)

The **Sovereign Mainframe & Autonomous Protocol Engine** (`SOL-008`, Port `8765`) is a sovereign, zero-dependency distributed state and multi-agent coordination core. It provides deterministic finite state machines, cryptographic hash-chained event journals, peer-to-peer agent messaging, hierarchical task routing, and discrete-clock RPG digital twin simulation.

---

## ⚡ Key Highlights
- **Deterministic State Protocol**: Mathematical state machine transition enforcement with SHA-256 tokens.
- **Cryptographic Hash Chain**: Merkle-adjacent event journal with sub-millisecond tamper verification and replay.
- **Peer-to-Peer Inter-Agent Mesh**: Asynchronous mailbox queues and cryptographic delivery receipts.
- **Hierarchical Task Router**: Decomposes macro goals into sub-agent DAGs with automatic persona dispatch.
- **RPG Digital Twin Engine**: 12-level state machine simulation loop with discrete clock evaluation.
- **Zero Third-Party Pip Dependencies**: Runs anywhere on bare-metal POSIX, Docker, or Raspberry Pi.

---

## 🛠️ Micro-Tool Function Catalog (100-Fold Decomposition)

| Micro-Tool | Endpoint | CLI Subcommand | Domain |
|---|---|---|---|
| **FSM State Transition** | `POST /api/v1/fsm/transition` | `fsm` | Protocol Enforcement |
| **Journal Event Append** | `POST /api/v1/journal/append` | `journal` | Cryptographic Ledger |
| **Verify Hash Chain** | `GET /api/v1/journal/verify` | `verify-journal` | Tamper Detection |
| **P2P Message Send** | `POST /api/v1/p2p/send` | `p2p` | Agent Communication |
| **Task Decomposition** | `POST /api/v1/task/decompose` | `task` | Autonomous Planning |
| **RPG Simulation Tick** | `POST /api/v1/rpg/tick` | `rpg-tick` | Digital Twin Clock |

---

## 🚀 Quick Start

```bash
# 1. Run unit test suite
python3 -m unittest discover tests/

# 2. Launch HTTP Microservice Adapter on port 8765
python3 n8n/webhook_adapter.py

# 3. View Interactive Swagger Documentation
open http://127.0.0.1:8765/docs
```

---

## 🔌 n8n Workflow Integration

This repository ships with a pre-wired n8n workflow (`n8n/workflow.json`) configured with:
- Webhook Inbound Gateway: `POST /webhook/mainframe`
- Dead Letter Queue (DLQ): Auto-reroutes failures to workflow `e7rR9pL2Km5Vx0Q3`
- Platform Variable Bindings: Configurable via n8n variables (`SBB_MAINFRAME_URL`, `SBB_VAULT_BRIDGE_URL`)

---

## 📜 License
MIT License. Developed for the Sovereign Biz Box autonomous platform ecosystem.
