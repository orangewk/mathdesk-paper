# Appendix D. Surveyor (`where_are_we`) — Technical Specification

*This appendix supplements §3.5 (Layer 4: The Concept Map as an External Tool) and §3.6 (Concept Graph Construction). It provides the full tool interface, algorithmic detail, and sub-agent configuration for `where_are_we`, the MCP tool at the core of the concept map layer.*

---

## D.1 Overview

`where_are_we` is an MCP (Model Context Protocol) tool that:

1. Accepts a natural-language observation from the tutor about the learner's current state
2. Delegates semantic interpretation to a **Surveyor sub-agent** (LLM call)
3. Applies a **deterministic graph algorithm** to the Surveyor's output
4. Returns a structured navigation report

The Surveyor is the only non-deterministic component. All graph calculations (frontier, obstacle, detour, fog) are deterministic given the Surveyor's float assessments and the concept graph.

---

## D.2 Tool Interface

### Input Schema

```json
{
  "observation": {
    "type": "string",
    "description": "Natural-language tutor observation about the learner's state. Example: 'The learner computed the mean fluently. They recognized the word deviation but could not perform the operation.'"
  }
}
```

### Output Schema

The tool returns a JSON object with the following structure:

```json
{
  "position": {
    "confident": [ { "id": "string", "label": "string", "value": "float" } ],
    "fuzzy":     [ { "id": "string", "label": "string", "value": "float" } ],
    "unknown":   [ { "id": "string", "label": "string", "value": "float" } ]
  },
  "terrain": {
    "frontier": [
      {
        "id": "string",
        "label": "string",
        "value": "float",
        "reason": "string (e.g., 'prerequisites [mean, deviation] are consolidated')"
      }
    ],
    "obstacles": [
      {
        "node": { "id": "string", "label": "string", "value": "float" },
        "nature": "string (e.g., 'acquisition value 0.55 — unstable')",
        "blocks": [ { "id": "string", "label": "string" } ]
      }
    ],
    "beyond": [
      {
        "id": "string",
        "label": "string",
        "blocked_by": [ { "id": "string", "label": "string", "value": "float" } ]
      }
    ]
  },
  "fog": "float (0.0–1.0)"
}
```

---

## D.3 Concept Node Representation

Each concept node in the knowledge graph carries an acquisition value:

| Value | Discrete label | Interpretation |
|-------|---------------|----------------|
| 0.0   | unknown       | Not mentioned; no evidence |
| ~0.3  | unknown       | Heard the term; cannot operate |
| ~0.6  | fuzzy         | Recently succeeded; consolidation uncertain |
| ~0.85 | confident     | Reliable; works after a delay |
| 1.0   | confident     | Fully consolidated; applies in novel contexts |

The `stateLabel` function maps floats to the three discrete categories:

```
confident : value ≥ 0.8
fuzzy     : 0.4 ≤ value < 0.8
unknown   : value < 0.4
```

---

## D.4 Surveyor Sub-Agent

The Surveyor is a dedicated LLM call that converts the tutor's natural-language observation into a list of per-node acquisition estimates.

### Surveyor Prompt (translated from Japanese)

```
You are a surveyor of a mathematical concept graph.
Based on observation information obtained from a conversation with a learner,
estimate the acquisition level of each concept node as a float value from 0.0 to 1.0.

## Scale
- 0.0: Unknown (not mentioned, does not know)
- 0.3: Heard of it (knows the word but cannot operate)
- 0.6: Recently succeeded (recently taught and succeeded, consolidation uncertain)
- 0.85: Can do it anytime (usable after a delay)
- 1.0: Fully consolidated (can apply freely)

## Concept Node List
[injected at call time from graph data]

## Observation Information
[injected at call time from tutor observation]

## Instructions
- Nodes with no direct evidence in the observation: set to 0.0
- "Could compute": 0.6–0.85; "has heard of it": 0.2–0.3
- Even if a prerequisite node is high, set to 0.0 if there is no
  evidence for the node itself

Respond only in the following JSON format (no explanation):
{
  "assessments": [
    {"id": "node_id", "value": 0.0, "evidence": "brief rationale"}
  ]
}
```

### Sub-Agent Configuration

