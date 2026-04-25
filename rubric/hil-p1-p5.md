# Appendix E. HIL Rubric — Tutor Response Classification

*This appendix supplements §4.1 (Experiment 1: Control Layer Stability) and §4.2 (Experiment 2: Knowledge State Ablation). It provides the full operational definitions, decision procedure, and inter-rater validation details for the five-level quality rubric (P1–P5) and the three-category response classification (Experience / Confirmation / Explanation) used throughout the experimental program.*

---

## E.1 Two Classification Instruments

The experimental program used two distinct classification instruments:

1. **Five-Point HIL Quality Rubric (P1–P5)** — Applied once per experimental condition to assess overall tutor quality. Performed by the human investigator after reviewing a set of tutor responses.
2. **Three-Category Response Classifier (Experience / Confirmation / Explanation)** — Applied per individual response to the *first substantive tutor move*. Used as the primary outcome metric in Experiments 1 and 2.

The P1–P5 rubric motivated the research direction; the three-category classifier operationalized it for statistical analysis.

---

## E.2 Five-Point HIL Quality Rubric (P1–P5)

### Background

The rubric emerged from Human-in-the-Loop (HIL) review of C0 and C1 conditions in the baseline experiment. No rubric was pre-specified; evaluation criteria were discovered by inspecting actual tutor outputs and identifying what distinguished effective from ineffective responses.

### Rubric Definition

| Level | Label | Description |
|-------|-------|-------------|
| P1 | Explanation density | Responses vary in how densely they pack information. P1 asks whether the tutor distributes information step-by-step vs. all at once. |
| P2 | Lateral vs. vertical movement | When a learner fails to understand, does the tutor try a different representation at the same level (lateral), or descend to a more foundational concept (vertical)? |
| P3 | Prerequisite excavation | Does the tutor open implicit assumptions? When a learner asks "where does 2x come from?", does the tutor trace back to the learner's prior knowledge of simultaneous equations? |
| P4 | Response to repeated failure | After two or more consecutive comprehension failures, does the tutor change strategy (vertical movement) or continue with variations of the same explanation? |
| P5 | Recovery from limit | In the most demanding condition: the learner has said "I don't understand" multiple times. The rubric asks whether the tutor shifts to the *experience → discovery → naming* sequence using the learner's existing knowledge, rather than producing yet another explanation. |

### P5 as Diagnostic Criterion

P5 is the operationally decisive level. The HIL review of the C0/C1 baseline assigned a P5 rating — the lowest quality — because no tested model (Gemini Pro, Gemini Flash, Claude Sonnet, Claude Opus) recovered correctly from a sequence of five consecutive comprehension failures on the parity-filter problem.

The observed failure mode: all four models responded to "I still don't get why it's even" by generating a new or rephrased explanation. The correct response — identified through HIL analysis — was:

1. **Engage** the learner's known procedure: "Try solving x+y=8, x-y=5 the way you know."
2. **Experience**: Let the learner compute x=6.5 themselves.
3. **Contrast**: "Now try x+y=10, x-y=4."
4. **Discovery**: "What was different?" — learner discovers the odd/even distinction independently.
5. **Name**: "That's the parity filter."

No model executed step 1. All began at step 5. This finding motivated the three-layer architecture: the failure is architectural, not textual — adding more instructions to the prompt does not fix it.

### P5 Observation

> "All four models begin at naming (step 5). The learner's existing knowledge of solving simultaneous equations — the substrate for the experience — is never engaged. The control-layer design problem is that no model treats 'the learner knows how to add two equations' as a routing input."

This observation is the direct origin of the Knowledge State layer (§3.3) and the experience-first constraint in the Principle layer (§3.2).

---

## E.3 Three-Category Response Classifier

### Operational Definitions

**Experience**

The tutor requests a concrete operation, calculation, or experiment from the learner. The learner cannot proceed without taking an action.

*Required condition*: An explicit operation request is present in the response (calculate, draw, substitute, list, observe, etc.).

Examples:
- "Try substituting x=1 and computing P(1)."
- "Experiment with these three numbers."
- "Write out the three conditions from the problem."

**Confirmation**

The tutor probes the learner's existing knowledge, memory, prediction, or intuition. The learner answers with what they know or expect; no operation is required.

*Required condition*: The response asks for recall of prior knowledge, prediction, or direct intuition ("Do you remember...?", "What do you think will happen...?", "Does that sound familiar?").

Examples:
- "Do you remember what the factor theorem says?"
- "What do you think happens to covariance if we change the unit?"
- "Does this equation remind you of something?"

**Explanation**

The tutor states a concept, procedure, or structure. The learner receives information passively.

*Required condition*: The tutor is the subject of the main clause, presenting information ("This is...", "There is a rule that...", "The reason is...").

Examples:
- "There are three steps in a proof."
- "Correlation coefficient represents the relationship between two datasets."
- "2x is always even because..."

### Judgment Target

**The first substantive move** of the response — excluding greetings, empathy, and framing ("Let's look at this together," "That's a good question"). Classification is based on the first real action, not the response as a whole.

For compound responses (explanation followed by experience, or vice versa), the first substantive move determines the label.

### Decision Flowchart

