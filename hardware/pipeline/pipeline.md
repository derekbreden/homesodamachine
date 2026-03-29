# Hardware Design Pipeline

This document defines the procedure for designing a new 3D-printed part or mechanism from concept through validated STEP file. It is the orchestration guide for multi-agent work — every step has explicit inputs, outputs, and quality gates.

**This procedure exists because improvised orchestration produces unvalidated output.** Every step matters. Skipping validation, misweighting decisions, or treating intermediate artifacts as deliverables are the failure modes this document prevents.

---

## Orchestrator Discipline: Inputs, Not Effort

The orchestrator's job is to provide each agent with the correct inputs, context, and quality gate. **The orchestrator does not judge how much effort an agent should apply.** Every agent receives the same quality expectations regardless of how "simple" the orchestrator believes the sub-component to be. The agent discovers the complexity by doing the work — the orchestrator cannot predict it.

Concretely:
- **Do:** Select the right input documents for each agent. Frame the task clearly. Point to the quality gate in the step's procedure doc.
- **Do not:** Tell an agent its task is "trivial," "straightforward," or "simple." Do not suggest an agent should produce a short document or skip checks. Do not modulate quality expectations based on perceived difficulty.

The quality gates are fixed by the step procedure documents. They are not parameters the orchestrator adjusts per sub-component.

---

## Scoping Rule: One Part at a Time

**The pipeline processes one printed part at a time.** A mechanism may contain multiple printed parts (e.g., the bag frame has a lower cradle and an upper cap). The pipeline runs steps 4a through 6 for ONE part before moving to the next. Do not run multiple parts through the pipeline simultaneously — the manager agent's context cannot hold the full state of multiple parts in flight.

The orchestration is:

1. Steps 1–3 (research and decision) apply to the mechanism as a whole.
2. Step 4a (concept) covers the full mechanism — all parts and how they fit together.
3. Steps 4d through 6c run for one part at a time:
   - Pick the most constrained or highest-risk part first.
   - Run it through 4d → 4s → 4b → 6g → 6c.
   - Commit the results.
   - Then start the next part, reading the previous part's docs as interface context.

This sequential approach means later parts can reference the exact dimensions of earlier parts at their interfaces. It also means the manager can focus its full context on one part's sub-components at a time, rather than tracking all parts' sub-components simultaneously.

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
4. **Validation tools exist:** `tools/step_validate.py`

---

## Pipeline Steps

Each step has a detailed procedure document in `hardware/pipeline/steps/`. The orchestrator reads the step's procedure doc before spawning the agent.

| Step | What it produces | Procedure doc | Scope |
|------|-----------------|---------------|-------|
| 1 | Folder tree | (none — do directly) | mechanism |
| 2A | Technical research docs | `steps/2a-technical-research.md` | mechanism |
| 2B | Design pattern research | `steps/2b-design-pattern-research.md` | mechanism |
| 3 | Synthesis document | `steps/3-design-decision.md` | mechanism |
| 4a | Concept document | `steps/4a-conceptual-architecture.md` | mechanism |
| 4d | Decomposition (or pass-through) | `steps/4d-decomposition.md` | per part |
| 4s | Spatial resolution document | `steps/4s-spatial-resolution.md` | per sub-component |
| 4b | parts.md | `steps/4b-parts-specification.md` | per sub-component |
| 6g | CadQuery scripts + STEP files | `steps/6-step-generation.md` | per sub-component |
| 6c | Composed STEP file | `steps/6c-composition.md` | per part (if decomposed) |

### Step 1 — Folder Structure

Create directly (no agent needed):
```
hardware/printed-parts/<mechanism-name>/
├── planning/
│   └── research/
```

### Steps 2A, 2B — Research (parallel)

All research agents run in parallel. The vision specifies the interaction; the research investigates how to execute it.

**2A agents** each answer one technical question the vision raises: forces, dimensions, materials, tolerances, failure modes. They do not explore alternative approaches — the approach is set by the vision.

**The 2B agent** studies how existing consumer products achieve the specific UX qualities the vision demands (squeeze feedback, hidden mechanisms, flush surfaces, seating confidence). It researches the details that make those qualities real, not alternative interaction types.

### Step 3 — Synthesis

One agent reads ALL research (technical and design pattern) and synthesizes them into a concrete execution plan for the vision. This step combines research findings into a coherent mechanism description — it does not choose between alternatives. If the research reveals a conflict with the vision, the agent flags the conflict and proposes the minimum modification, not a wholesale redesign.

### Step 4a — Conceptual Architecture

One agent explores the design space and settles on ONE concept. Covers the full mechanism — all parts and how they relate. Does not apply the full rubric suite — that's 4b's job.

### Step 4d — Sub-Component Decomposition (per part)

One agent per part reads the concept and decides: is this part a single geometric paradigm (2.5D), or does it combine multiple paradigms? If single paradigm, pass through. If multiple paradigms, decompose into sub-components that are each a 2.5D problem, plus a composition specification.

**This is the fan-out point.** After 4d, every subsequent step runs per-sub-component. The decomposition determines how many parallel tracks the pipeline will have for this part.

