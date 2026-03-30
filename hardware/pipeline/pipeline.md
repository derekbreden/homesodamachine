# Hardware Design Pipeline

**Parts are designed iteratively. The first version of any part is the simplest shape that occupies the correct space. Retention, joinery, and interfaces with parts that don't exist yet are added in later rounds — not anticipated in the first.**

This document defines the procedure for designing a new 3D-printed part or mechanism from concept through validated STEP file. It is the orchestration guide for multi-agent work — every step has explicit inputs, outputs, and quality gates.

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

1. Steps 1–3 (setup and synthesis) apply to the mechanism as a whole.
2. Step 4a (concept) covers the full mechanism — all parts and how they fit together.
3. Steps 4d through 6c run for one part at a time:
   - Pick the most constrained or highest-risk part first.
   - Run it through 4d → 4s → 4b → 6g → 6c.
   - Commit the results.
   - Then start the next part, reading the previous part's docs as interface context.

This sequential approach means later parts can reference the exact dimensions of earlier parts at their interfaces. It also means the manager can focus its full context on one part's sub-components at a time, rather than tracking all parts' sub-components simultaneously.

---

## Explicit Scoping

**The orchestrator must explicitly state what is in scope and what is out of scope for each run.** The vision describes the whole product. A single pipeline run does not produce the whole product. The synthesis prompt must say exactly which parts are being designed and, critically, what is NOT being designed in this run.

Example: "This run: six flat panels and their rail joints. Out of scope: retention mechanisms, strut routing, squeeze mechanism internals. These will be designed in future runs."

Agents will see unresolved interfaces — a hole that will later receive a strut, a rail that doesn't yet have a retention detent. This is expected. **Incomplete geometry is a valid deliverable.** A part that occupies the correct space with the correct outer dimensions and the features that are in scope is a finished deliverable for that run, even if it will gain features in future runs. Agents must not block on, design for, or add geometry to accommodate future work that is explicitly out of scope.

---

## Foundational Documents

Two documents are the foundation of all design work. Every agent in every step reads both first.

1. **`hardware/requirements.md`** — what we are building, the components involved, and the hard constraints (including printer specs, materials, and build volume). Facts that no agent can discover on its own.

2. **`hardware/vision.md`** — the product values (what we care about, in priority order) and the product owner's imagined architecture (how they picture the assembled product). The values are absolute constraints. The architecture is directional — it tells you what the product owner is imagining, not what the final design must be.

---

## Pipeline Steps

Each step has a detailed procedure document in `hardware/pipeline/steps/`. The orchestrator reads the step's procedure doc before spawning the agent.

| Step | What it produces | Procedure doc | Scope |
|------|-----------------|---------------|-------|
| 1 | Folder tree | (none — do directly) | mechanism |
| 2A | Technical research docs (optional) | `steps/2a-technical-research.md` | mechanism |
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

### Step 2A — Technical Research (optional)

Most mechanisms can be designed from the vision, requirements, and component datasheets already in the repo. Step 2A is invoked only when the orchestrator identifies a genuine open technical question that no agent can answer from existing information — typically physics that must be investigated (e.g., how a flexible bag behaves under gravity at a specific angle) or off-the-shelf component dimensions that aren't in the repo yet.

When invoked, each 2A agent answers one specific technical question. They do not explore alternative approaches — the approach is set by the vision. See `steps/2a-technical-research.md` for the full procedure.

**When NOT to invoke Step 2A:** If the mechanism's geometry can be fully determined from the vision, requirements.md, and component datasheets in the repo, skip directly to Step 3. Do not commission research to find features to add — the default is minimum viable geometry.

### Step 3 — Synthesis

One agent reads the vision, requirements, component datasheets, and any technical research (if Step 2A was invoked) and synthesizes them into a concrete execution plan for the vision. This step produces a coherent mechanism description — it does not choose between alternatives and does not add features beyond what the vision requires. If the research reveals a conflict with the vision, the agent flags the conflict and proposes the minimum modification, not a wholesale redesign.

