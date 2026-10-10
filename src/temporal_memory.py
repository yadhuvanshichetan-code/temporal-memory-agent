"""
Temporal Memory — triples with valid_from / valid_to.
When a new fact supersedes an old one, the old fact's validity is closed.

Now supports persistence:
  - save(path) — write all facts to a JSON file
  - load(path) — read facts back from a JSON file
"""

import json
import os
from datetime import datetime


class TemporalMemory:
    def __init__(self):
        # Each fact: dict with subject, predicate, object, valid_from, valid_to, confidence
        self.facts = []

    def add(self, subject: str, predicate: str, obj: str,
            timestamp: str = None, confidence: float = 1.0):
        """
        Add a fact. If a fact with the same subject+predicate is currently active,
        close it (set valid_to = timestamp) so the new fact wins.
        """
        ts = timestamp or datetime.now().isoformat()

        # Invalidate any currently-active fact with same subject + predicate
        for f in self.facts:
            if (f["subject"] == subject
                    and f["predicate"] == predicate
                    and f["valid_to"] is None):
                f["valid_to"] = ts

        # Add the new fact
        self.facts.append({
            "subject": subject,
            "predicate": predicate,
            "object": obj,
            "valid_from": ts,
            "valid_to": None,
            "confidence": confidence,
        })
        print(f"[added] {subject} {predicate} {obj}  (valid_from={ts})")

    def query(self, subject: str, predicate: str, as_of: str = None):
        """
        Retrieve the fact valid at a given time (or now).
        Returns the most recent matching fact.
        """
        when = as_of or datetime.now().isoformat()
        matches = [
            f for f in self.facts
            if f["subject"] == subject
            and f["predicate"] == predicate
            and f["valid_from"] <= when
            and (f["valid_to"] is None or f["valid_to"] > when)
        ]
        if not matches:
            return None
        matches.sort(key=lambda f: f["valid_from"], reverse=True)
        return matches[0]

    def history(self, subject: str, predicate: str):
        """Return all facts (past + present) for a subject+predicate."""
        return sorted(
            [f for f in self.facts
             if f["subject"] == subject and f["predicate"] == predicate],
            key=lambda f: f["valid_from"],
        )

    def save(self, path: str = "memory.json"):
        """Save all facts to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.facts, f, indent=2)
        print(f"[memory] Saved {len(self.facts)} facts to {path}")

    def load(self, path: str = "memory.json"):
        """Load facts from a JSON file (if it exists)."""
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            self.facts = json.load(f)
        print(f"[memory] Loaded {len(self.facts)} facts from {path}")


# --- Quick test (same scenario that broke vector memory) ---
if __name__ == "__main__":
    mem = TemporalMemory()

    mem.add("Alice", "job_title", "Senior Software Engineer",
            timestamp="2024-01-15T00:00:00")

    mem.add("Alice", "job_title", "Staff Engineer",
            timestamp="2025-06-10T00:00:00")

    # Current query — should return the NEWEST fact
    result = mem.query("Alice", "job_title")
    print("\nCurrent answer: ", result["object"])

    # As-of query — should return the fact valid in early 2024
    past = mem.query("Alice", "job_title", as_of="2024-06-01T00:00:00")
    print("As of 2024-06:  ", past["object"])

    # Full history
    print("\nHistory:")
    for f in mem.history("Alice", "job_title"):
        print(f"  {f['valid_from'][:10]} → "
              f"{f['valid_to'][:10] if f['valid_to'] else 'present'} : "
              f"{f['object']}")

    # Test persistence
    print("\n--- Testing persistence ---")
    mem.save("test_memory.json")

    mem2 = TemporalMemory()
    mem2.load("test_memory.json")
    print(f"Loaded facts count: {len(mem2.facts)}")