### Steps 4s, 4b, 6g — Per-Sub-Component Steps

**CRITICAL: Each sub-component is a separate agent.** If Step 4d decomposes a part into 3 sub-components, the orchestrator spawns 3 separate agents for Step 4s (one per sub-component), then 3 for Step 4b, then 3 for Step 6g. Do NOT spawn one agent and ask it to handle all sub-components — that defeats the entire purpose of decomposition. Each agent sees ONLY its own sub-component's documents and works on ONE 2.5D problem.

**Step 4s — Spatial Resolution:** One agent per sub-component resolves every multi-frame spatial relationship into concrete coordinates in the sub-component's own reference frame. Cross-sectional profiles that depend on physics (gravity, fluid fill, material drape at installation angle) are tabulated as coordinate data, not described in prose. Interface positions are pre-computed in the sub-component's local frame.

**Step 4b — Detailed Parts Specification:** The most important step. One agent per sub-component takes that sub-component's spatial resolution document and rigorously specifies it with full rubric suite. The spatial resolution document provides every derived dimension — the 4b agent should not need to perform trigonometry, coordinate transforms, or physics calculations. If it does, the spatial resolution step is incomplete.

**Step 6g — CadQuery Generation:** One agent per sub-component produces CadQuery scripts AND validated STEP files. **The agent MUST run the script.** Zero validation FAILs required. Unrun scripts are not deliverables. Each agent sees ONLY its sub-component's parts.md and produces ONE CadQuery script for ONE 2.5D solid.

### Step 6c — Composition (per decomposed part)

One agent per decomposed part combines the sub-component solids into a single validated STEP file using the transforms and operations from the decomposition spec (Step 4d). Skipped entirely for parts that were not decomposed.

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
                     Step 4a (concept — full mechanism)
                                         │
               ┌─────── PART 1 ──────────┼─── (PART 2 waits) ───┐
               │                                                  │
         Step 4d (decompose part 1)                               │
               │                                                  │
        ┌──────┴──────┐  (fan-out)                                │
        ▼             ▼                                           │
   4s → 4b → 6g      4s → 4b → 6g                           │
   (sub-comp A)       (sub-comp B)                                │
        │             │                                           │
        └──────┬──────┘                                           │
               ▼                                                  │
         Step 6c (compose part 1)                                 │
               │                                                  │
               ▼ commit                                           │
               └──────────────────────────┤                       │
                                          │                       │
                                    Step 4d (decompose part 2) ───┘
                                          │
                                         ...
```

- Steps 2A and 2B run in parallel.
- Step 3 waits for ALL Step 2 agents.
- Step 4a waits for Step 3.
- **Parts are processed sequentially** through steps 4d → 6c. One part completes and is committed before the next begins.
- Within a part, sub-component tracks (4s → 4b → 6g) can run in parallel after 4d.
- Step 6c waits for ALL 6g agents for that part.

---

## Common Mistakes This Procedure Prevents

1. **"Do not run the script"** — Never. The STEP file is the deliverable.
2. **Research exploring alternatives to the vision** — The vision specifies the interaction. Research investigates how to execute it, not whether to use a different approach.
3. **Separate parts that should be one** — Rubric F catches this.
4. **Stale references to old mechanisms** — Quality gate requires checking.
5. **Agents not reading the standards** — Every agent prompt includes the path to its procedure doc.
6. **Missing the CadQuery venv** — Prerequisites verify it exists.
7. **Optimizing throughput over correctness** — Quality gates are mandatory. Fast + wrong < slow + right.
8. **Combining exploration and specification** — 4a explores, 4b specifies. Never combine them.
9. **Synthesis agent replacing the vision** — If research reveals a feasibility conflict, the synthesis flags it and proposes the minimum modification. It does not silently substitute a different approach.
10. **Assumed manufacturing constraints** — All printer specs and materials are in `requirements.md`. No agent may assume "typical" values. If a constraint isn't in requirements.md, ask the product owner.
11. **CadQuery agent doing spatial reasoning** — All multi-frame geometry is resolved in Step 4s. By the time a CadQuery agent runs, every dimension is a concrete number in the sub-component's own frame.
12. **Single agent handling multi-paradigm geometry** — Step 4d decomposes complex parts so each CadQuery agent works on a 2.5D problem. If an agent needs both prismatic and rotational operations, the decomposition is wrong.
13. **Multiple parts in flight simultaneously** — The manager processes one part at a time through 4d → 6c. Running multiple parts in parallel overwhelms the manager's context and produces interface mismatches.
14. **One agent for all sub-components** — After decomposition, each sub-component is a SEPARATE agent. If 4d produces 3 sub-components, spawn 3 agents for 4s, 3 for 4b, 3 for 6g. A single agent handling all sub-components defeats the purpose of decomposition — it reintroduces the multi-paradigm complexity that decomposition was designed to eliminate.
15. **Orchestrator pre-judging complexity** — The orchestrator must never tell an agent its task is "trivial" or "straightforward," or suggest it should produce a short document. The agent discovers the complexity by doing the work. Quality gates are fixed, not adjustable per sub-component.

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
