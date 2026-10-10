"""
Demo: Historical query capability in temporal memory.
Seeds memory with facts at specific dates, then queries both current and past.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.temporal_memory import TemporalMemory


def main():
    memory = TemporalMemory()

    print("=" * 65)
    print("  Historical Query Demo — Temporal Memory")
    print("=" * 65)
    print()

    # Seed facts with explicit timestamps
    memory.add("alice", "job_title", "software engineer",
               timestamp="2024-01-15T00:00:00")
    memory.add("alice", "job_title", "senior engineer",
               timestamp="2025-01-01T00:00:00")
    memory.add("alice", "job_title", "staff engineer",
               timestamp="2026-01-01T00:00:00")

    print()

    # Query 1 — Current
    current = memory.query("alice", "job_title")
    print(f"Current job:          {current['object']}")

    # Query 2 — Historical (as of mid-2024)
    past_2024 = memory.query("alice", "job_title", as_of="2024-06-15T00:00:00")
    print(f"As of mid-2024:       {past_2024['object']}")

    # Query 3 — Historical (as of mid-2025)
    past_2025 = memory.query("alice", "job_title", as_of="2025-06-15T00:00:00")
    print(f"As of mid-2025:       {past_2025['object']}")

    # Query 4 — Before any fact existed
    past_2023 = memory.query("alice", "job_title", as_of="2023-01-01T00:00:00")
    if past_2023:
        print(f"As of 2023:           {past_2023['object']}")
    else:
        print(f"As of 2023:           (no information)")

    print()
    print("=" * 65)
    print("  Full history:")
    print("=" * 65)
    for f in memory.history("alice", "job_title"):
        start = f["valid_from"][:10]
        end = f["valid_to"][:10] if f["valid_to"] else "present"
        print(f"  {start} → {end} : {f['object']}")
    print()


if __name__ == "__main__":
    main()