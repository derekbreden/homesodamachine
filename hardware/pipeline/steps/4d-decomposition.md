# Sub-Component Decomposition

This document defines the procedure for the decomposition agent (Step 4d). This agent reads the conceptual architecture for a single part and decides whether to split it into sub-components that can each be designed, drawn, and generated independently as a 2.5D problem. It then writes a brief spec for each sub-component and a composition spec that tells the composition agent (Step 6c) how to combine them.

**Why this step exists — and why it happens early.** CadQuery generation agents produce reliable geometry for 2.5D problems. But if we wait until after parts specification and drawings to decompose, the parts specification agent has already struggled with the full 3D complexity — and the drawings may encode a monolithic geometry that doesn't cleanly separate. By decomposing immediately after the concept is settled, every subsequent step — spatial resolution, parts specification, engineering drawings, CadQuery generation — works on a simpler sub-problem. The decomposition is the fan-out point for the rest of the pipeline.

---

## Decision: decompose or pass through

Not every part needs decomposition. The agent's first job is to decide.

**Decompose when:**
- The part combines features from fundamentally different geometric paradigms (prismatic + rotational, flat plate + helical sweep, rectilinear body + complex lofted surface)
- A single CadQuery agent would need to use multiple advanced techniques (sweep + loft, or revolve + helix) in the same script
- Features in different regions of the part have no geometric dependencies on each other (the strut's threads don't affect the plate's bore geometry)

**Pass through when:**
- The part is a single geometric paradigm (all extrude-and-cut, or all revolved profiles)
- Features are tightly interdependent (a bore pattern that spans a body joint)
- The part is small enough that one agent can handle it without complex operations
- Decomposition would create more problems at the composition boundary than it solves

When passing through, the agent writes: "This part is a single geometric paradigm. No decomposition needed." The pipeline then runs steps 4s → 4b → 5 → 6g for the part as a single unit, with no composition step.

---

## Input

The decomposition agent reads:

1. **The conceptual architecture document** (Step 4a output) — this is the primary input. The concept describes what the part does, its features, and how it fits into the mechanism.
2. **`hardware/requirements.md`** — printer constraints, build volume, material properties
3. **`hardware/vision.md`** — product values and product architecture
4. **`hardware/pipeline/steps/6-step-generation.md`** — so the agent understands what CadQuery agents can and cannot do (the capabilities that define what "2.5D" means in practice)

The agent does NOT read a parts.md — that document doesn't exist yet. The decomposition is based on the conceptual architecture's description of the part's geometry and features, not on detailed dimensions.

---

## What the decomposition document must contain

### 1. Decomposition rationale

One paragraph: why is this part being split, and what is the geometric paradigm of each sub-component?

```
The release plate with integral strut combines two geometric paradigms:
(A) a prismatic plate with precision stepped bores — an extrude-and-cut problem, and
(B) a cylindrical strut with trapezoidal helical threads — a rotational/sweep problem.
These share a single interface point (the strut's base at the plate's back face center)
but have no geometric interdependence beyond that joint.
```

### 2. Sub-component descriptions

For each sub-component:

**Identity:**
- Name (e.g., "Sub-A: Plate Body")
- Which features from the concept belong to this sub-component

**Geometric paradigm:**
- What kind of CadQuery work this sub-component requires (extrude-and-cut, revolve, sweep, loft)
- Confirmation that it is a single paradigm

**Interface boundary:**
- Where this sub-component meets other sub-components — described in enough detail for the spatial resolution and parts specification agents to work with, but not yet fully dimensioned (that's 4s and 4b's job)

Note: Unlike the previous version of this step (which ran after parts.md and extracted dimensions), the decomposition at this stage produces *descriptions*, not *dimensions*. The dimensions come from 4s (spatial resolution) and 4b (parts specification), which run per-sub-component after this step.

### 3. Composition specification

How to combine the sub-components into the final solid. At this stage, the composition spec is directional rather than fully dimensioned:

**For each sub-component:**
- Where it attaches to the other sub-components (conceptually — exact transforms come after 4b)
- The expected interface geometry (circular face, rectangular face, etc.)

**Interface treatments:**
- For each joint between sub-components: what operations (if any) are needed at the boundary? Fillets, chamfers, or nothing (flush join)?

**Boolean operation notes:**
- Any known OCCT sensitivity to operation order
- Whether cuts from one sub-component affect another

This composition spec is refined after Step 4b, when exact dimensions are known. The composition agent (Step 6c) reads both this document and the parts.md files to produce the final composition script.

---

## Example: Release Plate with Integral Strut

```
DECOMPOSITION: Release Plate + Strut

RATIONALE:
  Plate body is extrude-and-cut (2.5D prismatic).
  Strut is revolved + helical sweep (rotational).
  Interface: single circular face at plate back face center.

SUB-COMPONENT A: Plate Body
  Features: plate body, guide pin pads, guide pins,
    stepped bores (x4), bore chamfers, tube chamfers
  Paradigm: box + cuts + cylinder unions. No sweeps, no lofts.
  Interface: circular face (D=strut diameter) at back face center

SUB-COMPONENT B: Strut with Threads
  Features: smooth shaft section, thread core, thread helices, end chamfer
  Paradigm: cylinder + helical sweep. No prismatic features.
  Interface: circular face (D=strut diameter) at plate-end

COMPOSITION:
  B attaches to A at A's back face center, extending away from the plate.
  Union. No interface treatment needed (flush cylindrical joint).
  Union guide pins and pads BEFORE cutting bores (OCCT sensitivity).
  Union strut AFTER bore cuts.
```

---

## How decomposition affects downstream steps

After decomposition, the pipeline fans out. Each sub-component gets its own pass through 4s → 4b → 5 → 6g, then the results converge at 6c:

```
4d (decompose into A, B)
  │
  ├── 4s-A (spatial resolution for A) → 4b-A (parts.md for A) → 5-A (drawing) → 6g-A (CadQuery)
  │
  ├── 4s-B (spatial resolution for B) → 4b-B (parts.md for B) → 5-B (drawing) → 6g-B (CadQuery)
  │
  └── 6c (compose A + B into final STEP)
```

Each sub-component's parts.md is a self-contained document. Each sub-component's drawing shows only that sub-component. Each CadQuery agent sees only its sub-component's spec. The composition agent is the only agent that sees all sub-components together.

---

## Agent prompt must include

- Path to the conceptual architecture document (4a output)
- Path to `hardware/pipeline/steps/6-step-generation.md` (so the agent understands what the generation agents can and cannot do)
- Path to `hardware/requirements.md` (printer constraints that may affect decomposition — e.g., a sub-component that exceeds build volume is a bad split)
- Path to `hardware/vision.md`
- Instruction to decide first: decompose or pass through?
- Instruction that each sub-component must be a self-contained 2.5D problem — if a sub-component still requires multi-paradigm CadQuery, the split is wrong
- Instruction to keep the number of sub-components minimal — split only at natural geometric boundaries, not arbitrarily
- Instruction to describe, not dimension — exact dimensions come from 4s and 4b

---

## Quality gate

The decomposition document must:

1. **Each sub-component is a single geometric paradigm.** If a sub-component still requires both prismatic and rotational operations, the decomposition is insufficient — split further or reconsider the boundary.
2. **Interface boundaries are clearly described.** Every joint between sub-components has a described geometry (circular face, rectangular face, flush surface) and location (back face center, top edge, etc.). Exact dimensions are not required at this stage but the topology must be clear.
3. **No feature is orphaned.** Every feature from the concept appears in exactly one sub-component. The decomposition agent must account for all features.
4. **Composition is mechanical.** The composition spec describes only translations, rotations, unions, and simple interface treatments (fillets, chamfers). If the composition requires generating new geometry beyond interface treatments, the decomposition boundary is in the wrong place.
5. **Simple parts pass through.** If the agent decomposes a part that a single CadQuery agent could handle easily, that is over-engineering. The decomposition adds pipeline complexity — it must earn its keep.
