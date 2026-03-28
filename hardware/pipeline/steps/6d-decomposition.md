# Sub-Component Decomposition

This document defines the procedure for the decomposition agent (Step 6d). This agent reads a part's specification and decides whether to split it into sub-components that can each be generated independently by a CadQuery agent working on a simpler problem. It then writes a spec for each sub-component and a composition spec that tells the composition agent how to combine them.

**Why this step exists.** CadQuery generation agents produce reliable geometry for 2.5D problems — extrude-and-cut from a single direction, or revolved profiles around a single axis. They struggle with parts that combine multiple geometric paradigms: a plate with precision bores AND a strut with helical threads AND guide pins, all in one solid. By decomposing the part into sub-components that are each 2.5D, we let each generation agent work within its competence. The composition agent then combines them with translations and boolean unions — a mechanical task, not a spatial reasoning task.

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

When passing through, the agent writes: "This part is a single geometric paradigm. No decomposition needed. Proceed to Step 6g with the full parts.md." The pipeline then runs a single CadQuery agent as in the current Step 6.

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

### 2. Sub-component specifications

For each sub-component:

**Identity:**
- Name (e.g., "Sub-A: Plate Body")
- Which features from parts.md belong to this sub-component (by name or feature number)

**Reference frame:**
- The sub-component's own coordinate system
- Origin, axis meanings, envelope

**Geometry spec:**
- All dimensions needed to build this sub-component, extracted from parts.md
- Interface face(s): the surface(s) where this sub-component will join others, with exact position and shape

**What the CadQuery agent receives:**
- The sub-component spec (this section)
- The relevant portions of parts.md
- The STEP generation standards document
- NO information about other sub-components' internal geometry — only the interface face

### 3. Composition specification

How to combine the sub-components into the final solid:

**For each sub-component:**
- The transform to apply: translation vector and/or rotation to align it with the final part's coordinate system
- The order of operations (which gets built first, which gets unioned next)

**Interface treatments:**
- For each joint between sub-components: what operations (if any) are needed at the boundary? Fillets, chamfers, or nothing (flush join)?

**Boolean operation notes:**
- Any known OCCT sensitivity to operation order (e.g., "union simple cylinders before complex swept geometry")
- Whether cuts from one sub-component affect another (e.g., "the plate's bores do not extend into the strut")

**Validation after composition:**
- The full validation suite runs on the composed solid
- Additional probes at interface boundaries to verify clean joins (no gaps, no self-intersections)

---

## Example: Release Plate with Integral Strut

```
DECOMPOSITION: Release Plate + Strut

RATIONALE:
  Plate body is extrude-and-cut (2.5D prismatic).
  Strut is revolved + helical sweep (rotational).
  Interface: single circular face at plate back face center.

SUB-COMPONENT A: Plate Body
  Features from parts.md: plate body, guide pin pads, guide pins,
    stepped bores (x4), bore chamfers, tube chamfers
  Frame: origin at plate bottom-left-front, X=width, Y=depth, Z=height
  Envelope: 59 x 6 x 47 mm (plus pad/pin protrusions)
  Interface face: circle D=12mm centered at (29.5, 6.0, 23.5) on back face (Y=6)
  CadQuery paradigm: box + cuts + cylinder unions. No sweeps, no lofts.

SUB-COMPONENT B: Strut with Threads
  Features from parts.md: smooth section, thread core, thread helices, end chamfer
  Frame: origin at plate-end center (0,0,0), Y along strut axis
  Envelope: D=12mm x L=130mm
  Interface face: circle D=12mm at Y=0
  CadQuery paradigm: cylinder + helical sweep. No prismatic features.

COMPOSITION:
  1. Build A (plate body with bores, pins, pads)
  2. Build B (strut with threads)
  3. Translate B by (29.5, 6.0, 23.5) — aligns B.Y=0 with A back face center
  4. Union A + B
  5. No interface treatment (flush cylindrical joint, same diameter)
  6. Validate composed solid: full rubric suite + interface boundary probes

BOOLEAN NOTES:
  Union guide pins and pads BEFORE cutting bores (per OCCT sensitivity
  observed in prior builds). Union strut AFTER bore cuts.
```

---

## Agent prompt must include

- Path to the part's `planning/parts.md` (the full specification)
- Path to `hardware/pipeline/steps/6-step-generation.md` (so the agent understands what the generation agents can and cannot do)
- Path to `hardware/requirements.md` (printer constraints that may affect decomposition — e.g., a sub-component that exceeds build volume is a bad split)
- Instruction to decide first: decompose or pass through?
- Instruction that each sub-component must be a self-contained 2.5D problem — if a sub-component still requires multi-paradigm CadQuery, the split is wrong
- Instruction to keep the number of sub-components minimal — split only at natural geometric boundaries, not arbitrarily

---

## Quality gate

The decomposition document must:

1. **Each sub-component is a single geometric paradigm.** If a sub-component still requires both prismatic and rotational operations, the decomposition is insufficient — split further or reconsider the boundary.
2. **Interface faces are fully specified.** Every joint between sub-components has an exact position, shape, and size. The composition agent must not need to infer anything about where parts meet.
3. **No feature is orphaned.** Every feature from parts.md appears in exactly one sub-component specification. The decomposition agent must account for all features.
4. **Composition is mechanical.** The composition spec contains only translations, rotations, unions, and simple interface treatments (fillets, chamfers). If the composition requires generating new geometry beyond interface treatments, the decomposition boundary is in the wrong place.
5. **Simple parts pass through.** If the agent decomposes a part that a single CadQuery agent could handle easily, that is over-engineering. The decomposition adds pipeline complexity — it must earn its keep.
