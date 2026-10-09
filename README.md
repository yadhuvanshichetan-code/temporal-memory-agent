# Temporal Memory Agent

**Research project:** Persistent temporal memory for AI agents.

AI assistants today forget across sessions and confuse old facts with new ones.
This project compares three memory architectures on **supersession** —
the ability to know that "Alice got promoted to Staff Engineer"
replaces "Alice is a Senior Software Engineer" — and on **historical queries** —
the ability to answer "What was Alice's job in June 2024?"

## Headline Result

| Architecture | Current Query | Historical Query |
|--------------|---------------|------------------|
| Vector Memory (RAG-style) | **10%** (1/10) | **0%** (0/10) |
| Structured Memory (key-value) | **100%** (10/10) | **0%** (0/10) |
| **Temporal Memory** (valid_from / valid_to) | **100%** (10/10) | **100%** (10/10) |

**Each architecture fails in a distinct way:**
- **Vector memory** returns the semantically closest fact, even if it is stale.
- **Structured memory** overwrites old values, so it answers current queries
  correctly but loses all historical information.
- **Temporal memory** tracks *when* each fact was true, so it answers both
  current and historical queries correctly.

## Architectures

1. **Vector Memory** (`src/vector_memory.py`) — embeddings + cosine similarity
2. **Structured Memory** (`src/structured_memory.py`) — key-value store with overwrite semantics
3. **Temporal Memory** (`src/temporal_memory.py`) — triples with `valid_from` / `valid_to`

## Project Structure
```
src/
  vector_memory.py      RAG-style baseline
  structured_memory.py  Key-value store
  temporal_memory.py    Temporal knowledge representation
eval/
  supersession_cases.json   10 test cases
  run_benchmark.py          Three-way comparison harness
docs/                       (paper draft coming)
```
## How to Run

Install dependencies:

    pip install sentence-transformers numpy pandas python-dotenv

Run each architecture demo:

    python src/vector_memory.py
    python src/structured_memory.py
    python src/temporal_memory.py

Run the full benchmark:

    python eval/run_benchmark.py

## Example Output
```
=================================================================
  MEMORY ARCHITECTURE BENCHMARK
=================================================================
  Architecture             Current   Historical
-----------------------------------------------------------------
  Vector Memory        10.0% (1/10)  0.0% (0/10)
  Structured Memory   100.0% (10/10) 0.0% (0/10)
  Temporal Memory     100.0% (10/10) 100.0% (10/10)
=================================================================
```


## Status

- [x] Vector memory baseline
- [x] Structured memory
- [x] Temporal memory
- [x] Three-way evaluation harness
- [x] Historical-query metric
- [ ] Scale to 50+ test cases
- [ ] LLM-based fact extraction
- [ ] Confidence scoring and forgetting
- [ ] Paper draft

## License

MIT

