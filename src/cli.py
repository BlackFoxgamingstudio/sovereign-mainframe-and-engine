#!/usr/bin/env python3
"""
CLI Invocation Harness for sovereign-mainframe-and-engine
Author: Russell Alan Powers
"""
import sys
import json
import argparse
from pathlib import Path

# Add solution root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core import CoreEngine

def main():
    parser = argparse.ArgumentParser(description="SBB Sovereign Mainframe CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # health
    subparsers.add_parser("health", help="Check mainframe health and persistence status")

    # execute (universal action gateway)
    exec_p = subparsers.add_parser("execute", help="Execute any mainframe microservice action")
    exec_p.add_argument("--action", type=str, required=True, help="Action name to execute")
    exec_p.add_argument("--payload", type=str, default="{}", help="JSON payload")

    # fsm
    fsm_p = subparsers.add_parser("fsm", help="Transition or view FSM state")
    fsm_p.add_argument("--state", type=str, help="Target state")
    fsm_p.add_argument("--event", type=str, default="CLI_EVENT", help="Trigger event")
    fsm_p.add_argument("--session", type=str, default="default", help="Session ID")
    fsm_p.add_argument("--sessions", action="store_true", help="List all sessions")

    # journal
    j_p = subparsers.add_parser("journal", help="Event journal operations")
    j_p.add_argument("--append", action="store_true", help="Append event")
    j_p.add_argument("--replay", action="store_true", help="Replay events")
    j_p.add_argument("--audit", action="store_true", help="Audit Merkle chain integrity")
    j_p.add_argument("--data", type=str, default="{}", help="Event JSON data")

    # p2p
    p2p_p = subparsers.add_parser("p2p", help="Dispatch or poll P2P messages")
    p2p_p.add_argument("--to", type=str, help="Recipient agent")
    p2p_p.add_argument("--from-agent", type=str, default="cli_operator", help="Sender agent")
    p2p_p.add_argument("--topic", type=str, default="general.dispatch", help="Topic")
    p2p_p.add_argument("--data", type=str, default="{}", help="Message payload")
    p2p_p.add_argument("--poll", type=str, help="Poll messages for given agent ID")

    # task
    t_p = subparsers.add_parser("task", help="Decompose an autonomous objective into a DAG")
    t_p.add_argument("--objective", type=str, required=True, help="Objective statement")
    t_p.add_argument("--complexity", type=str, default="MEDIUM", help="Complexity (LOW, MEDIUM, HIGH)")
    t_p.add_argument("--max-tasks", type=int, default=4, help="Max subtasks")

    # rpg
    rpg_p = subparsers.add_parser("rpg-tick", help="Evaluate single RPG simulation tick")
    rpg_p.add_argument("--delta-ms", type=int, default=1000, help="Delta milliseconds")

    args = parser.parse_args()
    engine = CoreEngine()

    if args.command == "health" or not args.command:
        print(json.dumps(engine.health_check(), indent=2))
    elif args.command == "execute":
        payload = json.loads(args.payload)
        res = engine.execute_action(args.action, payload)
        print(json.dumps(res, indent=2))
    elif args.command == "fsm":
        if args.sessions:
            res = engine.fsm.list_sessions()
        elif args.state:
            res = engine.fsm.transition(args.state, args.event, session_id=args.session)
        else:
            res = engine.fsm.get_state(session_id=args.session)
        print(json.dumps(res, indent=2))
    elif args.command == "journal":
        if args.append:
            payload = json.loads(args.data)
            res = engine.journal.append_event("CLI_APPEND", "cli", payload)
        elif args.audit:
            res = engine.journal.audit_trail()
        else:
            res = engine.journal.replay()
        print(json.dumps(res, indent=2))
    elif args.command == "p2p":
        if args.poll:
            res = engine.bus.poll_inbox(args.poll)
        elif args.to:
            payload = json.loads(args.data)
            res = engine.bus.dispatch(args.from_agent, args.to, args.topic, payload)
        else:
            res = engine.bus.get_mailbox_stats()
        print(json.dumps(res, indent=2))
    elif args.command == "task":
        res = engine.router.decompose_objective(args.objective, args.complexity, args.max_tasks)
        print(json.dumps(res, indent=2))
    elif args.command == "rpg-tick":
        res = engine.rpg.evaluate_tick(delta_ms=args.delta_ms)
        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