```
Identify the first substantive move
         ↓
Q1: Does this move request a concrete operation from the learner?
    (calculation, diagram, substitution, listing, observation)
    Yes → EXPERIENCE
    No  ↓
Q2: Does this move ask for the learner's existing knowledge,
    memory, prediction, or intuition?
    Yes → CONFIRMATION
    No  ↓
Q3: Does this move present a concept, procedure, or structure
    with the tutor as subject?
    Yes → EXPLANATION
    No  → UNCLASSIFIABLE — re-identify substantive move
```

### Boundary Cases

| Response | Classification | Rationale |
|----------|---------------|-----------|
| "What do you think happens to the value if temperature goes up?" | Confirmation | Probes everyday intuition; no mathematical operation required |
| "Move the point on the interactive graph." | Experience | Explicit operation request |
| "Let's solve this together. The formula is..." | Explanation | Tutor presents formula — first substantive move is information delivery |
| "Let's solve this together. First, substitute x=1." | Experience | First substantive move is an operation request |
| "Do you remember covariance?" | Confirmation | Probing prior knowledge |
| "Using covariance, compute what happens when the unit changes." | Experience | Computation request |
| "What conditions from the problem text equal what?" | Experience | Extracting information from a visible problem — processing a present artifact, not recalling memory |
| "Factor Theorem says P(x)=0... so let's try x=1..." (tutor computes) | Explanation | Tutor executes the calculation; learner is passive |

### Notes on Edge Cases

- Greetings and empathy are not substantive moves. Classification begins after them.
- "What do you think?" without a specific operation is Confirmation.
- Tutor-enumerated values (e.g., "when x=1, 2x=2; when x=2, 2x=4...") are Explanation even if framed as demonstration.
- JSXGraph / interactive figures: if the learner is asked to *manipulate* them, it is Experience; if the tutor says "look at this figure," it is Explanation.

---

## E.4 Inter-Rater Agreement

### Study Design

To assess reliability, the three-category classifier was applied independently by a second rater (Claude Opus CLI sub-agent) to a 20-response sample drawn from the H1 stability run (40 responses, stratified across probes and conditions).

The sub-agent received the rubric text and the 20 response texts; it returned a classification and a stated rationale for each, in a single batch call.

### Results

| Metric | Value |
|--------|-------|
| Observed agreement (p_o) | 18/20 = 0.900 |
| Expected agreement (p_e) | 0.410 |
| Cohen's κ | **0.831** |
| Interpretation (Landis & Koch, 1977) | Almost perfect agreement |

### Confusion Matrix

| Reference \ Claude | Experience | Confirmation | Explanation |
|--------------------|-----------|-------------|-------------|
| **Experience**     | 10        | 0           | 1           |
| **Confirmation**   | 0         | 2           | 1           |
| **Explanation**    | 0         | 0           | 6           |

### Disagreement Analysis

Two responses were classified differently:

**Case 1 (P-stat/None/Run3):**
- Reference: Experience
- Second rater: Explanation
- Rationale for disagreement: The second rater identified "correlation coefficient represents the degree of relationship between two datasets" as the first substantive move. The reference rater considered the JSXGraph manipulation request that immediately followed as the move. The reference position holds that the opening statement was framing (transition into the interactive exercise), making the manipulation request the first substantive move.

**Case 2 (P-stat/None/Run1):**
- Reference: Confirmation
- Second rater: Explanation
- Rationale for disagreement: The first line was "What do you think happens to the value when two groups are compared?" followed immediately by "Correlation coefficient represents..." The second rater treated the definition as the first substantive move. The reference rater treated the prediction question as the first substantive move. Both interpretations are textually defensible; the disagreement reflects a genuine boundary between probing-before-explaining and defining-then-asking.

---

## E.5 Sample Size and Labeling Protocol

### H1 Ablation Study (Experiment 2)

| Parameter | Value |
|-----------|-------|
| Total responses classified | 475 |
| Model families | Gemini (400 responses), Claude (75 responses) |
| Conditions | 5 knowledge-state ablation conditions (K only, S only, L only, K+S+L, baseline) |
| Probes | P5, P6, P-stat, P-geom, P3 |
| Labeling method | Primary: automated (Claude CLI sub-agent with rubric); Spot-check: human review of edge cases |
| Re-classification event | Rubric revision (v1 → v2) required re-classification of 65 prior responses; 22 labels changed (34%) |

### Stability Evaluation (Experiment 1, Sub-experiments 11d–11e)

| Parameter | Value |
|-----------|-------|
| Total responses classified | 40 |
| Conditions | Full (principle + knowledge state + strategy few-shot) vs. None (knowledge state removed) |
| Probes | P6, P5, P-stat, P-geom (5 replicates × 4 probes × 2 conditions) |
| Temperature | 0 (deterministic sampling) |
| Shuffle control | Fisher-Yates randomization of few-shot component order |
| Inter-rater agreement | κ = 0.831 on 20-response sample (see §E.4) |

---

## E.6 TBD Items

- Formal P1–P4 operationalization as measurable criteria (current rubric provides qualitative descriptions only; P5 is the only level with a reproducible positive criterion)
- Exact sample breakdown for the 65-response re-classification event (which probes, which conditions)
- Third-rater validation of the two disagreement cases in §E.4
