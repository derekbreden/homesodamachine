# Parts Specification

This document defines the procedure for the parts specification agent (Step 4b). This agent takes a single sub-component (from Step 4d) with its resolved spatial geometry (from Step 4s) and rigorously specifies it. It does not re-explore the design space — that was done in the conceptual architecture step. If a dimensional conflict is discovered, it flags it as a design gap rather than redesigning the concept.

**Scope.** This step runs once per sub-component (or once per part if Step 4d passed through). Each sub-component gets its own parts.md. The spatial resolution document (Step 4s) provides every derived dimension — the 4b agent should not need to perform trigonometry, coordinate transforms, or physics calculations. If it does, the spatial resolution step is incomplete.

**This is the most important step in the pipeline.** Everything downstream — drawings, STEP files — faithfully reproduces whatever the parts.md says. If the parts.md describes a mechanism that doesn't make physical sense, the drawings will be beautiful and the STEP files will pass all validation checks, and the mechanism still won't work.

---

## Scope freedom

Same as conceptual architecture: the agent may modify any interfacing part if the product values demand it. When it does, it must update those parts' documents too.

## Agent prompt must include

- Path to `hardware/requirements.md` and `hardware/vision.md`
- Path to the conceptual architecture document (the design decisions are settled)
- Path to the decomposition document (4d output) — identifies this sub-component and its interface boundaries
- Path to the spatial resolution document (4s output) — this is the primary dimensional input. Every derived dimension is already resolved into the sub-component's local frame.
- Path to the synthesis document
- Printer specs and materials are in `hardware/requirements.md`. **The agent must not assume, infer, or use "typical" values for any manufacturing constraint.**
- Paths to all existing docs that need updating (architecture, shell parts.md, etc.)
- Paths to interfacing parts that the agent has freedom to modify (shell, panels, etc.)
- The coordinate system convention from the shell parts.md
- Instruction to follow the format of existing parts.md files
- Instruction to remove stale references (don't leave old mechanism names in docs)
- **Instruction to apply the Self-Review Rubrics (below) after generating each document**
- **Instruction NOT to re-explore the design space** — the concept is settled. The agent's job is to specify it rigorously, not to second-guess it.

---

## Self-Review Rubrics

The agent MUST apply these rubrics after generating or updating any parts.md or architecture document. Print the rubric results to stdout so the orchestrator can verify.

### The Grounding Rule (applies to ALL rubrics)

**Every behavioral claim must resolve to a named geometric feature with dimensions.** For every statement in the document that describes a behavior, sensation, limit, outcome, or requirement — name the specific geometric feature that produces it and give its dimensions. If no feature can be identified, the design is incomplete at that point — flag it explicitly as a design gap rather than papering over it with vague language.

This applies everywhere: mechanism narratives, assembly sequences, interface descriptions, UX claims. For instance:
- "Half turn of travel" -> what geometric feature limits rotation to exactly 180 degrees?
- "Clear tactile endpoint" -> what feature produces the tactile sensation, and what are its dimensions?
- "Correct assembly orientation" -> what keying feature prevents incorrect assembly?
- "Self-locking" -> what specific geometry (lead angle, friction coefficient) produces the locking behavior?

If a claim cannot be grounded, do not invent a hand-wavy answer. State: **"DESIGN GAP: [claim] has no grounding feature. A [type of feature] is needed."** This is the most valuable output the rubric can produce — it identifies where the design needs more work.

**Path claims require continuity, not just existence.** When a behavioral claim involves something traversing a path — a screw passing through a hole into a threaded insert, fluid flowing from an inlet to an outlet, a wire routed from board to connector — grounding to individually named features is not sufficient. The features must form a continuous path with no gaps or obstructions. For each path claim, verify that every segment connects to the next: check that stop depths match start depths at every transition, that diameters are compatible at every junction, and that no solid material blocks the path at any point. If segments are specified independently and a gap exists between them, that is a **DESIGN GAP** — regardless of whether each segment is individually correct.

**The grounding rule also applies in reverse — from the product values to the geometry.** After writing the document, re-read the product values (from `hardware/vision.md`) and verify each value against the actual geometry of every part. If a value says the design must have property X, and a part violates X, that is a design gap — regardless of whether the document claims to satisfy it. The values are constraints on the design, not aspirations.

### Rubric A — Mechanism Narrative (MANDATORY)

Before listing any features or dimensions, the document must include a plain-language **mechanism narrative**. Start from the outside and work inward:

0. **What does the user see and touch?** Before describing any mechanism, describe the product surface this mechanism is part of. What does the exterior look like? What does the user's hand contact? Design this surface first — the mechanism exists to serve it, not the other way around.
1. **What moves?** Name every part that translates or rotates during operation. Name every part that is stationary.
2. **What converts the motion?** If the user rotates something and a plate translates, what is the mechanical linkage? (Thread, cam, lever, linkage, gear, etc.)
3. **What constrains each moving part?** For every moving part, state what prevents unwanted degrees of freedom. Example: "Guide pins prevent plate rotation; front wall prevents knob translation."
4. **What provides the return force?** If the mechanism has a rest position, what drives it back? (Spring, gravity, detent, etc.)
5. **What is the user's physical interaction?** Describe the hand motion, the direction of force, and the tactile feedback at each stage (engage, lock, unlock, disengage).

The narrative must be coherent enough that someone who has never seen the mechanism can understand how it works from words alone, with no diagrams. If you cannot write this narrative clearly, the design is not yet understood well enough to specify parts.

Apply the grounding rule to every claim in the narrative. If the narrative says "the user feels X" or "the mechanism stops at Y," the feature that produces X or enforces Y must be named with dimensions.

### Rubric B — Constraint Chain Diagram (MANDATORY)

Draw an ASCII constraint chain showing how user input becomes mechanical output:

```
[User hand] -> [Part A: rotates] -> [Thread/cam/linkage] -> [Part B: translates] -> [Output: collets release]
                  ^ constrained by: front wall (axial)     ^ constrained by: guide pins (rotational)
                                                            ^ returned by: springs
```

Every arrow must name the force transmission mechanism. Every part must list its constraints. If an arrow can't be labeled, the mechanism has a gap.

### Rubric C — Direction Consistency Check (MANDATORY)

For every statement about direction in the document, verify it against the coordinate system:

1. List every directional claim (e.g., "plate moves toward rear wall", "knob pulls cartridge forward", "springs push plate back")
2. For each claim, convert to axis notation (e.g., "toward rear wall" = "+Y direction")
3. Check: does the mechanism actually produce motion in that direction? Trace the force path through the constraint chain.
4. Check: are there contradictions? (e.g., one place says "push" and another says "pull" for the same motion)

Print a table:

```
| Claim | Direction | Axis | Verified? | Notes |
```

### Rubric D — Interface and Path Consistency (MANDATORY)

**Part 1 — Interface dimensions.** For every interface between two parts (mating threads, bore-to-shaft, pin-to-bushing):

1. List both sides of the interface and their dimensions
2. Verify clearance is specified and reasonable (not zero, not negative, not absurdly large)
3. Verify the dimension source (caliper-verified, derived from caliper measurement, or assumed)

```
| Interface | Part A dimension | Part B dimension | Clearance | Source |
```

If any interface has mismatched dimensions (e.g., 12mm shaft in a 12mm bore with no clearance), flag it.

**Part 2 — Path continuity.** For every set of features that must form a continuous path or mating pair (fastener paths, fluid channels, wire routes, snap-fit hook and catch pairs):

1. List every segment of the path in order, with its start and stop coordinates
2. Verify that each segment's stop meets the next segment's start — no gaps, no overlaps that create solid obstructions
3. Verify that diameters or cross-sections are compatible at every transition

```
| Path | Segment | Start | Stop | Diameter/Section | Connects to next? |
```

If any transition has a gap (segment A ends at Y=5.0, segment B starts at Y=5.5), flag it as a path discontinuity — a **DESIGN GAP**, not a clearance value.

### Rubric E — Assembly Feasibility Check (MANDATORY)

For the assembly sequence:

1. Can each step physically be performed? (Does the part fit through the opening? Can a hand reach the fastener?)
2. Is the order correct? (Are there steps that must happen before other steps that are listed after them?)
3. Are there parts that become trapped or inaccessible after a later step?
4. If the mechanism needs to be serviced (replace a worn part), what is the disassembly sequence?

### Rubric F — Part Count Minimization (MANDATORY)

For every pair of parts in the mechanism:

1. Are they permanently joined (epoxy, press-fit with no intent to separate)?
   - If yes -> they should be one printed part. Flag if they aren't.
2. Do they move relative to each other during operation?
   - If yes -> they must be separate parts. Flag if someone tried to combine them.
3. Are they the same material and could be printed as one piece without support issues?
   - If yes and they don't move relative to each other -> consider combining.

### Rubric G — FDM Printability (MANDATORY)

This rubric verifies that every feature in the part can be FDM-printed as designed. The FDM manufacturing constraints in `hardware/requirements.md` (Section 6) are the authoritative source — read them before applying this rubric.

**Step 1 — Print orientation.** State the intended print orientation (which face sits on the build plate). If multiple orientations were considered, state why this one was chosen. If the part's function constrains the orientation (e.g., a mating surface that must be on the build plate for accuracy, or a flex feature that must be oriented for layer strength), state that constraint.

**Step 2 — Overhang audit.** For every surface in the part, determine its angle relative to horizontal in the stated print orientation. Print a table:

```
| Surface / Feature | Angle from horizontal | Printable? | Resolution |
```

- **≥ 45° from horizontal** (i.e., ≤ 45° overhang): Printable without support. Mark "OK."
- **< 45° from horizontal** (i.e., > 45° overhang): Requires resolution. Options:
  - **Redesign to eliminate:** Add a chamfer, fillet, gusset, or taper that brings the angle above 45°. This is the preferred resolution. State the specific geometry added.
  - **Intentional designed support:** If the overhang is functionally necessary (e.g., snap-fit undercut, internal ledge), state: what the support geometry is, how it will be removed, and confirm there is physical access for removal. Do not write "slicer will add supports" — that is not a design decision.
  - **DESIGN GAP:** If neither redesign nor intentional support is feasible, flag it explicitly.

**Step 3 — Wall thickness check.** For every wall, rib, and thin feature, verify thickness against the minimums in requirements.md (0.8mm standard, 1.2mm structural). Flag any violations.

**Step 4 — Bridge span check.** For every horizontal unsupported span, verify length is under 15mm. If over, either add support geometry or break the span with intermediate supports designed into the part.

**Step 5 — Layer strength check.** For every feature that flexes, bears tension, or is a snap-fit arm: verify that the intended print orientation places layer lines parallel to (not perpendicular to) the load direction. If the print orientation conflicts between features, note the tradeoff and state which feature took priority and why.

### Rubric H — Feature Traceability (MANDATORY)

For every feature in the design, the agent must state its justification. Every feature must trace to one of exactly two sources:

1. **The vision.** Name the specific line or requirement from `hardware/vision.md` that this feature serves.
2. **Physical necessity.** The feature exists because the part would not function without it. Physical necessity has exactly four categories:
   - **Structural** — the part would deform, flex, or fail without this feature. Name the load.
   - **Manufacturing** — FDM printability requires this feature. (Rubric G should already cover this.)
   - **Assembly** — the parts cannot be aligned or joined without this feature.
   - **Routing** — a wire, tube, or cable needs a path and this feature provides it.

Print a table:

```
| Feature | Justification source | Specific reference |
```

- If the source is the vision, the "Specific reference" column quotes or paraphrases the vision line.
- If the source is physical necessity, the "Specific reference" column names the category and the specific load, constraint, or path.
- **If a feature cannot be traced to either source, it is unjustified.** Flag it: **"UNJUSTIFIED: [feature] serves no vision requirement and no physical necessity. Flag for removal."**

Do not invent justifications. "Good engineering practice," "robustness," "future flexibility," "serviceability beyond what the vision describes," and "development convenience" are not valid sources. If a feature exists only because it seems like a good idea, it is unjustified.

---

## Quality gate

After all agents complete, verify:
- No references to the old/replaced mechanism remain in any updated document
- The grounding rule is satisfied: no ungrounded behavioral claims remain. Any design gaps are explicitly flagged, not papered over.
- Rubric A narrative is present and coherent — a reader can understand the mechanism from text alone
- Rubric B constraint chain has no unlabeled arrows or unconstrained parts
- Rubric C direction table has no contradictions or unverified claims
- Rubric D interface table has no zero-clearance or mismatched dimensions; path continuity table has no gaps or obstructions
- Rubric E assembly sequence is physically feasible
- Rubric F part count is minimized
- Rubric G printability: no unresolved overhangs, no sub-minimum walls, no unsupported long bridges, print orientation stated with rationale
- Rubric H traceability: every feature traces to a vision line or a physical necessity (structural, manufacturing, assembly, routing). No unjustified features remain.
