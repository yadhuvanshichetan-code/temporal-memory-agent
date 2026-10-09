"""
Structured Memory — key-value store with explicit update semantics.
Keys are `subject.predicate`. Adding a new value overwrites the old one.
History is optionally preserved in a separate log.
"""

from datetime import datetime


class StructuredMemory:
    def __init__(self, keep_history: bool = True):
        self.store = {}              # key -> current value
        self.history = {}            # key -> list of (timestamp, value)
        self.keep_history = keep_history

    def _key(self, subject: str, predicate: str) -> str:
        return f"{subject}.{predicate}"

    def add(self, subject: str, predicate: str, obj: str,
            timestamp: str = None):
        """Insert or overwrite the value for a key."""
        ts = timestamp or datetime.now().isoformat()
        key = self._key(subject, predicate)

        if self.keep_history:
            self.history.setdefault(key, []).append((ts, obj))

        self.store[key] = obj
        print(f"[set] {key} = {obj}  (at {ts})")

    def query(self, subject: str, predicate: str):
        """Retrieve the current value. Overwrites mean only the newest survives."""
        key = self._key(subject, predicate)
        return self.store.get(key)

    def history_of(self, subject: str, predicate: str):
        """Full log of values for this key."""
        key = self._key(subject, predicate)
        return self.history.get(key, [])


# --- Quick test ---
if __name__ == "__main__":
    mem = StructuredMemory()

    mem.add("Alice", "job_title", "Senior Software Engineer",
            timestamp="2024-01-15T00:00:00")
    mem.add("Alice", "job_title", "Staff Engineer",
            timestamp="2025-06-10T00:00:00")

    # Current query — should return the NEWEST value (overwrite wins)
    print("\nCurrent answer:", mem.query("Alice", "job_title"))

    # As-of query — CANNOT be answered (no valid_to tracking)
    print("As of 2024-06:  (not supported — no timestamps in current store)")

    # History log — shows both entries
    print("\nHistory:")
    for ts, val in mem.history_of("Alice", "job_title"):
        print(f"  {ts[:10]} : {val}")