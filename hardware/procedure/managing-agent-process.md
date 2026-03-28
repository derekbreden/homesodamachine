# Hardware Design Pipeline

This document defines the procedure for designing a new 3D-printed part or mechanism from concept through validated STEP file. It is the orchestration guide for multi-agent work — every step has explicit inputs, outputs, agent instructions, and quality gates.

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

1. **Requirements exist:**
   `hardware/requirements.md` must exist. This document contains the hard requirements that are not flexible.

2. **Vision exists:**
   `hardware/vision.md` must exist. This document contains the soft vision that should expand you and your agent spawns' horizons.

3. **CadQuery venv exists and works:**
   ```
   tools/cad-venv/bin/python3 -c "import cadquery; print(cadquery.__version__)"
   ```
   If this fails, fix it before proceeding. Do not work around a broken environment.

4. **SVG checking tools exist:**
   ```
   ls tools/svg_label_check.py tools/svg_adjacency_check.py tools/step_validate.py
   ```

5. **Standards documents exist:**
   - `hardware/procedure/engineering-drawings-SVG.md`
   - `hardware/procedure/3d-models-STEP.md`
   - This document (`hardware/procedure/managing-agent-process.md`)

---

## Pipeline Steps

### Step 0 — Manufacturing Environment (run once, update when hardware changes)

**This step exists because assumed constraints propagate unchallenged through every downstream step.** A "typical 256mm print bed" assumption shaped an entire enclosure split strategy, tongue-and-groove joint engineering, and multi-piece architecture — and the actual printer had a 325×320mm bed. No downstream step questions constraints it receives. The only defense is verifying constraints at the source, before any design work begins.

**Input:** User-provided information about available manufacturing tools, materials, and hardware inventory
**Output:** `hardware/manufacturing-environment.md` — the single source of truth for all physical manufacturing constraints
**Agent:** One research agent that looks up and verifies specifications

This step runs once at the start of the project and is updated whenever the manufacturing environment changes (new printer, new materials, etc.). It does NOT run at the start of every part design — it produces a shared document that all parts reference.

**What the orchestrator must provide to the agent:**
- Printer make and model (e.g., "Bambu Lab H2C")
- Materials on hand or planned (e.g., "PETG, PETG-CF")
- Any non-obvious hardware inventory (magnets, fasteners, springs, etc.)

**What the agent must research and document:**
1. **Printer specifications** — look up the manufacturer's published specs for the exact model provided. Document: build volume (W×D×H for each nozzle configuration if multi-nozzle), nozzle diameter(s), heated bed capability, enclosure, maximum print temperature, and any other relevant capabilities. **Cite the source URL.**
2. **Material properties** — look up datasheets for each material. Document: tensile strength, heat deflection temperature, recommended print temperature, shrinkage rate, layer adhesion characteristics. **Cite the source URL.**
3. **Practical print constraints** — derived from specs, not assumed. Maximum single-piece dimensions in each axis (accounting for bed clips, purge area, etc. — these are often smaller than the raw build volume). Recommended minimum wall thickness for structural parts. Tolerance expectations.
4. **Hardware inventory** — document what fasteners, magnets, springs, inserts, etc. are available, with specific dimensions.

**Agent prompt must include:**
- The printer make and model (from user)
- The materials list (from user)
- Instruction to look up manufacturer specifications from the official website or datasheet
- Instruction to cite every number with a source URL
- Instruction to NOT use "typical," "standard," or "common" values — every number must be specific to the actual hardware
- Instruction to save to `hardware/manufacturing-environment.md`

**Agent prompt must NOT include:**
- Assumed dimensions for any equipment ("most FDM printers are...")
- Guidance toward any particular conclusion about what will or won't fit

**Quality gate:**
- Every dimensional constraint cites a specific source (manufacturer spec page URL, material datasheet URL)
- Build volume matches the manufacturer's published spec for the exact model provided
- No "typical" or "standard" values appear anywhere in the document
- The orchestrator verifies the key numbers against their own knowledge of the hardware

**How downstream steps use this document:**
- Step 4a and 4b agents receive the path to `manufacturing-environment.md` and are instructed to read it for all print bed, material, and tolerance constraints
- Step 2A technical research agents receive it for material property assumptions
- No agent in any step may invent or assume a manufacturing constraint that is not in this document

