# Sovereign Mainframe & Protocol State Machine (`sovereign-mainframe-and-engine`)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![OpenAPI 3.1](https://img.shields.io/badge/OpenAPI-3.1.0-brightgreen.svg)](/openapi.json)
[![Swagger UI](https://img.shields.io/badge/Swagger_UI-Port_8765-blue.svg)](http://localhost:8765/docs)

Autonomous decentralized multi-agent orchestrator featuring:
- **Finite State Machine Protocol Engine**: Deterministic state transitions (`UNINITIALIZED` -> `IDLE` -> `TASK_DECOMPOSING` -> `AGENT_DISPATCHING` -> `AWAITING_CONSENSUS` -> `JOURNAL_COMMITTED`).
- **Cryptographic Event Journal**: Append-only hash-chained ledger guaranteeing deterministic replay and tamper verification.
- **P2P Agent Message Bus**: Non-blocking peer-to-peer messaging with correlation IDs and ACK tokens.
- **Autonomous Task Decomposition Router**: Breaks high-level objectives into granular steps assigned to personas (`SentinelSRE`, `NovaPro`, etc.).
- **RPG Simulation Loop**: Deterministic game loop driving autonomous agent progression.

## Microservice API
- **Swagger UI**: [http://localhost:8765/docs](http://localhost:8765/docs)
- **OpenAPI 3.1**: [http://localhost:8765/openapi.json](http://localhost:8765/openapi.json)
- **Health Check**: `GET http://localhost:8765/healthz`
