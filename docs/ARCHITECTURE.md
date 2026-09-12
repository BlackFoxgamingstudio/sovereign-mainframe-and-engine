# Sovereign Mainframe & Autonomous Protocol Engine — Architecture

## 1. Executive Summary
The **Sovereign Mainframe & Autonomous Protocol Engine** (`SOL-008`, Port `8765`) provides a zero-dependency, mathematically verifiable distributed coordination layer for multi-agent autonomous platforms. It unifies protocol state machines, cryptographically chained event journals, peer-to-peer message meshes, hierarchical task decomposition, and simulated world-state RPG tick loops into a coherent sovereign core.

## 2. Micro-Solution Subsystem Topology

```
+-----------------------------------------------------------------------------------+
|                           Sovereign Mainframe Core                                 |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [FEAT-008-01: FSM Engine] <----> [FEAT-008-02: Cryptographic Event Journal]     |
|   Strict Transition Matrix             SHA-256 Chained Immutable Ledger          |
|   Deterministic State Verifier         Full Event Replay & Reconstruction         |
|             ^                                       ^                             |
|             |                                       |                             |
|  [FEAT-008-03: P2P Message Bus] <-> [FEAT-008-04: Autonomous Task Router]        |
|   Peer Mesh Routing & Delivery         Hierarchical Decomposition Engine          |
|   Cryptographic Signature Verif.       Persona-Aware Assignment (Sentinel, SRE)  |
|             ^                                       ^                             |
|             +-------------------+-------------------+                             |
|                                 |                                                 |
|                   [FEAT-008-05: RPG Simulation Engine]                            |
|                    Discrete Tick Evaluator & Entity State Matrix                  |
+-----------------------------------------------------------------------------------+
                                  |
                +-----------------+-----------------+
                |                                   |
        [HTTP / REST Gateway]              [n8n Workflow Canvas]
          Port 8765 FastAPI/BaseHTTP        wf-008-mainframe-engine
          Swagger UI /docs                   Topic: io.sovereignbizbox.mainframe.*
```

## 3. Core Modules & Contracts

### 3.1 Finite State Machine (FEAT-008-01)
- **File**: `src/fsm_engine.py`
- **Class**: `FSMEngine`
- **Specification**: Enforces deterministic state transitions (`idle` -> `active` -> `processing` -> `completed` / `error`). Any transition outside the strict transition table is rejected with a cryptographically signed error response.
- **Hash Integrity**: Emits a SHA-256 transition hash sealing previous state, target state, actor ID, and payload snapshot.

### 3.2 Cryptographic Event Journal (FEAT-008-02)
- **File**: `src/event_journal.py`
- **Class**: `EventJournal`
- **Specification**: Implements a Merkle-adjacent immutable linear hash chain:
  `Entry_Hash = SHA256(Sequence_ID + Prev_Hash + Timestamp + Topic + Payload)`
- **Verification**: `verify_chain_integrity()` iterates from Genesis block to head, mathematically proving zero tampering.
- **Replay**: `replay_events(from_seq)` emits state restoration deltas.

### 3.3 Peer-to-Peer Message Bus (FEAT-008-03)
- **File**: `src/p2p_message_bus.py`
- **Class**: `P2PMessageBus`
- **Specification**: Coordinates autonomous agents across distributed node addresses. Provides store-and-forward peer mailboxes, TTL-based eviction, and cryptographic acknowledgment tokens.

### 3.4 Autonomous Task Decomposition Router (FEAT-008-04)
- **File**: `src/task_router.py`
- **Class**: `TaskRouter`
- **Specification**: Deconstructs macro objectives into atomic child tasks. Automatically assigns sub-tasks to specialized personas (`SentinelSRE`, `CloudArchitect`, `DevOpsLead`, `SecurityAuditor`) with dependency graphs.

### 3.5 RPG Digital Twin Simulation Loop (FEAT-008-05)
- **File**: `src/rpg_loop.py`
- **Class**: `RPGSimulationLoop`
- **Specification**: Discrete clock-driven state simulation loop. Tracks entity HP, MP, status effects, and world event triggers, providing gamified operational observability.

## 4. Integration Matrix
- **Central Event Bus (Sol 00)**: Subscribes to `io.sovereignbizbox.mainframe.*` via webhook `/webhook/events`.
- **SBB Vault Bridge (Port 8766)**: All immutable state transitions and journal records persist to the decentralized ledger.
- **n8n Automation Engine**: Workflow `m7rR8pL2Km5Vx0M1` exposes visual pipeline with DLQ rerouting to `e7rR9pL2Km5Vx0Q3`.
