# Sovereign Mainframe & Autonomous Protocol Engine — Standard Operating Procedures (SOP)

## SOP-MF-001: Production Node Deployment
1. Verify host environment meets baseline requirements (Python 3.10+, 512MB RAM, POSIX filesystem).
2. Clone repository to `/opt/sovereign/mainframe`.
3. Copy `.env.example` to `.env` and configure `MAINFRAME_SECRET_KEY` with 32 cryptographically secure bytes.
4. Launch daemon via systemd unit or container:
   ```bash
   docker compose up -d
   ```
5. Verify health endpoint: `curl -f http://127.0.0.1:8765/health`.

## SOP-MF-002: Secret Key Rotation
1. Generate new 32-byte hexadecimal key:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
2. Update `.env` and n8n platform variable `SBB_MAINFRAME_SECRET_KEY`.
3. Issue graceful reload signal to the daemon:
   ```bash
   pkill -HUP -f "n8n/webhook_adapter.py"
   ```
4. Perform smoke test on `/api/v1/fsm/transition`.

## SOP-MF-003: Daily Cryptographic Integrity Audit
1. Schedule a cron or n8n recurring trigger calling `/api/v1/journal/verify`.
2. Ensure log status is recorded to the central SBB audit database.
3. Trigger DLQ alert `e7rR9pL2Km5Vx0Q3` if hash mismatch is detected.
