"""
Autonomous Task Decomposition Router (FEAT-008-04)
Domain: Agentic Protocols & Distributed State
Author: Russell Alan Powers
"""
import time
import hashlib
from typing import Dict, Any, List, Set

class TaskDecompositionRouter:
    """Autonomous hierarchical task decomposition engine with dependency DAG and persona capability routing."""

    PERSONA_CAPABILITIES: Dict[str, Dict[str, Any]] = {
        "SentinelSRE": {
            "keywords": ["infra", "thermal", "load", "crash", "hardware", "diagnostic", "cpu", "memory", "disk", "network", "reboot", "outage", "alert", "telemetry", "incident"],
            "role": "Site Reliability Engineer & Autonomous System Healer",
            "max_concurrency": 4
        },
        "Hunter": {
            "keywords": ["security", "audit", "vuln", "cve", "auth", "firewall", "patch", "exploit", "breach", "zero-day", "siem", "tamper"],
            "role": "Cybersecurity & Zero-Trust Defense Operator",
            "max_concurrency": 2
        },
        "NovaPro": {
            "keywords": ["research", "paper", "data", "deep_dive", "science", "ast", "analysis", "algorithm", "math", "benchmark", "synthesis"],
            "role": "Principal Research Scientist & Data Modeling Specialist",
            "max_concurrency": 3
        },
        "ChefPro": {
            "keywords": ["resource", "recipe", "inventory", "supply", "kitchen", "provision", "quota", "allocation", "storage", "asset"],
            "role": "Resource Provisioning & Asset Supply Chain Officer",
            "max_concurrency": 4
        },
        "Grace": {
            "keywords": ["customer", "support", "triage", "empathy", "ticket", "escalation", "notification", "comms", "status-page", "dispatch"],
            "role": "Communications Dispatcher & Stakeholder Liaison",
            "max_concurrency": 5
        }
    }

    INTENT_PATTERNS: Dict[str, List[str]] = {
        "REMEDIATION": ["crash", "thermal", "runaway", "failure", "incident", "healer", "remediation", "outage"],
        "SECURITY_AUDIT": ["security", "audit", "cve", "vulnerability", "auth", "zero-trust", "firewall", "breach"],
        "RESEARCH": ["research", "paper", "evaluate", "investigate", "benchmark", "analysis", "compare"],
        "PROVISIONING": ["provision", "deploy", "scale", "allocate", "setup", "install", "spin-up"]
    }

    def _classify_intent(self, objective_lower: str) -> str:
        words = set(objective_lower.split())
        for intent, triggers in self.INTENT_PATTERNS.items():
            if any(t in words or t in objective_lower for t in triggers):
                return intent
        return "GENERAL_AUTOMATION"

    def _match_personas(self, objective_lower: str) -> List[str]:
        scores: Dict[str, int] = {}
        words = set(objective_lower.split())

        for persona, meta in self.PERSONA_CAPABILITIES.items():
            matched_keywords = [k for k in meta["keywords"] if k in words or k in objective_lower]
            scores[persona] = len(matched_keywords)

        sorted_personas = sorted([p for p, s in scores.items() if s > 0], key=lambda p: scores[p], reverse=True)
        if not sorted_personas:
            sorted_personas = ["SentinelSRE"]
        return sorted_personas

    def decompose_objective(
        self,
        objective: str,
        complexity: str = "MEDIUM",
        max_subtasks: int = 4
    ) -> Dict[str, Any]:
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        obj_id = "OBJ-" + hashlib.sha256(f"{objective}:{now}".encode("utf-8")).hexdigest()[:12]
        obj_lower = objective.lower()

        intent = self._classify_intent(obj_lower)
        assigned_personas = self._match_personas(obj_lower)
        primary_persona = assigned_personas[0]
        secondary_persona = assigned_personas[1] if len(assigned_personas) > 1 else assigned_personas[0]

        # Dynamic subtask blueprints based on classified intent
        if intent == "REMEDIATION":
            blueprint = [
                ("Telemetry Triage & Environmental Isolation", primary_persona, "Ingest telemetry, parse anomaly vectors, and establish blast-radius containment boundary."),
                ("Root Cause Analysis & Boundary Constraint Check", secondary_persona, "Correlate telemetry markers against historical event journal to identify root cause."),
                ("Execute Deterministic Remediation Protocol", primary_persona, "Dispatch automated remediation commands and engage mitigation actuators."),
                ("Post-Remediation Verification & Cryptographic Ledger Commit", "Hunter" if "Hunter" in assigned_personas else primary_persona, "Verify system convergence, run health probes, and seal audit log into Event Journal.")
            ]
        elif intent == "SECURITY_AUDIT":
            blueprint = [
                ("Zero-Trust Surface Inspection & Credential Scan", "Hunter", "Audit service endpoints, inspect authorization tokens, and detect unauthorized drift."),
                ("Vulnerability Matrix Assessment", "NovaPro" if "NovaPro" in assigned_personas else "Hunter", "Cross-reference CVE databases and evaluate exploitability vectors."),
                ("Apply Protective Patch & Security Hardening", "Hunter", "Enforce firewall access control lists, rotate API secrets, and apply security controls."),
                ("Verify Cryptographic Chain Integrity", primary_persona, "Run Merkle tree validation across all platform ledgers and commit audit report.")
            ]
        elif intent == "RESEARCH":
            blueprint = [
                ("Literature & Dataset Retrieval", "NovaPro", "Collect technical specifications, research whitepapers, and dataset artifacts."),
                ("Synthesis & Feature Extraction", "NovaPro", "Perform dense/sparse semantic extraction and compile comparative feature matrices."),
                ("Benchmark & Architecture Evaluation", secondary_persona, "Execute benchmark simulations and evaluate architectural trade-offs."),
                ("Executive Summary & Artifact Publication", "Grace" if "Grace" in assigned_personas else "NovaPro", "Format findings into structured markdown and notify orchestration bus.")
            ]
        else:
            blueprint = [
                ("Ingest Context & Validate Input Vector", primary_persona, "Analyze input parameters and establish execution preconditions."),
                ("Synthesize Solution Plan & Evaluate Constraints", secondary_persona, "Formulate deterministic execution steps and verify resource allocations."),
                ("Execute Core Domain Pipeline", primary_persona, "Trigger domain microservice actions and process payload."),
                ("Audit Trail Commitment & State Verification", primary_persona, "Commit state transition to FSM and log cryptographic receipt.")
            ]

        subtasks: List[Dict[str, Any]] = []
        blueprint_slice = blueprint[:max_subtasks]

        for i, (title, persona, detail) in enumerate(blueprint_slice):
            subtask_id = f"{obj_id}-{i+1:02d}"
            deps = [f"{obj_id}-{i:02d}"] if i > 0 else []
            subtasks.append({
                "subtask_id": subtask_id,
                "step": i + 1,
                "title": title,
                "description": f"[{persona}] {title}: {detail}",
                "target_persona": persona,
                "persona_role": self.PERSONA_CAPABILITIES.get(persona, {}).get("role", "Autonomous Agent"),
                "dependencies": deps,
                "status": "PENDING",
                "estimated_duration_ms": 250 if complexity == "LOW" else (750 if complexity == "MEDIUM" else 1500),
                "verification_criteria": f"Subtask {subtask_id} must emit a deterministic SHA-256 success token."
            })

        complexity_multiplier = 3 if complexity == "HIGH" else (2 if complexity == "MEDIUM" else 1)

        return {
            "success": True,
            "objective_id": obj_id,
            "objective": objective,
            "complexity": complexity,
            "classified_intent": intent,
            "subtasks_count": len(subtasks),
            "subtasks": subtasks,
            "assigned_personas": list(set(assigned_personas)),
            "dag_edges": [{"from": s["dependencies"][0], "to": s["subtask_id"]} for s in subtasks if s["dependencies"]],
            "estimated_ticks": len(subtasks) * complexity_multiplier,
            "timestamp": now
        }