### Step 4a — Conceptual Architecture

One agent takes the synthesis's execution plan and works out the concrete architecture: piece count, split strategy, join methods, seam placement, surfaces, and manufacturing approach. Covers the full mechanism — all parts and how they relate. Does not reconsider the interaction design (that's settled by the vision and synthesis) and does not apply the full rubric suite (that's 4b's job).

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
  ├──→ Step 2A (technical research, optional, parallel agents) ──┐
  │    (skip if no open technical questions)                      │
  │                                                               │
  └──→ Step 3 (synthesis — reads vision + requirements + any 2A research)
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

- If Step 2A is invoked, Step 3 waits for all 2A agents. Otherwise Step 3 starts immediately after Step 1.
- Step 4a waits for Step 3.
- **Parts are processed sequentially** through steps 4d → 6c. One part completes and is committed before the next begins.
- Within a part, sub-component tracks (4s → 4b → 6g) can run in parallel after 4d.
- Step 6c waits for ALL 6g agents for that part.

---

## Common Mistakes This Procedure Prevents

1. **"Do not run the script"** — Never. The STEP file is the deliverable.
2. **Research adding scope** — If Step 2A is invoked, it answers specific technical questions. It does not harvest features from other products or propose additions to the design. The default is minimum viable geometry.
3. **Separate parts that should be one** — Rubric F catches this.
4. **Stale references to old mechanisms** — Quality gate requires checking.
5. **Agents not reading the standards** — Every agent prompt includes the path to its procedure doc.
6. **Missing the CadQuery venv** — Prerequisites verify it exists.
7. **Optimizing throughput over correctness** — Quality gates are mandatory. Fast + wrong < slow + right.
8. **Combining architecture and specification** — 4a works out the architecture, 4b specifies the parts. Never combine them.
9. **Synthesis agent replacing the vision** — If research reveals a feasibility conflict, the synthesis flags it and proposes the minimum modification. It does not silently substitute a different approach.
10. **Assumed manufacturing constraints** — All printer specs and materials are in `requirements.md`. No agent may assume "typical" values. If a constraint isn't in requirements.md, ask the product owner.
11. **CadQuery agent doing spatial reasoning** — All multi-frame geometry is resolved in Step 4s. By the time a CadQuery agent runs, every dimension is a concrete number in the sub-component's own frame.
12. **Single agent handling multi-paradigm geometry** — Step 4d decomposes complex parts so each CadQuery agent works on a 2.5D problem. If an agent needs both prismatic and rotational operations, the decomposition is wrong.
13. **Multiple parts in flight simultaneously** — The manager processes one part at a time through 4d → 6c. Running multiple parts in parallel overwhelms the manager's context and produces interface mismatches.
14. **One agent for all sub-components** — After decomposition, each sub-component is a SEPARATE agent. If 4d produces 3 sub-components, spawn 3 agents for 4s, 3 for 4b, 3 for 6g. A single agent handling all sub-components defeats the purpose of decomposition — it reintroduces the multi-paradigm complexity that decomposition was designed to eliminate.
15. **Orchestrator pre-judging complexity** — The orchestrator must never tell an agent its task is "trivial" or "straightforward," or suggest it should produce a short document. The agent discovers the complexity by doing the work. Quality gates are fixed, not adjustable per sub-component.
16. **Features serving imagined stakeholders** — Every feature must trace to the vision or a physical necessity (structural, manufacturing, assembly, routing). "Good engineering practice," "developer convenience," "future flexibility," and "robustness to scenarios the vision doesn't contemplate" are not justifications. Rubric H catches this.
17. **Designing for out-of-scope future work** — If the orchestrator's scoping says retention mechanisms are out of scope, do not add detent geometry, snap-fit hooks, or screw bosses "so they're ready." A flat panel without retention is the correct deliverable. Future runs will add features to existing parts. Do not anticipate them.

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
