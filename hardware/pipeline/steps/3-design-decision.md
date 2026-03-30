# Design Synthesis

This document defines the procedure for the synthesis agent. One agent reads the vision, requirements, component datasheets, and any technical research from Step 2A (if it was invoked) and produces a concrete execution plan for the vision.

**This step is not choosing between alternatives.** The vision specifies the interaction. This step produces the minimum viable mechanism description that executes that interaction: what the parts are, how they achieve the vision's specified interaction, what the critical dimensions are, and what the bill of materials is.

**This step does not add features.** The synthesis describes the minimum geometry needed to execute the vision. If a feature is not required by the vision or by the physics of the mechanism, it does not belong in the synthesis.

**Parts are designed iteratively. The first version of any part is the simplest shape that occupies the correct space. Retention, joinery, and interfaces with parts that don't exist yet are added in later rounds — not anticipated in the first.**

**Start from the simplest possible shape.** For every part, begin with the simplest geometry that could work — a flat plate, a rectangular box, a cylinder. Then ask: does this part fail at its job in this shape? If not, that is the geometry. Every additional surface, wall, rib, channel, or feature beyond the starting shape must be justified by a specific, quantified failure that would occur without it. "Structural rigidity" is not a justification — "the plate deflects X mm under Y N of pump load, exceeding the Z mm clearance to the adjacent part" is. If the failure cannot be quantified, the feature is not justified.

**Only design what is in scope for this run.** The orchestrator's scoping statement says what is being designed. If retention, joinery, or an interface with a part that doesn't exist yet is out of scope, do not include it in the synthesis. A flat panel with no retention features is a correct output.

---

## Agent prompt must include

- Path to `hardware/requirements.md` and `hardware/vision.md`
- File paths to component datasheets in the repo (off-the-shelf part dimensions, measurements)
- File paths to any Step 2A technical research documents (if Step 2A was invoked)
- Instruction to synthesize the minimum viable mechanism: combine the vision, requirements, and technical findings into one coherent mechanism description that executes the vision with the fewest parts and simplest geometry
- Instruction to flag conflicts: if the technical research reveals that some aspect of the vision is mechanically infeasible (e.g., the required force exceeds what a user can comfortably apply), state the conflict clearly and propose the minimum modification to the vision's interaction that resolves it. Do not silently replace the vision with a different approach.
- Instruction to include a bill of materials
- Instruction to note open questions — technical details that weren't fully resolved and that the concept/specification steps will need to address

## Quality gate

The synthesis must:
- Execute the vision's specified interaction, not propose an alternative
- Incorporate specific findings from technical research and component datasheets (forces, dimensions, travel distances) into the mechanism description
- Describe the minimum geometry that achieves the vision — no features beyond what the vision requires or the physics demands
- Every surface, wall, or feature beyond the simplest starting shape has an explicit, quantified justification. "Adds rigidity" or "provides structure" without numbers is not sufficient.
- Flag any conflict between the vision and technical feasibility explicitly — with the proposed minimum modification, not a wholesale redesign
- Include a concrete BOM
- Never cite cost as a deciding factor