| Parameter | Value |
|-----------|-------|
| Model | Claude CLI (default model) |
| Invocation | Subprocess call to Claude CLI with `-p` flag |
| Output format | `text` (JSON extracted from response) |
| Timeout | 120 seconds |
| Temperature | Model default (not explicitly set) |

The Surveyor is invoked via `runClaude(prompt)`, which spawns a child process. This design allows the Surveyor to run as a headless sub-agent without inheriting the parent MCP server's session.

---

## D.5 Knowledge State Record (Persistent Storage)

Between Surveyor calls, node acquisition values are persisted in a local JSON file. The implementation file name and tool identifiers retain the legacy term `karte` for the storage object; this is an implementation detail and the operational concept is the knowledge state defined in §3.3.

### Update Rule

On each `where_are_we` call, for each node with a positive assessment:

```
if observationCount == 0:
    value = observedValue           # first observation: adopt directly
else:
    value = value × 0.6 + observedValue × 0.4   # recency-weighted EMA
```

The weights (0.6 / 0.4) bias toward the accumulated estimate while allowing recent observations to shift it meaningfully.

### Time Decay

Nodes decay toward zero if not observed for more than 7 days:

```
if daysSince > 7:
    decay = min(0.3, daysSince × 0.005)
    value = max(0, value − decay)
```

Maximum decay is capped at 30% regardless of elapsed time.

---

## D.6 computeTerrain Algorithm

`computeTerrain` is called after every knowledge state record update. It is fully deterministic.

### Step 1: Classify nodes

For each node, apply `stateLabel(value)` → `{confident, fuzzy, unknown}`.

### Step 2: Compute frontier

```
frontier = []
for each node n where stateLabel(n) != "confident":
    prerequisites = inNeighbors(n)          // nodes that must precede n
    if prerequisites is empty: skip
    if all prerequisites are "confident":
        frontier.append(n)
```

Interpretation: frontier nodes are the next teachable concepts — all prerequisites are consolidated, but the concept itself is not yet confident.

### Step 3: Compute obstacles

```
obstacles = []
for each node f in frontier:
    if f.value >= 0.4:       // fuzzy, not unknown
        downstream = outNeighbors(f)
        obstacles.append({
            node: f,
            nature: "acquisition value {f.value} — unstable",
            blocks: downstream
        })
```

An obstacle is a frontier node that appears nominally acquired (fuzzy) but is unstable — it blocks downstream concepts from reaching frontier status.

### Step 4: Compute beyond

```
beyond = []
confidentIds = {n.id for n in position.confident}
frontierIds  = {n.id for n in frontier}
for each node n not in confidentIds and not in frontierIds:
    prerequisites = inNeighbors(n)
    if prerequisites is empty: skip
    blockers = [p for p in prerequisites if p not in confidentIds]
    if blockers is not empty:
        beyond.append({node: n, blocked_by: blockers})
```

Interpretation: beyond nodes are concepts the learner cannot yet reach because one or more prerequisites remain unconfident.

### Step 5: Compute fog

```
fog = 1 − (confidentCount + fuzzyCount × 0.3) / totalNodes
fog = clamp(fog, 0, 1)
```

Fog represents how much of the concept graph remains inaccessible. A fuzzy node contributes 0.3 of a confident node's weight, reflecting partial progress.

---

## D.7 Additional Tools

The MCP server exposes three additional tools alongside `where_are_we`:

| Tool | Purpose |
|------|---------|
| `run_diagnostic` | Generates one diagnostic question per turn for the next unconfident node (adaptive; skips confident nodes) |
| `update_node` | Directly sets a node's acquisition value; propagates 0.0 to unobserved downstream nodes when value < 0.4 |
| `get_karte` | Returns the current full knowledge state record with state labels and last-observed timestamps (the tool name `karte` is a legacy implementation identifier) |

---

## D.8 Anonymization Notes

The following elements were removed:

| Original element | Replacement |
|---|---|
| Repository file paths in `graphPath`, `kartePath` defaults | omitted |
| Repository URL | omitted |
| Internal project name in MCP server metadata | replaced with "galaxy-navigator" (the value already in the source) |

The tool name `where_are_we`, the Surveyor prompt logic, all threshold values, and the graph algorithm are reproduced verbatim or in direct translation.
