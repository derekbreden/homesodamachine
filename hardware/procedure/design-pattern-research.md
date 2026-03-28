# Design Pattern Research

This document defines the procedure for the design pattern research agent. This agent studies how existing consumer products solve the same interaction problem. The goal is exposure — the agent (and the decision-maker downstream) must understand the landscape of real-world solutions before choosing an approach.

Without this exposure, agents default to "functional but bolted-on" designs. With it, they discover patterns like recessed dials, flush-mounted controls, integrated surfaces, and snap-fit assemblies that make a product feel unified.

---

## Agent prompt must include

- Path to `hardware/requirements.md` and `hardware/vision.md`
- A description of the interaction being designed (what the user does, what the mechanism achieves) — but NOT the current design or any candidate solution. The agent must research patterns without anchoring to an existing approach.
- Instruction to search for and study how shipped consumer products (appliances, electronics, automotive, medical devices) solve the same or analogous interaction problem
- Instruction to focus on products known for exceptional industrial design (e.g., how does a washing machine handle a recessed program dial? How does an oven handle a flush-mounted temperature knob? How does a car handle a twist-lock fuel cap?)
- Instruction to document specific design patterns found, with emphasis on:
  - How the mechanism integrates with the product surface (flush, recessed, proud, hidden)
  - How the product communicates state and affordance without text (icons, detent feel, visual indicators)
  - How assembly/disassembly is handled (snap-fit, living hinges, captive fasteners)
  - How the product looks and feels as a unified object rather than an assembly of parts
- Instruction to save the document to `planning/research/design-patterns.md`
- Instruction to commit and push

## Agent prompt must NOT include

- The current design, existing parts.md, or any candidate solution — the research must be unbiased by existing approaches
- Instruction to evaluate or compare against the current design — that evaluation belongs in the decision step

## Quality gate

The design pattern research must:
- Reference at least 3 real shipped products by name
- Describe specific geometric/mechanical details of how each product solves the interaction (not just "it looks nice")
- Connect the patterns back to the product values — which patterns serve UX? Which create product unity?
