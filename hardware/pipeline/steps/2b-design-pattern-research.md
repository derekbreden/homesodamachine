# Design Pattern Research

This document defines the procedure for the design pattern research agent. This agent studies how existing consumer products achieve the specific UX qualities that the vision demands. The goal is to find concrete geometric and mechanical details that make those qualities real — not to survey alternative approaches.

Without this research, agents produce mechanisms that function but don't feel right. With it, they discover the specific details — surface transitions, detent profiles, gap tolerances, feedback cues — that separate "it works" from "it feels like a product."

---

## How the orchestrator frames the research

Read the vision. Identify the specific UX qualities the mechanism must achieve. Frame the research around those qualities, not around the interaction category.

Examples of good framing (vision-anchored):
- "How do consumer products create satisfying squeeze-to-release interactions? What makes the squeeze feel deliberate and the release feel clean? What geometric details (travel distance, force curve, surface texture, audible/tactile feedback) produce that satisfaction?"
- "How do consumer products hide complex internal mechanisms behind minimal external surfaces? When the user sees only two flat surfaces and a seam, what's happening inside that makes the exterior feel simple?"
- "How do consumer products create confidence that a slide-in module is fully seated? What feedback (click, flush surface, resistance curve) tells the user 'you're done'?"

Examples of bad framing (approach-exploring):
- "How do consumer products solve module insertion and removal?" (too broad — explores alternatives to the vision's specified approach)
- "What locking mechanisms do appliances use?" (surveys a design space instead of investigating the vision's specific interaction)

---

## Agent prompt must include

- Path to `hardware/requirements.md` and `hardware/vision.md`
- The specific UX qualities being researched — extracted from the vision, stated as questions about how to achieve them
- The relevant section of the vision that describes the user's interaction — so the agent understands what the product must feel like
- Instruction to search for and study shipped consumer products that achieve the same UX qualities, even if the products serve completely different functions
- Instruction to focus on the geometric and mechanical details that produce the quality: dimensions, surface finishes, force profiles, tolerances, material choices. "It feels premium" is not a finding. "The squeeze travel is 8mm with a 15N force peak at 6mm followed by a sharp drop at full engagement" is.
- Instruction to save the document to `planning/research/design-patterns.md`
- Instruction to commit and push

## Agent prompt must NOT include

- Instruction to survey alternative approaches to the interaction — the interaction is specified by the vision
- Instruction to compare the vision's approach against other approaches — that implies the approach is undecided

## Quality gate

The design pattern research must:
- Reference at least 3 real shipped products by name
- Describe specific geometric/mechanical details that produce the UX quality being studied (not just "it looks nice" or "it feels premium")
- Connect the findings to actionable design guidance: "this suggests the squeeze travel should be at least X mm" or "this suggests the seam gap should be under Y mm for the mechanism to read as hidden"
- Stay anchored to the vision's specified interaction — findings about alternative interaction types are off-topic
