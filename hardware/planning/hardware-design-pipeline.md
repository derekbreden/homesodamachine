# Hardware Design Pipeline

This document defines the procedure for designing a new 3D-printed part or mechanism from concept through validated STEP file. It is the orchestration guide for multi-agent work — every step has explicit inputs, outputs, agent instructions, and quality gates.

**This procedure exists because improvised orchestration produces unvalidated output.** Every step matters. Skipping validation, misweighting decisions, or treating intermediate artifacts as deliverables are the failure modes this document prevents.

---

## Design Priorities

These apply to every step and every agent in the pipeline. Include them verbatim in every agent prompt.

1. **UX is the primary concern** — above durability, simplicity, prototypability, and cost. One-handed operation, intuitive feel, speed, and dark-cabinet usability define "good."
2. **Cost is no concern** — never use cost as a factor in any decision.
3. **Durability must be adequate, not maximal** — if it survives the expected lifecycle with reasonable margin, it passes. Don't penalize an approach for having less margin than an alternative.
4. **The deliverable is always the final artifact, not the script or document that produces it.** A STEP generation script that was never run is not a deliverable. A parts.md that contradicts the research is not a deliverable.

---

## Prerequisites

Before starting the pipeline, verify:

1. **CadQuery venv exists and works:**
   ```
   tools/cad-venv/bin/python3 -c "import cadquery; print(cadquery.__version__)"
   ```
   If this fails, fix it before proceeding. Do not work around a broken environment.

2. **SVG checking tools exist:**
   ```
   ls tools/svg_label_check.py tools/svg_adjacency_check.py tools/step_validate.py
   ```

3. **Standards documents are current:**
   - `hardware/planning/drawing-standards.md`
   - `hardware/planning/step-generation-standards.md`
   - This document (`hardware/planning/hardware-design-pipeline.md`)

---

## Pipeline Steps

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

**Agent prompt must include:**
- The design priorities (Section "Design Priorities" above — include verbatim)
- All known physical constraints (envelope, forces, materials, interfaces)
- The specific question the research must answer
- Instruction to save the document to the exact file path
- Instruction to commit and push

**Quality gate:** Each research document must:
- Cover the specific question completely
- Include specific dimensions, materials, and sourcing where applicable
- Address failure modes and concerns
- Be saved to the correct path

---

### Step 3 — Decision

**Input:** All research documents from Step 2
**Output:** Decision document in `planning/research/decision.md`
**Agent:** One agent that reads ALL research docs

**Agent prompt must include:**
- The design priorities (verbatim) — UX is the primary criterion, cost is irrelevant
- File paths to every research document
- Decision criteria in priority order: UX first, then mechanical feasibility, then simplicity, then durability adequacy. Cost is last and irrelevant.
- Instruction to make a clear recommendation with rationale
- Instruction to include a bill of materials
- Instruction to note what would change the recommendation

**Quality gate:** The decision must:
- Explicitly rank alternatives on UX first
- Never cite cost as a deciding factor
- Only reject a UX-superior approach if it is mechanically infeasible
- Include a concrete BOM

---

### Step 4 — Architecture and Parts

**This is the most important step in the pipeline.** Everything downstream — drawings, STEP files — faithfully reproduces whatever the parts.md says. If the parts.md describes a mechanism that doesn't make physical sense, the drawings will be beautiful and the STEP files will pass all validation checks, and the mechanism still won't work.

**Input:** Decision document, existing architecture docs
**Output:** Updated `cartridge-architecture.md`, new or updated `parts.md` for each part
**Agents:** Can parallelize if architecture update and parts.md are independent

**Agent prompt must include:**
- The design priorities (verbatim)
- Path to the decision document
- Paths to all existing docs that need updating (architecture, shell parts.md, etc.)
- The coordinate system convention from the shell parts.md
- Instruction to follow the format of existing parts.md files
- Instruction to remove stale references (don't leave old mechanism names in docs)
- **Instruction to apply the Parts.md Self-Review Rubrics (below) after generating each document**

#### Parts.md Self-Review Rubrics

The agent MUST apply these rubrics after generating or updating any parts.md or architecture document. Print the rubric results to stdout so the orchestrator can verify.

##### Rubric A — Mechanism Narrative (MANDATORY)

Before listing any features or dimensions, the document must include a plain-language **mechanism narrative** that answers:

1. **What moves?** Name every part that translates or rotates during operation. Name every part that is stationary.
2. **What converts the motion?** If the user rotates something and a plate translates, what is the mechanical linkage? (Thread, cam, lever, linkage, gear, etc.)
3. **What constrains each moving part?** For every moving part, state what prevents unwanted degrees of freedom. Example: "Guide pins prevent plate rotation; front wall prevents knob translation."
4. **What provides the return force?** If the mechanism has a rest position, what drives it back? (Spring, gravity, detent, etc.)
5. **What is the user's physical interaction?** Describe the hand motion, the direction of force, and the tactile feedback at each stage (engage, lock, unlock, disengage).

The narrative must be coherent enough that someone who has never seen the mechanism can understand how it works from words alone, with no diagrams. If you cannot write this narrative clearly, the design is not yet understood well enough to specify parts.

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
- Path to `hardware/planning/drawing-standards.md` (MUST read and follow)
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
- Path to `hardware/planning/step-generation-standards.md` (MUST read and follow ALL rubrics)
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
Step 1 (folders)
  │
  ├──→ Step 2a (research path A) ──┐
  └──→ Step 2b (research path B) ──┤
                                    │
                                    ▼
                              Step 3 (decision)
                                    │
                              Step 4 (architecture + parts.md)
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              Step 5a (drawing)  Step 5b (drawing)  ...
                    │               │
                    ▼               ▼
              Step 6a (STEP)    Step 6b (STEP)     ...
```

- Steps 2a and 2b run in parallel (no dependencies between research paths)
- Step 3 waits for ALL Step 2 agents to complete
- Step 4 waits for Step 3
- Step 5 agents run in parallel (one per part) after Step 4
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

---

## Agent Prompt Template

Every agent in this pipeline should receive a prompt structured as:

```
You are [role] for [part/mechanism name].

**DESIGN PRIORITIES (apply to all decisions):**
- UX is the primary concern — above durability, simplicity, prototypability, and cost
- Cost is no concern — never use cost as a factor
- Durability must be adequate, not maximal
- The deliverable is the final artifact, not the intermediate script

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

- **Drawing standards:** `drawing-standards.md`
- **STEP generation standards:** `step-generation-standards.md`
- **System architecture:** `architecture.md`
- **Cartridge architecture:** `cartridge-architecture.md`
- **Spatial layout:** `spatial-layout.md`
