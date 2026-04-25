# Appendix A. Glossary of Terms

The terms below are used with the specific meanings given. Where a term is also used in the broader literature with different connotations, the paper-internal usage takes precedence.

| Term | Definition |
|---|---|
| **Four-layer control architecture** | The complete tutoring control system comprising four layers: Principle, Knowledge State, Strategy Few-Shot, and Concept Map. |
| **Principle layer** | Layer 1; encodes the pedagogical sequence (experience → discovery → naming) as a compact system-prompt constraint. |
| **Knowledge State layer** | Layer 2; represents the learner's acquired concept set as the tutor's primary routing input. |
| **Strategy few-shot** | Layer 3; a single compact pedagogical-pattern rule embedded in the system prompt that activates the target teaching behavior. |
| **Concept map layer** | Layer 4; the prerequisite graph for the target domain, provided as an external MCP tool rather than embedded in the system prompt. |
| **Concept graph** | A directed prerequisite graph over mathematical concepts; nodes are concepts, edges represent prerequisite relations. |
| **Core** | The subset of concept graph nodes and edges with confidence ≥ 0.7; used as the stable basis for frontier calculations. |
| **Fringe** | The subset of concept graph nodes and edges with confidence ≤ 0.4; reflects model-specific or context-dependent judgments. |
| **Multi-model union** | A graph construction method that aggregates independent prerequisite judgments from multiple LLM instances and scores each element by agreement rate. |
| **`where_are_we`** | The MCP tool that accepts a natural-language tutor observation and returns a structured navigation report (frontier, obstacles, detour, fog). |
| **Surveyor** | The sub-agent inside `where_are_we` that classifies each concept node as *confident*, *fuzzy*, or *unknown* from the tutor's natural-language observation. |
| **Frontier** | The set of concept graph nodes that are immediately reachable from the learner's current acquired node set; the candidates for the next teaching target. |
| **Obstacle** | A concept node nominally marked as acquired but classified as *fuzzy* by the Surveyor; a potential site of prerequisite instability blocking the frontier. |
| **Detour** | The path back to a *confident* ancestor node recommended when an obstacle is detected. |
| **Fog** | A scalar indicator (0–1) of uncertainty in the learner's current position on the concept graph; output by `where_are_we`. |
| **computeTerrain** | The deterministic graph computation function that derives frontier, obstacle, and detour from the node-level status estimate produced by the Surveyor. |
| **K (acquired knowledge)** | The component of the learner model representing the set of concepts the learner has confirmed understanding of; the sole knowledge state component confirmed as effective in the H1 ablation. |
| **S (struggle history)** | The component of the learner model representing past comprehension difficulties; found ineffective in the H1 ablation under all conditions tested. |
| **L (learning style)** | The component of the learner model representing the learner's preferred representational mode; found ineffective in the H1 ablation under all conditions tested. |
| **Probe** | A researcher-constructed learner utterance used as a stimulus in experiments (P3, P5, P6, P-stat, P-geom). |
| **C2** | The three-layer prompt configuration (Principle + Knowledge State + Strategy Few-Shot) established in Experiment 1; the basis for Layers 1–3 of the full architecture. |
| **Full condition** | The experimental condition in which all three prompt layers (Principle + Knowledge State + Strategy Few-Shot) are active. |
| **None condition** | The ablation condition in which the Knowledge State layer is removed, leaving only Principle and Strategy Few-Shot. |
| **Building-Blocks decomposition** | The recursive reduction of an unfamiliar concept into components already in the learner's acquired knowledge set; the operation the four-layer architecture is designed to execute. |
| **KST (Knowledge Space Theory)** | The formal framework (Doignon & Falmagne, 1999) in which a *knowledge state* is a subset of a concept domain closed under the prerequisite relation; used in §6 to interpret the architecture's control logic. |
