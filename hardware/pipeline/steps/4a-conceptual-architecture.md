# Conceptual Architecture

This document defines the procedure for the conceptual architecture agent (Step 4a). This agent explores the design space freely and settles on one concept. It is explicitly separate from the detailed specification step because exploring and specifying are fundamentally different tasks — combining them causes exploration to consume the agent's context window, leaving specification truncated.

---

## Scope freedom

The agent designing a mechanism is not limited to the mechanism's own parts. If the product values demand it, the agent may and should modify any interfacing part — the shell, walls, panels, other sub-assemblies — to achieve the right design. A mechanism that fits awkwardly into an unchanged shell is worse than a mechanism that reshapes the shell to make the whole product feel unified. When the agent modifies other parts, it must update those parts' documents too.

## What the concept document must address

1. **Piece count and split strategy** — how many pieces, where do they split, why
2. **Join methods** — how the pieces connect (snap-fit, screws, magnets, etc.)
3. **Seam placement** — where are the seams and how are they treated
4. **User-facing surface composition** — what does the user see and touch, visual hierarchy
5. **Design language** — surface finish, corner treatment, material, what makes this a product
6. **Service access strategy** — how are internals accessed, tiered by frequency
7. **Manufacturing constraints** — print bed limits, orientation, material selection

## Agent prompt must include

- Path to `hardware/requirements.md` and `hardware/vision.md`
- Path to the synthesis document
- Path to the design pattern research (`planning/research/design-patterns.md`)
- Printer specs and materials are in `hardware/requirements.md`. **The agent must not assume, infer, or use "typical" values for any manufacturing constraint.**
- All known physical constraints (dimensions, what goes inside)
- Instruction to explore freely — try ideas, discard dead ends, show the reasoning
- Instruction to settle on ONE concept and summarize it clearly at the end
- **Instruction NOT to apply the full rubric suite** — that happens in the detailed specification step

## Quality gate

The concept document must:
- Clearly state what the design IS (not just what it isn't or what was considered)
- Address all 7 topics listed above
- Be free of unresolved contradictions (e.g., a piece that doesn't fit the print bed)
- Be concise enough that the specification agent can read it without losing context

## Orchestrator checkpoint

The orchestrator (or user) reviews the concept before launching the detailed specification step. This is the natural point for design direction feedback — much cheaper to redirect here than after a full parts.md is written.
