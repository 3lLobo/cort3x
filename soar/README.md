[Ingest Case]
      ↓
[Initial Context Builder]
      ↓
[Tool Loop (LLM decides → tools execute)]
      ↓
[Confidence Check]
      ↓
 ┌───────────────┬────────────────────┐
 │ High confidence│ Low confidence     │
 │ → skip agents  │ → trigger AutoGen  │
 └───────────────┴────────────────────┘
      ↓
[Final Summary + Classification]