# Parts Specification

This document defines the procedure for the parts specification agent (Step 4b). This agent takes a settled concept and rigorously specifies every part. It does not re-explore the design space — that was done in the conceptual architecture step. If a dimensional conflict is discovered, it flags it as a design gap rather than redesigning the concept.

**This is the most important step in the pipeline.** Everything downstream — drawings, STEP files — faithfully reproduces whatever the parts.md says. If the parts.md describes a mechanism that doesn't make physical sense, the drawings will be beautiful and the STEP files will pass all validation checks, and the mechanism still won't work.

---

## Scope freedom

Same as conceptual architecture: the agent may modify any interfacing part if the product values demand it. When it does, it must update those parts' documents too.

## Agent prompt must include

- Path to `hardware/requirements.md` and `hardware/vision.md`
- Path to the conceptual architecture document (this is the primary input — the design decisions are settled)
- Path to the decision document
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

### Rubric D — Interface Dimensional Consistency (MANDATORY)

For every interface between two parts (mating threads, bore-to-shaft, pin-to-bushing):

1. List both sides of the interface and their dimensions
2. Verify clearance is specified and reasonable (not zero, not negative, not absurdly large)
3. Verify the dimension source (caliper-verified, derived from caliper measurement, or assumed)

```
| Interface | Part A dimension | Part B dimension | Clearance | Source |
```

If any interface has mismatched dimensions (e.g., 12mm shaft in a 12mm bore with no clearance), flag it.

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

---

## Quality gate

After all agents complete, verify:
- No references to the old/replaced mechanism remain in any updated document
- The grounding rule is satisfied: no ungrounded behavioral claims remain. Any design gaps are explicitly flagged, not papered over.
- Rubric A narrative is present and coherent — a reader can understand the mechanism from text alone
- Rubric B constraint chain has no unlabeled arrows or unconstrained parts
- Rubric C direction table has no contradictions or unverified claims
- Rubric D interface table has no zero-clearance or mismatched dimensions
- Rubric E assembly sequence is physically feasible
- Rubric F part count is minimized
