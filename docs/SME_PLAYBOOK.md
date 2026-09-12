# Sovereign Mainframe & Autonomous Protocol Engine — SME Playbook

## 1. Role Definition & Scope
The Subject Matter Expert (SME) manages protocol lifecycle governance, cryptographic ledger auditing, multi-agent mesh topology, and dispute resolution across distributed sovereign nodes.

## 2. Operational Runbooks

### Runbook 01: Protocol FSM Deadlock Recovery
**Symptoms**: Agents report invalid state transition errors (`400 Invalid transition: locked -> idle`).
**Procedure**:
1. Check current FSM status:
   ```bash
   curl http://127.0.0.1:8765/api/v1/fsm/status?session_id=<SESSION_ID>
   ```
2. Verify if the session is locked in an unhandled exception state.
3. If unrecoverable, issue an administrative reset transition using the master key:
   ```bash
   curl -X POST http://127.0.0.1:8765/api/v1/fsm/transition \
     -H "Authorization: Bearer $MAINFRAME_SECRET_KEY" \
     -H "Content-Type: application/json" \
     -d '{"session_id":"<SESSION_ID>","from_state":"*","to_state":"idle","override":true}'
   ```

### Runbook 02: Journal Cryptographic Tamper Detection
**Symptoms**: Automated health check returns `journal_integrity: false`.
**Procedure**:
1. Run verification diagnostic:
   ```bash
   python3 src/cli.py verify-journal
   ```
2. The verification engine identifies the exact Sequence ID where `prev_hash != computed_hash`.
3. Compare local journal against SBB Vault Ledger replica:
   ```bash
   curl http://127.0.0.1:8766/api/v1/audit/verify
   ```
4. Restore clean chain segment from the verified replica.

### Runbook 03: P2P Network Partition Mitigation
**Symptoms**: Message delivery latency spikes, mailbox queue length exceeds 1000 items.
**Procedure**:
1. Query peer mailbox metrics:
   ```bash
   curl http://127.0.0.1:8765/api/v1/p2p/metrics
   ```
2. Identify unreachable peer node addresses.
3. Reroute outbound traffic through intermediate bridge relay nodes.
