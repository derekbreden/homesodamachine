# Design Synthesis

This document defines the procedure for the synthesis agent. One agent reads the vision, requirements, component datasheets, and any technical research from Step 2A (if it was invoked) and produces a concrete execution plan for the vision.

**This step is not choosing between alternatives.** The vision specifies the interaction. This step produces the minimum viable mechanism description that executes that interaction: what the parts are, how they achieve the vision's specified interaction, what the critical dimensions are, and what the bill of materials is.

**This step does not add features.** The synthesis describes the minimum geometry needed to execute the vision. If a feature is not required by the vision or by the physics of the mechanism, it does not belong in the synthesis.

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
- Flag any conflict between the vision and technical feasibility explicitly — with the proposed minimum modification, not a wholesale redesign
- Include a concrete BOM
- Never cite cost as a deciding factor
