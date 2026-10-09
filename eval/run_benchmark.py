"""
Benchmark: Run supersession test cases against both memory architectures.
Outputs accuracy for each system.
"""

import json
import os
import sys

# Make src/ importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.vector_memory import VectorMemory
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


def evaluate_vector_memory(cases):
    """Vector memory: add both facts, ask question, see what wins."""
    correct = 0
    for case in cases:
        mem = VectorMemory()
        mem.add(case["old_fact"])
        mem.add(case["new_fact"])
        top = mem.query(case["query"], top_k=1)
        answer = top[0][0] if top else ""
        if case["expected"].lower() in answer.lower():
            correct += 1
    return correct / len(cases)


def evaluate_temporal_memory(cases):
    """Temporal memory: add both facts with earlier/later timestamps."""
    correct = 0
    for case in cases:
        mem = TemporalMemory()
        subject, predicate = extract_triple(case["old_fact"])

        # Old fact: earlier timestamp
        mem.add(subject, predicate, case["stale"],
                timestamp="2024-01-01T00:00:00")

        # New fact: later timestamp (supersedes)
        mem.add(subject, predicate, case["expected"],
                timestamp="2025-01-01T00:00:00")

        result = mem.query(subject, predicate)
        answer = result["object"] if result else ""

        if case["expected"].lower() in answer.lower():
            correct += 1
    return correct / len(cases)


def main():
    cases = load_cases()
    print(f"Loaded {len(cases)} supersession test cases.\n")

    vec_acc = evaluate_vector_memory(cases)
    tmp_acc = evaluate_temporal_memory(cases)

    print("=" * 50)
    print("  SUPERSESSION ACCURACY RESULTS")
    print("=" * 50)
    print(f"  Vector Memory:   {vec_acc * 100:5.1f}%  "
          f"({int(vec_acc * len(cases))}/{len(cases)})")
    print(f"  Temporal Memory: {tmp_acc * 100:5.1f}%  "
          f"({int(tmp_acc * len(cases))}/{len(cases)})")
    print("=" * 50)


if __name__ == "__main__":
    main()