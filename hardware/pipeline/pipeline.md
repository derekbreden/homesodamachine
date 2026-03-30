# Hardware Design Pipeline

**Parts are designed iteratively. The first version of any part is the simplest shape that occupies the correct space. Retention, joinery, and interfaces with parts that don't exist yet are added in later rounds — not anticipated in the first.**

---

## Roles

- **Orchestrator** — [`orchestrator.md`](orchestrator.md). Runs through a phase or season, launching engineering managers for each item in sequence. Stops at print-and-test steps.
- **Engineering Manager** — reads this document. Runs pipeline steps for one build sequence item at a time.
- **Build Planner** — [`build-planner.md`](build-planner.md). Decides what gets built when. Maintains the build sequence in `hardware/vision.md` Section 4.

---

## How It Works

The build sequence in `hardware/vision.md` Section 4 defines every deliverable. Each line in the build sequence is one pipeline run. The engineering manager takes one line, produces a parts spec and a STEP file, commits, and moves on.

### Step 1 — Parts Specification

One agent reads the build sequence line and writes `parts.md` for the part. The build sequence line is the scope — do not add features beyond what it says, do not solve problems it defers to later phases.

**Inputs:**
- The build sequence line from `hardware/vision.md` (this is the scope)
- `hardware/requirements.md` (printer specs, materials, FDM constraints)
- `hardware/vision.md` (product values, architecture context)
- Component datasheets in `hardware/off-the-shelf-parts/` (caliper-verified dimensions)
- Any existing parts that this part interfaces with (for matching dimensions)

**The spec must include:**

1. **Coordinate system** — origin, axes, envelope.
2. **Feature list** — every feature with dimensions, positions, and justification. If a feature is not in the build sequence line and is not required by physics, it does not belong.
3. **Print orientation** — which face goes on the build plate and why.
4. **FDM check** — overhangs, wall thickness, bridge spans per `hardware/requirements.md` Section 6.
5. **Feature traceability** — every feature traces to the build sequence line or a physical necessity (structural load, manufacturing constraint, assembly alignment, routing). Features that trace to neither are unjustified. Flag them for removal.
6. **Path continuity** — for any set of features that must form a continuous path (fastener, fluid, wire), verify that segments connect at every transition with no gaps.

**The spec must NOT include:**

- Mechanism narratives longer than a few sentences. The part is described by its features, not by a story.
- Direction consistency tables, constraint chain diagrams, or assembly feasibility checklists. These were overhead for simple parts and didn't catch real errors.
- Features for future phases. If the build sequence line says "no strut bores — those come in Phase 4," the spec does not mention strut bores except to note they are out of scope.

**Save to:** `hardware/printed-parts/<part-name>/planning/parts.md`

### Step 2 — CadQuery Generation

One agent reads `parts.md` and produces a CadQuery script that generates a validated STEP file. See `steps/6-step-generation.md` for CadQuery standards, techniques, and validation requirements.

**The agent MUST run the script.** Zero validation failures required. An unrun script is not a deliverable. The STEP file is the deliverable.

**Save script to:** `hardware/printed-parts/<part-name>/generate_step_cadquery.py`
**Save STEP to:** `hardware/printed-parts/<part-name>/<part-name>-cadquery.step`

### Commit and Push

After each step. Every step produces a checkpoint. We would rather have a checkpoint to roll back to than worry about every checkpoint being correct.

---

## Revision Archive

When a build sequence item modifies an existing part (e.g., "coupler tray v2" replaces "coupler tray v1"), the orchestrator archives the current files before starting the new iteration.

**Before overwriting, copy the current files into:**

```
hardware/printed-parts/<part-name>/revisions/<label>/
```

Where `<label>` is: `s<season>-p<phase>-item<number>-v<version>`

Example: coupler tray v1 was Season 1, Phase 1, item 3, first version:

```
hardware/printed-parts/cartridge/coupler-tray/
├── planning/
│   └── parts.md                ← always current
├── generate_step_cadquery.py   ← always current
├── coupler-tray-cadquery.step  ← always current
└── revisions/
    └── s1-p1-item3-v1/
        ├── parts.md
        ├── generate_step_cadquery.py
        └── coupler-tray-cadquery.step
```

The working files are always the latest version. The `revisions/` folder is the browsable history — any agent or human can see what a prior iteration looked like without digging through git.

---

## Technical Research (optional, rare)

Most parts can be fully specified from the build sequence line, requirements, vision, and component datasheets. Occasionally a part involves physics that no agent can derive from existing information (e.g., how a flexible bag behaves under gravity at a specific angle). In that case, commission a research agent to answer the specific technical question before starting the spec. See `steps/2a-technical-research.md`.

Do not commission research to find features to add. The build sequence line is the scope.

---

## Common Mistakes

1. **Adding features the build sequence doesn't ask for.** If the line says "flat plate with 8 holes," the deliverable is a flat plate with 8 holes. Not a U-channel. Not a box. Not a plate with ribs.
2. **Solving problems deferred to later phases.** If the line says "no strut bores — those come in Phase 4," do not design strut bores, do not leave space for strut bores, do not think about strut bores.
3. **Not running the script.** The STEP file is the deliverable. An unrun script is nothing.
4. **Inventing load cases to justify geometry.** "Structural rigidity" without deflection numbers and clearance constraints is not a justification. If the failure can't be quantified, the feature isn't justified.
5. **Writing a synthesis, concept, or architecture document.** The build sequence line is the synthesis. The product owner already did the decomposition. Go straight to spec.

---

## Agent Prompt Template

```
You are the engineering manager for [part name].

**Your deliverable — read this first:**
[Exact build sequence line from vision.md, including explicit exclusions]

That line is your complete scope. Do not add features beyond what it says.

**Read these documents:**
- hardware/requirements.md — hard constraints, printer specs, FDM rules
- hardware/vision.md — product values and architecture context
- [paths to relevant component datasheets]
- [paths to any existing interfacing parts]

**Step 1: Write the parts spec.**
Save to: hardware/printed-parts/<part-name>/planning/parts.md
Commit and push.

**Step 2: Write the CadQuery script, run it, produce the STEP file.**
Follow the standards in hardware/pipeline/steps/6-step-generation.md
Save script to: hardware/printed-parts/<part-name>/generate_step_cadquery.py
Save STEP to: hardware/printed-parts/<part-name>/<part-name>-cadquery.step
Commit and push.
```

---

## Related Documents

- **Requirements:** `hardware/requirements.md`
- **Vision and build sequence:** `hardware/vision.md`
- **CadQuery standards:** `hardware/pipeline/steps/6-step-generation.md`
- **Build planner role:** `hardware/pipeline/build-planner.md`
