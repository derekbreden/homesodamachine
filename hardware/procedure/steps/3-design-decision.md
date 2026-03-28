# Design Decision

This document defines the procedure for the decision agent. One agent reads ALL research documents (technical and design pattern) and makes a recommendation.

---

## Agent prompt must include

- Path to `hardware/requirements.md` and `hardware/vision.md`
- File paths to every research document, **including the design pattern research** (`planning/research/design-patterns.md`)
- Instruction to read the design pattern research first, before evaluating technical candidates — the patterns should inform what "good" looks like
- Decision criteria in priority order: UX first, then mechanical feasibility, then simplicity, then durability adequacy. Cost is last and irrelevant.
- Instruction to evaluate each candidate against the design patterns: does this approach enable product-surface integration, or does it result in bolted-on mechanisms?
- Instruction to make a clear recommendation with rationale
- Instruction to include a bill of materials
- Instruction to note what would change the recommendation

## Quality gate

The decision must:
- Explicitly rank alternatives on UX first
- Never cite cost as a deciding factor
- Only reject a UX-superior approach if it is mechanically infeasible
- Include a concrete BOM
