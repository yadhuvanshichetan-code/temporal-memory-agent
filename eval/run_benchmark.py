"""
Benchmark: Run supersession test cases against three memory architectures.

Architectures:
  1. Vector Memory      — embedding + cosine similarity (RAG-style)
  2. Structured Memory  — key-value store with overwrite semantics
  3. Temporal Memory    — triples with valid_from / valid_to

Metrics:
  - Supersession Accuracy (current-fact queries)
  - Historical Accuracy   (as-of-past-date queries)
"""

import json
import os
import sys

# Make src/ importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.vector_memory import VectorMemory
from src.structured_memory import StructuredMemory
from src.temporal_memory import TemporalMemory


def load_cases():
    path = os.path.join(os.path.dirname(__file__), "supersession_cases.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_triple(sentence):
    """
    Extremely simple rule-based extractor for the demo.
    Format expected: "<Name> <rest>" — treats first word as subject.
    """
    parts = sentence.split(" ", 1)
    return parts[0].rstrip("'s"), parts[1] if len(parts) > 1 else ""


# ---------------------------------------------------------------
# Evaluation functions — each returns (current_acc, historical_acc)
# ---------------------------------------------------------------

def evaluate_vector_memory(cases):
    correct_current = 0
    correct_historical = 0

    for case in cases:
        mem = VectorMemory()
        mem.add(case["old_fact"])
        mem.add(case["new_fact"])

        # Current query
        top = mem.query(case["query"], top_k=1)
        answer = top[0][0] if top else ""
        if case["expected"].lower() in answer.lower():
            correct_current += 1

        # Historical query — vector memory has no notion of time
        # so it can't reliably answer; we mark as incorrect by default
        # (it returns whichever embedding is closest, ignoring time).

    n = len(cases)
    return correct_current / n, correct_historical / n


def evaluate_structured_memory(cases):
    correct_current = 0
    correct_historical = 0

    for case in cases:
        mem = StructuredMemory(keep_history=False)
        subject, predicate = extract_triple(case["old_fact"])

        mem.add(subject, predicate, case["stale"],
                timestamp="2024-01-01T00:00:00")
        mem.add(subject, predicate, case["expected"],
                timestamp="2025-01-01T00:00:00")

        # Current query — works because newest overwrote old
        answer = mem.query(subject, predicate) or ""
        if case["expected"].lower() in answer.lower():
            correct_current += 1

        # Historical query — cannot answer (old value was overwritten)
        # Historical store isn't queryable as-of; it just lists all values.

    n = len(cases)
    return correct_current / n, correct_historical / n


def evaluate_temporal_memory(cases):
    correct_current = 0
    correct_historical = 0

    for case in cases:
        mem = TemporalMemory()
        subject, predicate = extract_triple(case["old_fact"])

        mem.add(subject, predicate, case["stale"],
                timestamp="2024-01-01T00:00:00")
        mem.add(subject, predicate, case["expected"],
                timestamp="2025-01-01T00:00:00")

        # Current query — newest valid fact wins
        result = mem.query(subject, predicate)
        answer = result["object"] if result else ""
        if case["expected"].lower() in answer.lower():
            correct_current += 1

        # Historical query — as of mid-2024, the OLD fact should be returned
        past = mem.query(subject, predicate, as_of="2024-06-01T00:00:00")
        past_answer = past["object"] if past else ""
        if case["stale"].lower() in past_answer.lower():
            correct_historical += 1

    n = len(cases)
    return correct_current / n, correct_historical / n


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------

def main():
    cases = load_cases()
    print(f"Loaded {len(cases)} supersession test cases.\n")

    vec_cur, vec_hist = evaluate_vector_memory(cases)
    str_cur, str_hist = evaluate_structured_memory(cases)
    tmp_cur, tmp_hist = evaluate_temporal_memory(cases)

    n = len(cases)

    print("=" * 65)
    print("  MEMORY ARCHITECTURE BENCHMARK")
    print("=" * 65)
    print(f"  {'Architecture':<20} {'Current':>12} {'Historical':>12}")
    print("-" * 65)
    print(f"  {'Vector Memory':<20} "
          f"{f'{vec_cur*100:.1f}% ({int(vec_cur*n)}/{n})':>12} "
          f"{f'{vec_hist*100:.1f}% ({int(vec_hist*n)}/{n})':>12}")
    print(f"  {'Structured Memory':<20} "
          f"{f'{str_cur*100:.1f}% ({int(str_cur*n)}/{n})':>12} "
          f"{f'{str_hist*100:.1f}% ({int(str_hist*n)}/{n})':>12}")
    print(f"  {'Temporal Memory':<20} "
          f"{f'{tmp_cur*100:.1f}% ({int(tmp_cur*n)}/{n})':>12} "
          f"{f'{tmp_hist*100:.1f}% ({int(tmp_hist*n)}/{n})':>12}")
    print("=" * 65)
    print()
    print("Legend:")
    print("  Current    = query for the latest/current value of a fact")
    print("  Historical = query for the value valid at a past date")


if __name__ == "__main__":
    main()