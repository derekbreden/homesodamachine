# Design Synthesis

This document defines the procedure for the synthesis agent. One agent reads ALL research documents (technical and design pattern) and synthesizes them into a concrete execution plan for the vision.

**This step is not choosing between alternatives.** The vision specifies the interaction. The research answers the technical questions that interaction raises. This step combines those answers into a coherent plan: what the mechanism looks like, how it achieves the vision's specified interaction, what the critical dimensions are, and what the bill of materials is.

---

## Agent prompt must include

- Path to `hardware/requirements.md` and `hardware/vision.md`
- File paths to every research document, including the design pattern research (`planning/research/design-patterns.md`)
- Instruction to read the design pattern research first — the UX details discovered there set the bar for what "good" looks like in the execution plan
- Instruction to synthesize, not choose: combine the technical findings and design pattern findings into one coherent mechanism description that executes the vision
- Instruction to flag conflicts: if the technical research reveals that some aspect of the vision is mechanically infeasible (e.g., the required force exceeds what a user can comfortably apply), state the conflict clearly and propose the minimum modification to the vision's interaction that resolves it. Do not silently replace the vision with a different approach.
- Instruction to include a bill of materials
- Instruction to note open questions — technical details that the research didn't fully resolve and that the concept/specification steps will need to address

## Quality gate

The synthesis must:
- Execute the vision's specified interaction, not propose an alternative
- Incorporate specific findings from the technical research (forces, dimensions, travel distances) into the mechanism description
- Incorporate UX guidance from the design pattern research (feedback cues, surface treatments, tolerance targets) into the mechanism description
- Flag any conflict between the vision and technical feasibility explicitly — with the proposed minimum modification, not a wholesale redesign
- Include a concrete BOM
- Never cite cost as a deciding factor
