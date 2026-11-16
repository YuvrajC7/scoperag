# ScopeRAG

**Permission-aware retrieval with revocation and citation evidence.** Runnable engineering prototype with a local browser demo, FastAPI endpoints, automated tests, and reproducible synthetic evaluation.

## Run locally

Use Python 3.13. From the repository directory:

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python benchmark.py
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 for the interactive JSON demo or /docs for API schemas. The demo's Run button calls POST /demo. No API key is needed for the default path. Services are local demonstration applications without production authentication or rate limiting.

## Design and boundaries

Search quality is only useful when the retrieved evidence is authorized. ScopeRAG filters tenant membership and document ACLs before computing retrieval statistics, then combines lexical BM25-style scoring with character n-gram TF-IDF through reciprocal-rank fusion.

`server demo identity -> ACL-filtered corpus -> lexical/character/hybrid rank -> versioned evidence -> answer`

Document updates increment a policy epoch and clear cached retrievals. A process lock defines retrieval admission. Revocation cannot retract an answer already admitted, displayed, or sent to an external model. The browser demo shows a query, a cache hit, and the result after revoking the top document.

Default answers are extractive. Optional OpenAI-compatible generation reads SCOPERAG_LLM_URL, SCOPERAG_LLM_KEY, and SCOPERAG_LLM_MODEL from the environment; this integration was not benchmarked. Never commit credentials. Citation checks validate reference identity only, not semantic support. The model has no tools.

Public synthetic demo credentials are `Bearer demo-acme-reader` and `Bearer demo-beacon-reader`, used with POST /query. They are deliberately not production authentication. Bind to localhost. There is no dense embedding model, pgvector, or learned reranker. The synthetic identifier benchmark favors character matching: its 100% top-1 score versus 53.33% for lexical/hybrid is a finding about this fixture family, not general retrieval superiority.

## Evaluation

The checked-in [benchmark report](reports/benchmark.json) contains measured results, source hashes, environment metadata, and scope notes. Run `python benchmark.py` to regenerate it; timing varies by machine. The test suite contains **11 passing cases** in the recorded local run. CI reruns tests and benchmarks on Ubuntu.

All generated transactions, documents, labels, and API fixtures are synthetic. Generators are in core.py and experiment definitions in benchmark.py. The generator plus fixed seeds is the reproducible data source; no private user, employer, or customer data is included. Finite passing checks do not prove universal correctness.

## Source map

| File | Responsibility |
| --- | --- |
| core.py | Domain logic and seeded fixtures |
| app.py | Validated API requests and demo routes |
| ui.py | Lightweight browser interface |
| tests/ | Regression and domain checks |
| benchmark.py | Reproducible evaluation workload |
| reports/benchmark.json | Measured local evidence |

## Development

Created with AI coding assistance. Claims describe the code and bounded evaluations in this repository. MIT licensed; see LICENSE.
