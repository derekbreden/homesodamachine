# Technical Research

This document defines the procedure for technical research agents. Each agent investigates one candidate mechanism or approach (e.g., "threaded rod" vs "cam lever" vs "spring detent"). Multiple agents run in parallel, one per approach.

---

## Agent prompt must include

- Path to `hardware/requirements.md` and `hardware/vision.md`
- All known physical constraints (envelope, forces, materials, interfaces)
- The specific question the research must answer
- Instruction to save the document to the exact file path
- Instruction to commit and push

## Quality gate

Each research document must:
- Cover the specific question completely
- Include specific dimensions, materials, and sourcing where applicable
- Address failure modes and concerns
- Be saved to the correct path
