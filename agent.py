"""
ChronoMind — Persistent Temporal Memory Agent
Interactive agent that learns facts from your sentences and answers questions.

Features:
  - Extract facts from natural language
  - Store facts in temporal memory (valid_from / valid_to)
  - Detect supersession (new facts override old ones)
  - Answer current queries ("what is alice's job?")
  - Answer historical queries ("what was alice's job in 2024?")
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.extractor import is_question, extract_fact, extract_query
from src.temporal_memory import TemporalMemory


def format_predicate(predicate: str) -> str:
    """Convert 'job_title' to 'job title' for display."""
    return predicate.replace("_", " ")


def main():
    memory = TemporalMemory()

    print("=" * 65)
    print("  ChronoMind — Persistent Temporal Memory Agent")
    print("  Type 'exit' to quit.")
    print("=" * 65)
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAgent: Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit", "bye"):
            print("Agent: Goodbye! I've saved everything to memory.")
            break

        # ---------- QUESTION ----------
        if is_question(user_input):
            q = extract_query(user_input)
            if not q or not q["subject"]:
                print("Agent: Sorry, I couldn't understand the question.")
                continue

            subject = q["subject"]
            predicate = q["predicate"]
            as_of_year = q.get("as_of_year")

            if not predicate:
                print(f"Agent: I'm not sure what you're asking about {subject}.")
                continue

            # ---- Historical query: "what was alice's job in 2024?" ----
            if as_of_year:
                as_of_ts = f"{as_of_year}-06-15T00:00:00"
                result = memory.query(subject, predicate, as_of=as_of_ts)
                if result:
                    print(f"Agent: In {as_of_year}, {subject} "
                          f"{format_predicate(predicate)} was {result['object']}.")
                else:
                    print(f"Agent: I don't have information about "
                          f"{subject}'s {format_predicate(predicate)} "
                          f"in {as_of_year}.")
                continue

            # ---- Current query: "what is alice's job?" ----
            result = memory.query(subject, predicate)
            if result:
                print(f"Agent: {subject} {format_predicate(predicate)} "
                      f"is {result['object']}. "
                      f"(valid since {result['valid_from'][:10]})")
            else:
                print(f"Agent: I don't have any information about "
                      f"{subject}'s {format_predicate(predicate)}.")
            continue

        # ---------- STATEMENT (fact to store) ----------
        fact = extract_fact(user_input)
        if not fact:
            print("Agent: I couldn't extract a fact from that. "
                  "Try something like 'Alice is an engineer'.")
            continue

        subject = fact["subject"]
        predicate = fact["predicate"]
        obj = fact["object"]

        # Check if this supersedes an existing fact
        previous = memory.query(subject, predicate)

        memory.add(subject, predicate, obj)
        fact["timestamp"] = datetime.now().isoformat()

        if previous and previous["object"] != obj:
            print(f"Agent: Updated. {subject} {format_predicate(predicate)} "
                  f"is now {obj} (previously {previous['object']}).")
        else:
            print(f"Agent: Got it. I'll remember {subject} "
                  f"{format_predicate(predicate)} is {obj}.")


if __name__ == "__main__":
    main()