# Concept Graph Samples

Demonstration concept graphs used in the four-layer architecture's Experiment 3 (Galaxy).

## Status

🚧 Under construction. Sample graphs (correlation coefficient, factoring/expansion) will be deposited here after extraction from the development repository.

## License

CC BY-NC-SA 4.0 — Educational / personal / research use is free with attribution and share-alike. **Commercial use requires a separate license**. Contact orange.wk@gmail.com.

## What is and isn't included

- ✅ Included: Demo units (correlation coefficient, factoring/expansion) — the units used in Galaxy v0/v1 experiments reported in the paper
- ❌ Not included: The full concept graph (60 units, 435 concepts) — maintained privately at `orangewk/MathDesk`

## Schema

Each graph is a JSON object with:

```json
{
  "domain": "correlation-coefficient",
  "nodes": [
    {"id": "...", "label": "...", "confidence": 1.0, ...}
  ],
  "edges": [
    {"from": "...", "to": "...", "confidence": 0.85, ...}
  ]
}
```

Confidence scores reflect multi-model union construction (5–10 LLM instances; see paper §3.6).
