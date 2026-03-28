# Hardware Design Pipeline

This document defines the procedure for designing a new 3D-printed part or mechanism from concept through validated STEP file. It is the orchestration guide for multi-agent work — every step has explicit inputs, outputs, and quality gates.

**This procedure exists because improvised orchestration produces unvalidated output.** Every step matters. Skipping validation, misweighting decisions, or treating intermediate artifacts as deliverables are the failure modes this document prevents.

---

## Foundational Documents

Two documents are the foundation of all design work. Every agent in every step reads both first.

1. **`hardware/requirements.md`** — what we are building, the components involved, and the hard constraints. Facts that no agent can discover on its own.

2. **`hardware/vision.md`** — the product values (what we care about, in priority order) and the product owner's imagined architecture (how they picture the assembled product). The values are absolute constraints. The architecture is directional — it tells you what the product owner is imagining, not what the final design must be.

If either document does not exist or has not been verified by the product owner, no design work may proceed.

---

## Prerequisites

Before starting the pipeline, verify:

1. **Requirements exist:** `hardware/requirements.md` must exist.
2. **Vision exists:** `hardware/vision.md` must exist.
3. **CadQuery venv works:** `tools/cad-venv/bin/python3 -c "import cadquery; print(cadquery.__version__)"`
4. **Validation tools exist:** `tools/svg_label_check.py`, `tools/svg_adjacency_check.py`, `tools/step_validate.py`

---

## Pipeline Steps

Each step has a detailed procedure document in `hardware/procedure/steps/`. The orchestrator reads the step's procedure doc before spawning the agent.

| Step | What it produces | Procedure doc | Agent count |
|------|-----------------|---------------|-------------|
| 0 | `hardware/manufacturing-environment.md` | `steps/0-manufacturing-environment.md` | 1 research agent |
| 1 | Folder tree | (none — do directly) | 0 |
| 2A | Technical research docs | `steps/2a-technical-research.md` | 1 per approach, parallel |
| 2B | Design pattern research | `steps/2b-design-pattern-research.md` | 1 |
| 3 | Decision document | `steps/3-design-decision.md` | 1 |
| 4a | Concept document | `steps/4a-conceptual-architecture.md` | 1 |
| 4b | parts.md per part | `steps/4b-parts-specification.md` | 1 per part, parallel |
| 5 | SVG engineering drawings | `steps/5-engineering-drawings.md` | 1 per part, parallel |
| 6 | STEP files | `steps/6-step-generation.md` | 1 per part, parallel |

### Step 0 — Manufacturing Environment (run once)

Produces `hardware/manufacturing-environment.md`. Runs once at project start, updated when hardware changes. All downstream steps read this for physical constraints.

**No agent may assume manufacturing constraints. They must come from this document.**

### Step 1 — Folder Structure

Create directly (no agent needed):
```
hardware/printed-parts/<mechanism-name>/
├── planning/
│   └── research/
└── drawings/
```

### Steps 2A, 2B — Research (parallel)

All research agents run in parallel. 2A agents investigate technical approaches. The 2B agent researches how real consumer products solve the same interaction.

**Critical: The 2B agent must NOT know about the current design.** Anchoring to an existing approach causes rationalization of the status quo.

### Step 3 — Decision

One agent reads ALL research (including design patterns) and makes a recommendation. Reads patterns first, then evaluates technical candidates against them.

### Step 4a — Conceptual Architecture

One agent explores the design space and settles on ONE concept. Does not apply the full rubric suite — that's 4b's job.

**Orchestrator checkpoint after 4a:** Review the concept before launching 4b. Redirecting here is cheap; redirecting after a full parts.md is expensive.

### Step 4b — Detailed Parts Specification

The most important step. Takes the settled concept and rigorously specifies every part with full rubric suite (grounding rule, mechanism narrative, constraint chains, direction checks, interface dimensions, assembly feasibility, part count).

### Step 5 — Engineering Drawings

One agent per part produces SVG engineering drawings. Must run SVG checking tools and achieve zero TEXT-TEXT collisions.

### Step 6 — STEP Generation

One agent per part produces CadQuery scripts AND validated STEP files. **The agent MUST run the script.** Zero validation FAILs required. Unrun scripts are not deliverables.

---

## Step Dependencies

```
Step 0 (manufacturing environment — run once, verified by orchestrator)
  │
  ▼
Step 1 (folders)
  │
  ├──→ Step 2A-1 (technical research) ──┐
  ├──→ Step 2A-2 (technical research) ──┤
  └──→ Step 2B   (design patterns)   ───┤
                                         │
                                         ▼
                     Step 3 (decision — reads ALL research)
                                         │
                     Step 4a (concept — explore, settle on one)
                                         │
                             [orchestrator/user review]
                                         │
                     Step 4b (parts.md — one per part, parallel)
                                         │
               ┌─────────────────────────┼──────────────────────┐
               ▼                         ▼                      ▼
         Step 5a (drawing)         Step 5b (drawing)           ...
               │                         │
               ▼                         ▼
         Step 6a (STEP)            Step 6b (STEP)              ...
```

- Step 0 runs once. All downstream steps read its output.
- Steps 2A and 2B run in parallel.
- Step 3 waits for ALL Step 2 agents.
- Step 4a waits for Step 3.
- **4a → 4b has an orchestrator checkpoint.**
- Steps 5 and 6 for the SAME part are sequential.
- Steps 5 and 6 for DIFFERENT parts can overlap.

---

## Common Mistakes This Procedure Prevents

1. **"Do not run the script"** — Never. The STEP file is the deliverable.
2. **Decision agent ignoring UX** — Product values are in every agent prompt. UX is always #1.
3. **Separate parts that should be one** — Rubric F catches this.
4. **Stale references to old mechanisms** — Quality gate requires checking.
5. **Agents not reading the standards** — Every agent prompt includes the path to its procedure doc.
6. **Skipping SVG tool checks** — Step 5 requires running tools and getting clean results.
7. **Missing the CadQuery venv** — Prerequisites verify it exists.
8. **Optimizing throughput over correctness** — Quality gates are mandatory. Fast + wrong < slow + right.
9. **Combining exploration and specification** — 4a explores, 4b specifies. Never combine them.
10. **Research agent anchoring to current design** — 2B must not know about the current design.
11. **Assumed manufacturing constraints** — Every constraint must come from `manufacturing-environment.md`, verified in Step 0. No "typical" values, ever.

---

## Agent Prompt Template

Every agent in this pipeline should receive a prompt structured as:

```
You are [role] for [part/mechanism name].

**FOUNDATIONAL DOCUMENTS (read these first):**
- hardware/requirements.md — what we are building, hard constraints
- hardware/vision.md — values and the product owner's imagined architecture
- hardware/manufacturing-environment.md — verified printer specs, material properties

**Context files to read:**
[list of file paths]

**Your task:**
[specific instructions]

**Quality requirements:**
[specific checks from the relevant quality gate]

**Save output to:**
[exact file path]
```

---

## Related Documents

- **Requirements:** `hardware/requirements.md`
- **Vision:** `hardware/vision.md`
- **Step procedures:** `hardware/procedure/steps/`
