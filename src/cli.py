#!/usr/bin/env python3
"""
CLI Invocation Harness for sovereign-mainframe-and-engine
Author: Russell Alan Powers
"""
import sys
import json
import argparse
from pathlib import Path

# Add solution to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core import CoreEngine

def main():
    parser = argparse.ArgumentParser(description="SBB Sovereign Mainframe CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # health
    subparsers.add_parser("health", help="Check mainframe health")

    # fsm
    fsm_p = subparsers.add_parser("fsm", help="Transition or view FSM state")
    fsm_p.add_argument("--state", type=str, help="Target state")
    fsm_p.add_argument("--event", type=str, default="CLI_EVENT", help="Trigger event")

    # journal
    j_p = subparsers.add_parser("journal", help="Event journal operations")
    j_p.add_argument("--append", action="store_true", help="Append event")
    j_p.add_argument("--replay", action="store_true", help="Replay events")
    j_p.add_argument("--data", type=str, default="{}", help="Event JSON data")

    # p2p
    p2p_p = subparsers.add_parser("p2p", help="Dispatch P2P message")
    p2p_p.add_argument("--to", type=str, required=True, help="Recipient agent")
    p2p_p.add_argument("--topic", type=str, required=True, help="Topic")
    p2p_p.add_argument("--data", type=str, default="{}", help="Message payload")

    # task
    t_p = subparsers.add_parser("task", help="Decompose an autonomous objective")
    t_p.add_argument("--objective", type=str, required=True, help="Objective statement")
    t_p.add_argument("--complexity", type=str, default="MEDIUM", help="Complexity")

    # rpg
    subparsers.add_parser("rpg-tick", help="Evaluate single RPG simulation tick")

    args = parser.parse_args()
    engine = CoreEngine()

    if args.command == "health" or not args.command:
        print(json.dumps(engine.health_check(), indent=2))
    elif args.command == "fsm":
        if args.state:
            res = engine.fsm.transition(args.state, args.event)
        else:
            res = engine.fsm.get_state()
        print(json.dumps(res, indent=2))
    elif args.command == "journal":
        if args.append:
            payload = json.loads(args.data)
            res = engine.journal.append_event("CLI_APPEND", "cli", payload)
        else:
            res = engine.journal.replay()
        print(json.dumps(res, indent=2))
    elif args.command == "p2p":
        payload = json.loads(args.data)
        res = engine.bus.dispatch("cli_operator", args.to, args.topic, payload)
        print(json.dumps(res, indent=2))
    elif args.command == "task":
        res = engine.router.decompose_objective(args.objective, args.complexity)
        print(json.dumps(res, indent=2))
    elif args.command == "rpg-tick":
        res = engine.rpg.evaluate_tick()
        print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()