---

### Step 1 — Folder Structure

**Input:** Concept description (what the mechanism does, why it's needed)
**Output:** Empty folder tree under `hardware/printed-parts/<mechanism-name>/`
**Agent:** Not needed — do this directly

Create:
```
hardware/printed-parts/<mechanism-name>/
├── planning/
│   └── research/
└── drawings/
```

No quality gate. This is scaffolding.

---

### Step 2 — Research (parallel agents)

**Input:** Concept description, physical constraints, interface requirements
**Output:** Research documents in `planning/research/`
**Agents:** One per research path, run in parallel

Research falls into two categories. Both run in parallel.

#### 2A — Technical research (one agent per approach)

Each technical research agent investigates one candidate mechanism or approach (e.g., "threaded rod" vs "cam lever" vs "spring detent").

**Agent prompt must include:**
- The design priorities (Section "Design Priorities" above — include verbatim)
- All known physical constraints (envelope, forces, materials, interfaces)
- The specific question the research must answer
- Instruction to save the document to the exact file path
- Instruction to commit and push

#### 2B — Design pattern research (one agent)

This agent studies how existing consumer products solve the same interaction problem. The goal is exposure — the agent (and the decision-maker in Step 3) must understand the landscape of real-world solutions before choosing an approach. Without this exposure, agents default to "functional but bolted-on" designs. With it, they discover patterns like recessed dials, flush-mounted controls, integrated surfaces, and snap-fit assemblies that make a product feel unified.

**Agent prompt must include:**
- The design priorities (verbatim)
- A description of the interaction being designed (what the user does, what the mechanism achieves) — but NOT the current design or any candidate solution. The agent must research patterns without anchoring to an existing approach.
- Instruction to search for and study how shipped consumer products (appliances, electronics, automotive, medical devices) solve the same or analogous interaction problem
- Instruction to focus on products known for exceptional industrial design (e.g., how does a washing machine handle a recessed program dial? How does an oven handle a flush-mounted temperature knob? How does a car handle a twist-lock fuel cap?)
- Instruction to document specific design patterns found, with emphasis on:
  - How the mechanism integrates with the product surface (flush, recessed, proud, hidden)
  - How the product communicates state and affordance without text (icons, detent feel, visual indicators)
  - How assembly/disassembly is handled (snap-fit, living hinges, captive fasteners)
  - How the product looks and feels as a unified object rather than an assembly of parts
- Instruction to save the document to `planning/research/design-patterns.md`
- Instruction to commit and push

**Agent prompt must NOT include:**
- The current design, existing parts.md, or any candidate solution — the research must be unbiased by existing approaches
- Instruction to evaluate or compare against the current design — that evaluation belongs in Step 3

**Quality gate (applies to all Step 2 research):** Each research document must:
- Cover the specific question completely
- Include specific dimensions, materials, and sourcing where applicable
- Address failure modes and concerns
- Be saved to the correct path

**Additional quality gate for 2B:** The design pattern research must:
- Reference at least 3 real shipped products by name
- Describe specific geometric/mechanical details of how each product solves the interaction (not just "it looks nice")
- Connect the patterns back to the design priorities — which patterns serve UX? Which create product unity?

---

### Step 3 — Decision

**Input:** All research documents from Step 2
**Output:** Decision document in `planning/research/decision.md`
**Agent:** One agent that reads ALL research docs

**Agent prompt must include:**
- The design priorities (verbatim) — UX is the primary criterion, cost is irrelevant
- File paths to every research document, **including the design pattern research** (`planning/research/design-patterns.md`)
- Instruction to read the design pattern research first, before evaluating technical candidates — the patterns should inform what "good" looks like
- Decision criteria in priority order: UX first, then mechanical feasibility, then simplicity, then durability adequacy. Cost is last and irrelevant.
- Instruction to evaluate each candidate against the design patterns: does this approach enable product-surface integration, or does it result in bolted-on mechanisms?
- Instruction to make a clear recommendation with rationale
- Instruction to include a bill of materials
- Instruction to note what would change the recommendation

**Quality gate:** The decision must:
- Explicitly rank alternatives on UX first
- Never cite cost as a deciding factor
- Only reject a UX-superior approach if it is mechanically infeasible
- Include a concrete BOM

---

### Step 4a — Conceptual Architecture

Step 4 splits into two sub-steps because exploring the design space and rigorously specifying the result are fundamentally different tasks. Combining them causes the exploration to consume the agent's context window, leaving the specification truncated. Splitting them produces better results in both phases.

**Scope freedom (applies to both 4a and 4b):** The agent designing a mechanism is not limited to the mechanism's own parts. If the design priorities demand it, the agent may and should modify any interfacing part — the shell, walls, panels, other sub-assemblies — to achieve the right design. A mechanism that fits awkwardly into an unchanged shell is worse than a mechanism that reshapes the shell to make the whole product feel unified. When the agent modifies other parts, it must update those parts' documents too.

**Input:** Decision document, design pattern research, existing architecture docs, physical constraints
**Output:** A 1-2 page concept document covering settled high-level decisions
**Agent:** One agent, free to explore and discard ideas

The concept document must address:
1. **Piece count and split strategy** — how many pieces, where do they split, why
2. **Join methods** — how the pieces connect (snap-fit, screws, magnets, etc.)
3. **Seam placement** — where are the seams and how are they treated
4. **User-facing surface composition** — what does the user see and touch, visual hierarchy
5. **Design language** — surface finish, corner treatment, material, what makes this a product
6. **Service access strategy** — how are internals accessed, tiered by frequency
7. **Manufacturing constraints** — print bed limits, orientation, material selection

**Agent prompt must include:**
- The design priorities (verbatim)
- Path to the decision document
- Path to the design pattern research (`planning/research/design-patterns.md`)
- Path to `hardware/manufacturing-environment.md` — the agent must read this for all print bed, material, and tolerance constraints. **The agent must not assume, infer, or use "typical" values for any manufacturing constraint.**
- All known physical constraints (dimensions, what goes inside)
- Instruction to explore freely — try ideas, discard dead ends, show the reasoning
- Instruction to settle on ONE concept and summarize it clearly at the end
- **Instruction NOT to apply the full rubric suite** — that happens in Step 4b

**Quality gate:** The concept document must:
- Clearly state what the design IS (not just what it isn't or what was considered)
- Address all 7 topics listed above
- Be free of unresolved contradictions (e.g., a piece that doesn't fit the print bed)
- Be concise enough that a Step 4b agent can read it without losing context

**Orchestrator checkpoint:** The orchestrator (or user) reviews the 4a concept before launching 4b. This is the natural point for design direction feedback — much cheaper to redirect here than after a full parts.md is written.

---

### Step 4b — Detailed Parts Specification

**This is the most important step in the pipeline.** Everything downstream — drawings, STEP files — faithfully reproduces whatever the parts.md says. If the parts.md describes a mechanism that doesn't make physical sense, the drawings will be beautiful and the STEP files will pass all validation checks, and the mechanism still won't work.

**Input:** Step 4a concept document (settled decisions), decision document, existing architecture docs
**Output:** Updated architecture docs, new or updated `parts.md` for each part (including interfacing parts that were modified)
**Agents:** Can parallelize — one per part, since the concept is already settled

**Agent prompt must include:**
- The design priorities (verbatim)
- Path to the Step 4a concept document (this is the primary input — the design decisions are settled)
- Path to the decision document
- Path to `hardware/manufacturing-environment.md` — the agent must read this for all print bed, material, and tolerance constraints. **The agent must not assume, infer, or use "typical" values for any manufacturing constraint.**
- Paths to all existing docs that need updating (architecture, shell parts.md, etc.)
- Paths to interfacing parts that the agent has freedom to modify (shell, panels, etc.)
- The coordinate system convention from the shell parts.md
- Instruction to follow the format of existing parts.md files
- Instruction to remove stale references (don't leave old mechanism names in docs)
- **Instruction to apply the Parts.md Self-Review Rubrics (below) after generating each document**
- **Instruction NOT to re-explore the design space** — the concept is settled in 4a. The agent's job is to specify it rigorously, not to second-guess it. If a dimensional conflict is discovered, flag it as a design gap rather than redesigning the concept.

#### Parts.md Self-Review Rubrics

The agent MUST apply these rubrics after generating or updating any parts.md or architecture document. Print the rubric results to stdout so the orchestrator can verify.

##### The Grounding Rule (applies to ALL rubrics)

**Every behavioral claim must resolve to a named geometric feature with dimensions.** For every statement in the document that describes a behavior, sensation, limit, outcome, or requirement — name the specific geometric feature that produces it and give its dimensions. If no feature can be identified, the design is incomplete at that point — flag it explicitly as a design gap rather than papering over it with vague language.

This applies everywhere: mechanism narratives, assembly sequences, interface descriptions, UX claims. For instance:
- "Half turn of travel" → what geometric feature limits rotation to exactly 180 degrees?
- "Clear tactile endpoint" → what feature produces the tactile sensation, and what are its dimensions?
- "Correct assembly orientation" → what keying feature prevents incorrect assembly?
- "Self-locking" → what specific geometry (lead angle, friction coefficient) produces the locking behavior?

If a claim cannot be grounded, do not invent a hand-wavy answer. State: **"DESIGN GAP: [claim] has no grounding feature. A [type of feature] is needed."** This is the most valuable output the rubric can produce — it identifies where the design needs more work.

**The grounding rule also applies in reverse — from the design priorities to the geometry.** After writing the document, re-read the Design Priorities section (above) and verify each priority against the actual geometry of every part. If a priority says the design must have property X, and a part violates X, that is a design gap — regardless of whether the document claims to satisfy it. The priorities are constraints on the design, not aspirations. A part that violates a priority must be redesigned, not justified.

##### Rubric A — Mechanism Narrative (MANDATORY)

Before listing any features or dimensions, the document must include a plain-language **mechanism narrative**. Start from the outside and work inward:

0. **What does the user see and touch?** Before describing any mechanism, describe the product surface this mechanism is part of. What does the exterior look like? What does the user's hand contact? Design this surface first — the mechanism exists to serve it, not the other way around.
1. **What moves?** Name every part that translates or rotates during operation. Name every part that is stationary.
2. **What converts the motion?** If the user rotates something and a plate translates, what is the mechanical linkage? (Thread, cam, lever, linkage, gear, etc.)
3. **What constrains each moving part?** For every moving part, state what prevents unwanted degrees of freedom. Example: "Guide pins prevent plate rotation; front wall prevents knob translation."
4. **What provides the return force?** If the mechanism has a rest position, what drives it back? (Spring, gravity, detent, etc.)
5. **What is the user's physical interaction?** Describe the hand motion, the direction of force, and the tactile feedback at each stage (engage, lock, unlock, disengage).

The narrative must be coherent enough that someone who has never seen the mechanism can understand how it works from words alone, with no diagrams. If you cannot write this narrative clearly, the design is not yet understood well enough to specify parts.

Apply the grounding rule to every claim in the narrative. If the narrative says "the user feels X" or "the mechanism stops at Y," the feature that produces X or enforces Y must be named with dimensions.

##### Rubric B — Constraint Chain Diagram (MANDATORY)

Draw an ASCII constraint chain showing how user input becomes mechanical output:

```
[User hand] → [Part A: rotates] → [Thread/cam/linkage] → [Part B: translates] → [Output: collets release]
                  ↑ constrained by: front wall (axial)     ↑ constrained by: guide pins (rotational)
                                                            ↑ returned by: springs
```

Every arrow must name the force transmission mechanism. Every part must list its constraints. If an arrow can't be labeled, the mechanism has a gap.

##### Rubric C — Direction Consistency Check (MANDATORY)

For every statement about direction in the document, verify it against the coordinate system:

1. List every directional claim (e.g., "plate moves toward rear wall", "knob pulls cartridge forward", "springs push plate back")
2. For each claim, convert to axis notation (e.g., "toward rear wall" = "+Y direction")
3. Check: does the mechanism actually produce motion in that direction? Trace the force path through the constraint chain.
4. Check: are there contradictions? (e.g., one place says "push" and another says "pull" for the same motion)

Print a table:

```
| Claim | Direction | Axis | Verified? | Notes |
```

##### Rubric D — Interface Dimensional Consistency (MANDATORY)

For every interface between two parts (mating threads, bore-to-shaft, pin-to-bushing):

1. List both sides of the interface and their dimensions
2. Verify clearance is specified and reasonable (not zero, not negative, not absurdly large)
3. Verify the dimension source (caliper-verified, derived from caliper measurement, or assumed)

```
| Interface | Part A dimension | Part B dimension | Clearance | Source |
```

If any interface has mismatched dimensions (e.g., 12mm shaft in a 12mm bore with no clearance), flag it.

##### Rubric E — Assembly Feasibility Check (MANDATORY)

For the assembly sequence:

1. Can each step physically be performed? (Does the part fit through the opening? Can a hand reach the fastener?)
2. Is the order correct? (Are there steps that must happen before other steps that are listed after them?)
3. Are there parts that become trapped or inaccessible after a later step?
4. If the mechanism needs to be serviced (replace a worn part), what is the disassembly sequence?

##### Rubric F — Part Count Minimization (MANDATORY)

For every pair of parts in the mechanism:

1. Are they permanently joined (epoxy, press-fit with no intent to separate)?
   - If yes → they should be one printed part. Flag if they aren't.
2. Do they move relative to each other during operation?
   - If yes → they must be separate parts. Flag if someone tried to combine them.
3. Are they the same material and could be printed as one piece without support issues?
   - If yes and they don't move relative to each other → consider combining.

**Quality gate:** After all agents complete, verify:
- No references to the old/replaced mechanism remain in any updated document
- The grounding rule is satisfied: no ungrounded behavioral claims remain. Any design gaps are explicitly flagged, not papered over.
- Rubric A narrative is present and coherent — a reader can understand the mechanism from text alone
- Rubric B constraint chain has no unlabeled arrows or unconstrained parts
- Rubric C direction table has no contradictions or unverified claims
- Rubric D interface table has no zero-clearance or mismatched dimensions
- Rubric E assembly sequence is physically feasible
- Rubric F part count is minimized

---

### Step 5 — Engineering Drawings (parallel agents, one per part)

**Input:** parts.md for the part, drawing-standards.md
**Output:** SVG engineering drawing in `drawings/`
**Agents:** One per part, run in parallel

**Agent prompt must include:**
- The design priorities (verbatim)
- Path to the part's parts.md
- Path to `hardware/procedure/engineering-drawings-SVG.md` (MUST read and follow)
- Path to an existing drawing for style reference (e.g., release-plate.svg)
- Path to the feedback memory on engineering drawings (`~/.claude/projects/.../memory/feedback_engineering_drawings.md`)
- Which views are needed (front, side, section, detail)
- Which dimensions to call out
- Explicit instruction to run the SVG checking tools after generation:
  ```
  python3 tools/svg_label_check.py <file.svg>
  python3 tools/svg_adjacency_check.py <file.svg>
  ```
- Explicit instruction to fix any issues and re-run until clean

**Quality gate:**
- SVG checking tools report zero TEXT-TEXT collisions
- All 9 rubrics from drawing-standards.md are applied
- Drawing is saved to the correct path

---

### Step 6 — CadQuery STEP Generation (parallel agents, one per part)

**This is the most critical step.** The STEP file is the final deliverable for each part. A script that was never run is worthless.

**Input:** parts.md, drawing, step-generation-standards.md, interfacing part geometry descriptions
**Output:** Working CadQuery script AND validated STEP file
**Agents:** One per part, run in parallel

**Agent prompt MUST include (non-negotiable):**
- The design priorities (verbatim)
- Path to the part's parts.md
- Path to `hardware/procedure/3d-models-STEP.md` (MUST read and follow ALL rubrics)
- Path to an existing CadQuery script for structure reference (e.g., `cartridge-release-plate/generate_step_cadquery.py`)
- Paths to ALL interfacing geometry descriptions (off-the-shelf parts with caliper measurements)
- The exact Python path for running the script:
  ```
  tools/cad-venv/bin/python3
  ```
- **Explicit instruction: "You MUST run the script after writing it. Run it with `tools/cad-venv/bin/python3 generate_step_cadquery.py`. If validation fails, fix the script and re-run. Repeat until all checks pass with zero FAILs. The deliverable is a working STEP file, not a Python script."**
- Instruction to commit the STEP file alongside the script

**Agent prompt must NEVER include:**
- "Do not try to run the script" — this is forbidden
- "Do not commit" without a reason — scripts and STEP files should be committed together
- Any instruction that shortcuts the validation rubrics

**Quality gate (non-negotiable):**
- Script runs without errors
- All Rubric 3 point-in-solid probes pass (zero FAILs)
- Rubric 4 solid validity passes
- Rubric 5 bounding box reconciliation passes
- STEP file exists on disk
- STEP file and script are both committed

---

## Step Dependencies

```
Step 0 (manufacturing environment — run once, verified by orchestrator)
  │
  ▼
Step 1 (folders)
  │
  ├──→ Step 2A-1 (technical research — reads mfg env) ──┐
  ├──→ Step 2A-2 (technical research — reads mfg env) ──┤
  └──→ Step 2B   (design pattern research)            ───┤
                                                          │
                                                          ▼
                              Step 3 (decision — reads ALL research including patterns)
                                                          │
                              Step 4a (concept — reads mfg env, explore, settle on one concept)
                                                          │
                                          [orchestrator/user review]
                                                          │
                              Step 4b (detailed parts.md — reads mfg env, one per part, parallel)
                                                          │
                    ┌─────────────────────────────────────┼──────────────────────────────┐
                    ▼                                     ▼                              ▼
              Step 5a (drawing)                     Step 5b (drawing)                   ...
                    │                                     │
                    ▼                                     ▼
              Step 6a (STEP)                        Step 6b (STEP)                      ...
```

- **Step 0 runs once** at project start (or when hardware changes). It produces `manufacturing-environment.md`, which is verified by the orchestrator before any design work begins. All downstream steps that reference physical constraints read this document.
- All Step 2 agents (2A-1, 2A-2, 2B) run in parallel (no dependencies between research paths)
- Step 3 waits for ALL Step 2 agents to complete (including design pattern research)
- Step 4a waits for Step 3
- **Step 4a → 4b has an orchestrator checkpoint** — review the concept before committing to detailed specification
- Step 4b agents run in parallel (one per part) after 4a is approved
- Step 5 agents run in parallel (one per part) after Step 4b for the same part
- Step 6 agents run in parallel (one per part) after Step 5 for the same part
- Step 5 and Step 6 for the SAME part are sequential (drawing informs STEP)
- Step 5 and Step 6 for DIFFERENT parts can overlap

---

## Common Mistakes This Procedure Prevents

1. **"Do not run the script"** — Never. The STEP file is the deliverable. An unrun script is an unfinished step.

2. **Decision agent ignoring UX** — The design priorities are included verbatim in every agent prompt. UX is always criterion #1. Cost is always irrelevant.

3. **Separate parts that should be one** — Step 4's quality gate requires checking: "if two parts are permanently joined, they should be one printed part."

4. **Stale references to old mechanisms** — Step 4's quality gate requires checking that no old mechanism names remain in updated docs.

5. **Agents not reading the standards** — Every Step 5 and Step 6 agent prompt explicitly includes the path to the relevant standards document and requires reading it.

6. **Skipping SVG tool checks** — Step 5 requires running both checking tools and getting clean results.

7. **Missing the CadQuery venv** — Prerequisites section verifies it exists before any work begins.

8. **Optimizing pipeline throughput over step correctness** — Each step has an explicit quality gate. No step is complete until its gate passes. A fast pipeline that produces unvalidated output is worse than a slower one that produces working artifacts.

9. **Combining exploration and specification in one agent** — Step 4 splits into 4a (explore the design space, settle on a concept) and 4b (specify the settled concept rigorously). Combining them causes the agent to spend most of its context on exploration, leaving the specification truncated. The 4a→4b handoff also creates a natural checkpoint for orchestrator/user review.

10. **Research agent anchoring to current design** — Step 2B design pattern research must NOT receive the current design or any candidate solution. Anchoring to an existing approach causes the agent to rationalize the status quo rather than discovering better patterns. The evaluation of candidates against patterns belongs in Step 3.

11. **Assumed manufacturing constraints** — No agent may assume "typical," "standard," or "common" values for any manufacturing parameter (print bed size, material properties, tolerances). A research agent once assumed a "256mm print bed" because it was a common FDM spec — the actual printer had a 325×320mm bed. The entire enclosure split strategy, joint engineering, and piece count were designed around a constraint that didn't exist. Every manufacturing constraint must come from `manufacturing-environment.md`, which is established in Step 0 from verified manufacturer specifications. If Step 0 has not been run, no design work may proceed.

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
- **Drawing standards:** `hardware/procedure/engineering-drawings-SVG.md`
- **STEP generation standards:** `hardware/procedure/3d-models-STEP.md`
