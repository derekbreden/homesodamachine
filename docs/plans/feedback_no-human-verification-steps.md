---
name: No human verification steps in build sequences
description: Build sequences should contain only design deliverables, never "print and test" or "verify" steps
type: feedback
---

Do not include human verification steps (e.g. "print and test", "verify alignment", "dry fit") in build sequences. Every step should be a design deliverable — a STEP file or a geometry change.

**Why:** The user is constantly checking everything in parallel with the design work. Explicit verification steps both understate what the user is actually doing (they check far more than one thing) and overstate when work should pause (which is never). Including them implies work should block on the user's verification, which it should not.

**How to apply:** When writing or updating build sequences, only include steps that produce a design artifact. If a step's verb is "print", "test", "verify", "check", or "dry fit", it doesn't belong in the sequence.
