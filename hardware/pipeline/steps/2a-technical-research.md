# Technical Research

This document defines the procedure for technical research agents. Each agent investigates one technical question that must be answered to execute the vision. Multiple agents run in parallel, one per question.

**The vision is the constraint, not the design space.** These agents do not explore alternative approaches to meeting the requirements. The vision describes what the user experiences — the interaction, the form, the feel. The research investigates the technical details needed to make that vision work: forces, dimensions, materials, tolerances, failure modes. If the vision says "the user squeezes two flat surfaces," the research question is "what leverage ratio and travel distance does the squeeze need?" — not "should we use a squeeze, a lever, or a knob?"

---

## How the orchestrator identifies research questions

Read `hardware/vision.md` and `hardware/requirements.md`. For each mechanism being designed, ask: what technical facts must be known to specify this mechanism's geometry? Each fact that isn't already in the repo is a research question.

Examples of good research questions (vision-serving):
- "What is the collet depression force and travel for the John Guest PP0408W?" (needed to design the release plate the vision describes)
- "What are the Kamoer KPHM400 mounting dimensions, vibration characteristics, and tubing routing constraints?" (needed to mount the pumps as the vision describes)
- "What is the cross-sectional profile of a Platypus 2L bag at 1.5L fill under gravity at 35 degrees?" (needed to design the bag cradle the vision describes)

Examples of bad research questions (design-space exploration):
- "What are the pros and cons of threaded rod vs cam lever vs spring detent for collet release?" (the vision already specifies squeeze-release)
- "Should the cartridge use rails, a bayonet mount, or a drop-in cradle?" (the vision already specifies rails)

---

## Agent prompt must include

- Path to `hardware/requirements.md` and `hardware/vision.md`
- All known physical constraints (envelope, forces, materials, interfaces)
- The specific technical question the research must answer
- The relevant section of the vision that this question serves — so the agent understands WHY this question matters and what design decision it supports
- Instruction to save the document to the exact file path
- Instruction to commit and push

## Agent prompt must NOT include

- Instruction to propose or evaluate alternative approaches — the approach is set by the vision
- Instruction to make recommendations about which mechanism to use — that framing implies the mechanism is undecided

## Quality gate

Each research document must:
- Answer the specific technical question completely
- Include specific dimensions, materials, and sourcing where applicable
- Address failure modes and concerns relevant to the vision's specified approach
- Connect findings back to the vision: "this means the release plate needs X mm of travel" or "this means the cradle profile should follow this curve"
- Be saved to the correct path
