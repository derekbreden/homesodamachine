# Hardware Design Pipeline

This document defines the procedure for designing a new 3D-printed part or mechanism from concept through validated STEP file. It is the orchestration guide for multi-agent work — every step has explicit inputs, outputs, and quality gates.

**This procedure exists because improvised orchestration produces unvalidated output.** Every step matters. Skipping validation, misweighting decisions, or treating intermediate artifacts as deliverables are the failure modes this document prevents.

---

## Foundational Documents

Two documents are the foundation of all design work. Every agent in every step reads both first.

1. **`hardware/requirements.md`** — what we are building, the components involved, and the hard constraints (including printer specs, materials, and build volume). Facts that no agent can discover on its own.

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

Each step has a detailed procedure document in `hardware/pipeline/steps/`. The orchestrator reads the step's procedure doc before spawning the agent.

| Step | What it produces | Procedure doc | Agent count |
|------|-----------------|---------------|-------------|
| 1 | Folder tree | (none — do directly) | 0 |
| 2A | Technical research docs | `steps/2a-technical-research.md` | 1 per approach, parallel |
| 2B | Design pattern research | `steps/2b-design-pattern-research.md` | 1 |
| 3 | Decision document | `steps/3-design-decision.md` | 1 |
| 4a | Concept document | `steps/4a-conceptual-architecture.md` | 1 |
| 4s | Spatial resolution document | `steps/4s-spatial-resolution.md` | 1 |
| 4b | parts.md per part | `steps/4b-parts-specification.md` | 1 per part, parallel |
| 5 | SVG engineering drawings | `steps/5-engineering-drawings.md` | 1 per part, parallel |
| 6d | Decomposition spec (or pass-through) | `steps/6d-decomposition.md` | 1 per part |
| 6g | CadQuery scripts + STEP files | `steps/6-step-generation.md` | 1 per sub-component, parallel |
| 6c | Composed STEP file | `steps/6c-composition.md` | 1 per decomposed part |

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

### Step 4s — Spatial Resolution (NEW)

One agent takes the settled concept and resolves every multi-frame spatial relationship into concrete coordinates in each part's own reference frame. Cross-sectional profiles that depend on physics (gravity, fluid fill, material drape at installation angle) are tabulated as coordinate data, not described in prose. Interface positions between parts are pre-computed in each part's local frame.

**For simple mechanisms with no angled mounting, no physics-dependent profiles, and no multi-frame interfaces**, this step produces a trivial document ("single frame, no transforms needed") and imposes no overhead.

### Step 4b — Detailed Parts Specification

The most important step. Takes the settled concept AND the spatial resolution document and rigorously specifies every part with full rubric suite (grounding rule, mechanism narrative, constraint chains, direction checks, interface dimensions, assembly feasibility, part count).

The spatial resolution document provides every derived dimension — the 4b agent should not need to perform trigonometry, coordinate transforms, or physics calculations. If it does, the spatial resolution step is incomplete.

### Step 5 — Engineering Drawings

One agent per part produces SVG engineering drawings. Must run SVG checking tools and achieve zero TEXT-TEXT collisions.

### Step 6d — Sub-Component Decomposition

One agent per part reads the parts.md and decides: is this part a single geometric paradigm (2.5D extrude-and-cut, or revolved profiles), or does it combine multiple paradigms? If single paradigm, the agent passes through to a single 6g agent. If multiple paradigms, the agent decomposes into sub-components that are each a 2.5D problem, plus a composition specification.

### Step 6g — CadQuery Generation

One agent per sub-component (or per part, if no decomposition) produces CadQuery scripts AND validated STEP files. **The agent MUST run the script.** Zero validation FAILs required. Unrun scripts are not deliverables. This is the existing step 6 procedure — unchanged.

### Step 6c — Composition

One agent per decomposed part combines the sub-component solids into a single validated STEP file using the transforms and operations from the decomposition spec. Skipped entirely for parts that were not decomposed.

---

## Step Dependencies

```
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
                     Step 4s (spatial resolution — resolve all multi-frame geometry)
                                         │
                     Step 4b (parts.md — one per part, parallel)
                                         │
               ┌─────────────────────────┼──────────────────────┐
               ▼                         ▼                      ▼
         Step 5a (drawing)         Step 5b (drawing)           ...
               │                         │
               ▼                         ▼
         Step 6d-a (decompose)     Step 6d-b (decompose)       ...
               │                         │
        ┌──────┴──────┐                  │ (pass-through)
        ▼             ▼                  ▼
   Step 6g-a1    Step 6g-a2        Step 6g-b
   (sub-comp)    (sub-comp)        (full part)
        │             │                  │
        └──────┬──────┘                  │
               ▼                         │
         Step 6c-a (compose)             │ (no composition needed)
               │                         │
               ▼                         ▼
          STEP file a               STEP file b               ...
```

- Steps 2A and 2B run in parallel.
- Step 3 waits for ALL Step 2 agents.
- Step 4a waits for Step 3.
- Step 4s waits for Step 4a.
- Step 4b waits for Step 4s.
- Steps 5 and 6d for the SAME part are sequential.
- Steps 5 and 6d for DIFFERENT parts can overlap.
- Step 6g sub-component agents for the SAME part run in parallel.
- Step 6c waits for ALL 6g agents for that part.
- The 6d → 6g → 6c chain for DIFFERENT parts can overlap.

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
11. **Assumed manufacturing constraints** — All printer specs and materials are in `requirements.md`. No agent may assume "typical" values. If a constraint isn't in requirements.md, ask the product owner.
12. **CadQuery agent doing spatial reasoning** — All multi-frame geometry is resolved in Step 4s. By the time a CadQuery agent runs, every dimension is a concrete number in the part's own frame.
13. **Single agent handling multi-paradigm geometry** — Step 6d decomposes complex parts so each CadQuery agent works on a 2.5D problem. If an agent needs both prismatic and rotational operations, the decomposition is wrong.

---

## Agent Prompt Template

Every agent in this pipeline should receive a prompt structured as:

```
You are [role] for [part/mechanism name].

**FOUNDATIONAL DOCUMENTS (read these first):**
- hardware/requirements.md — what we are building, hard constraints, printer specs
- hardware/vision.md — values and the product owner's imagined architecture

**Web research:** Use WebFetch first. If it returns 403 or empty/useless content,
fall back to Chrome MCP tools (mcp__Claude_in_Chrome__navigate,
mcp__Claude_in_Chrome__read_page). Never give up on a URL just because
WebFetch failed — many manufacturer sites block non-browser requests but
work fine in Chrome.

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
- **Step procedures:** `hardware/pipeline/steps/`
