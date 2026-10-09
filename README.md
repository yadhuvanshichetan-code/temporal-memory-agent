# Temporal Memory Agent

**Research project:** Persistent temporal memory for AI agents.

AI assistants today forget across sessions and confuse old facts with new ones.
This project compares memory architectures on **supersession** —
the ability to know that "Alice got promoted to Staff Engineer"
replaces "Alice is a Senior Software Engineer."

## Headline Result

| Architecture | Supersession Accuracy |
|--------------|-----------------------|
| Vector Memory (RAG-style) | **10%** (1/10) |
| Temporal Memory (valid_from / valid_to) | **100%** (10/10) |

Vector memory returns whichever fact is semantically closest, even if it's stale.
Temporal memory tracks *when* each fact was true and correctly returns the newest one.

## Architectures

1. **Vector Memory** (`src/vector_memory.py`) — embeddings + cosine similarity
2. **Temporal Memory** (`src/temporal_memory.py`) — triples with validity intervals
3. **Structured Memory** — *planned*


## Project Structure

```                                    ← 3 backticks
src/
  vector_memory.py     RAG-style baseline
  temporal_memory.py   Temporal knowledge representation
eval/
  supersession_cases.json   10 test cases
  run_benchmark.py          Comparison harness
docs/                       (documentation to come)
```           