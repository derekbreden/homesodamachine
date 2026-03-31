# Orchestrator

**Parts are designed iteratively. The first version of any part is the simplest shape that occupies the correct space. Retention, joinery, and interfaces with parts that don't exist yet are added in later rounds — not anticipated in the first.**

The orchestrator reads the build sequence in `hardware/vision.md` Section 4, identifies what needs to be done next, and produces parts specs and STEP files for each item in order.

---

## Roles

- **Orchestrator** — this document. Runs through a phase or season, producing deliverables for each item. Stops at print-and-test steps.
- **Build Planner** — [`build-planner.md`](build-planner.md). Decides what gets built when. Maintains the build sequence.

---

## How it works

1. Read `hardware/vision.md` Section 4 (the build sequence).
2. Read the existing parts in `hardware/printed-parts/` to determine what's already done. A build sequence item is done if its STEP file exists.
3. Starting from the first incomplete item, for each item in order:
   - If the item is a **print-and-test step** (e.g., "Print and test the split," "Full assembly dry fit"), stop. These require the product owner physically holding parts. Report what you completed and what the next physical step is.
   - If the item modifies an existing part, archive the current files per the revision archive convention below before proceeding.
   - Produce the deliverable (see "For each item" below).
   - Commit and push.
   - Verify a STEP file was produced. If not, flag the failure and stop.
   - Move to the next item.

---

## For each item

The build sequence line is the complete scope. Do not add features beyond what it says. Do not solve problems it defers to later phases.

### Write the parts spec

Read:
- The build sequence line from `hardware/vision.md` (this is the scope)
- `hardware/requirements.md` (printer specs, materials, FDM constraints)
- `hardware/vision.md` (product values, architecture context)
- Component datasheets in `hardware/off-the-shelf-parts/` (caliper-verified dimensions)
- Any existing parts that this part interfaces with (for matching dimensions)

The spec must include:

1. **Coordinate system** — origin, axes, envelope.
2. **Feature list** — every feature with dimensions, positions, and justification. If a feature is not in the build sequence line and is not required by physics, it does not belong.
3. **Print orientation** — which face goes on the build plate and why.
4. **FDM check** — overhangs, wall thickness, bridge spans per `hardware/requirements.md` Section 6.
5. **Feature traceability** — every feature traces to the build sequence line or a physical necessity (structural load, manufacturing constraint, assembly alignment, routing). Features that trace to neither are unjustified. Flag them for removal.
6. **Path continuity** — for any set of features that must form a continuous path (fastener, fluid, wire), verify that segments connect at every transition with no gaps.

The spec must NOT include:

- Mechanism narratives longer than a few sentences. The part is described by its features, not by a story.
- Direction consistency tables, constraint chain diagrams, or assembly feasibility checklists.
- Features for future phases. If the build sequence line says "no strut bores — those come in Phase 4," the spec does not mention strut bores except to note they are out of scope.

Save to: `hardware/printed-parts/<part-name>/parts.md`
Commit and push.

### Write the CadQuery script and produce the STEP file

Read `parts.md` and follow the standards in [`step-generation.md`](step-generation.md) for CadQuery techniques and validation requirements.

**Run the script.** Zero validation failures required. An unrun script is not a deliverable. The STEP file is the deliverable.

Save script to: `hardware/printed-parts/<part-name>/generate_step_cadquery.py`
Save STEP to: `hardware/printed-parts/<part-name>/<part-name>-cadquery.step`
Commit and push.

---

## When to stop

- **A print-and-test step is next.** The product owner needs to physically verify something.
- **A step fails.** Couldn't produce a STEP file, or validation failures.
- **The phase is complete.** Ask the product owner if they want to continue into the next phase.
- **The season is complete.** Always stop at season boundaries.

---

## Revision Archive

When a build sequence item modifies an existing part (e.g., "coupler tray v2" replaces "coupler tray v1"), archive the current files before starting the new iteration.

**Before overwriting, copy the current files into:**

```
hardware/printed-parts/<part-name>/revisions/<label>/
```

Where `<label>` is: `s<season>-p<phase>-item<number>-v<version>`

Example:

```
hardware/printed-parts/cartridge/coupler-tray/
├── parts.md                    ← always current
├── generate_step_cadquery.py   ← always current
├── coupler-tray-cadquery.step  ← always current
└── revisions/
    └── s1-p1-item3-v1/
        ├── parts.md
        ├── generate_step_cadquery.py
        └── coupler-tray-cadquery.step
```

---

## Common Mistakes

1. **Adding features the build sequence doesn't ask for.** If the line says "flat plate with 8 holes," the deliverable is a flat plate with 8 holes. Not a U-channel. Not a box. Not a plate with ribs.
2. **Solving problems deferred to later phases.** If the line says "no strut bores — those come in Phase 4," do not design strut bores, do not leave space for strut bores, do not think about strut bores.
3. **Not running the script.** The STEP file is the deliverable. An unrun script is nothing.
4. **Inventing load cases to justify geometry.** "Structural rigidity" without deflection numbers and clearance constraints is not a justification. If the failure can't be quantified, the feature isn't justified.
5. **Writing a synthesis, concept, or architecture document.** The build sequence line is the synthesis. The product owner already did the decomposition. Go straight to spec.

---

## What this agent does NOT do

- **Does not modify the build sequence.** If something seems wrong or out of order, report it to the product owner. The build planner maintains the sequence.
- **Does not skip items.** The sequence is ordered for a reason. Do not reorder or parallelize unless the product owner explicitly says to.
- **Does not continue past print-and-test steps.** Physical verification gates are not optional.

---

## Prompt to launch

```
You are the orchestrator for the pump cartridge build.

Read hardware/pipeline/orchestrator.md and follow it.
Run [Phase X / through Season X / continue from where we left off].
```
