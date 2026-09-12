"""
Deterministic Event Replay & Journaling Engine (FEAT-008-02)
Domain: Agentic Protocols & Distributed State
Author: Russell Alan Powers
"""
import time
import json
import hashlib
from typing import Dict, Any, List, Optional

class EventJournal:
    def __init__(self):
        self._journal: List[Dict[str, Any]] = []
        self._last_hash = "GENESIS_HASH_0000000000000000"

    def append_event(self, event_type: str, source: str, data: Dict[str, Any]) -> Dict[str, Any]:
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        index = len(self._journal)
        data_str = json.dumps(data, sort_keys=True)
        raw = f"{index}:{event_type}:{source}:{data_str}:{self._last_hash}:{now}"
        entry_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

        entry = {
            "index": index,
            "event_type": event_type,
            "source": source,
            "timestamp": now,
            "data": data,
            "previous_hash": self._last_hash,
            "entry_hash": entry_hash
        }
        self._journal.append(entry)
        self._last_hash = entry_hash

        return {
            "success": True,
            "index": index,
            "entry_hash": entry_hash,
            "journal_length": len(self._journal)
        }

    def replay(self, from_index: int = 0, to_index: Optional[int] = None) -> Dict[str, Any]:
        end = to_index if to_index is not None else len(self._journal)
        sliced = self._journal[from_index:end]
        return {
            "success": True,
            "replayed_count": len(sliced),
            "from_index": from_index,
            "to_index": end,
            "events": sliced,
            "integrity_verified": self.verify_integrity()
        }

    def verify_integrity(self) -> bool:
        prev = "GENESIS_HASH_0000000000000000"
        for e in self._journal:
            data_str = json.dumps(e["data"], sort_keys=True)
            raw = f"{e['index']}:{e['event_type']}:{e['source']}:{data_str}:{prev}:{e['timestamp']}"
            expected = hashlib.sha256(raw.encode("utf-8")).hexdigest()
            if e["entry_hash"] != expected:
                return False
            prev = e["entry_hash"]
        return True
