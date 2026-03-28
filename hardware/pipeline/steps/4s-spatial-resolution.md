# Spatial Resolution

This document defines the procedure for the spatial resolution agent (Step 4s). This agent takes a single sub-component (from Step 4d) or a single part (if no decomposition was needed) and resolves every multi-frame spatial relationship into concrete coordinates in the sub-component's own reference frame. It does not specify parts (that's 4b's job) and it does not explore alternatives (that was 4a's job). It does one thing: pre-compute the geometry so that no downstream agent ever needs to reason about more than one reference frame at a time.

**Why this step exists.** CadQuery generation agents produce correct geometry when every dimension is a concrete number in the part's own coordinate system. They fail when they must derive dimensions from spatial relationships that span reference frames — converting a 35-degree enclosure mounting angle into a bag cross-section profile, or figuring out where a pump bracket's mounting holes land on a tray that sits at a specific position inside a shell. This step does that conversion once, correctly, so that all downstream work is single-frame.

**Scope.** This step runs once per sub-component (or once per part if Step 4d passed through). When a part was decomposed, each sub-component gets its own spatial resolution document. The sub-component's reference frame is defined in the decomposition document — this step resolves all external spatial relationships into that frame.

---

## What the agent must produce

A **spatial resolution document** for the mechanism being designed. This document contains:

### 1. System-level placement

Where does this mechanism live inside the product? State the position and orientation of the mechanism's reference frame relative to the enclosure (or whatever the parent assembly is), using the coordinate system from `hardware/vision.md` and `hardware/requirements.md`.

```
Mechanism: Bag Frame (lower)
Parent: Enclosure interior
Position: left wall, 140mm from bottom, 60mm from front
Orientation: rotated 35° about the X axis (width axis)
```

This section exists for context only. Downstream agents do not use it directly — they use the resolved dimensions below.

### 2. Part reference frames

For every part in the mechanism, define its local coordinate system. Each part is modeled in this frame — flat on the build plate, oriented for printing.

```
Part: Lower Cradle
  Origin: lower-left-front corner
  X: width, 0..180mm
  Y: length (uphill to downhill), 0..250mm
  Z: height, 0..18mm
  Print orientation: flat, XY plane on build plate
  Installed orientation: rotated 35° about X, mounted on enclosure rail
```

### 3. Derived geometry

This is the core output. For every geometric property that depends on the mechanism's spatial context (gravity direction, mating part positions, fluid behavior, tube routing), resolve it into concrete numbers in the part's local frame.

**Cross-sectional profiles:** If the part's internal shape depends on physics (gravity, fluid fill, material drape), provide the profile as a coordinate table or mathematical description in the part's local frame.

```
Bag cross-section at Y=125 (mid-length), derived from:
  - Platypus 2L bag: 190mm wide, 0.15mm PE/nylon film
  - Fill level: 1.5L in a 2L bag
  - Gravity acts at 35° to the part's Z axis (because the part mounts at 35°)
  - Lenticular profile with R=341mm, sag=7mm at center

Profile (X, Z) in part-local frame, sampled at 10mm intervals:
  X=5:   Z_floor=1.2  Z_ceiling=27.0
  X=25:  Z_floor=1.2  Z_ceiling=25.5
  X=45:  Z_floor=1.2  Z_ceiling=24.0
  X=65:  Z_floor=1.2  Z_ceiling=23.0
  X=85:  Z_floor=1.2  Z_ceiling=22.5  (center, max sag)
  ... (mirror for X>85) ...
```

**Interface positions:** For every point where this part touches another part, provide the position and geometry of the interface in the part's local frame.

```
Interface: Enclosure mounting rail (left side)
  Part-local position: X=-3, Z=5..9, full Y length
  Tongue cross-section: 3mm protrusion (+X), 4mm tall (Z)
  Mating feature: horizontal rail on enclosure interior wall
  Derived from: enclosure rail at 35° in system frame → horizontal in part frame
```

**Routing paths:** If tubes, wires, or other flexible elements pass through or near the part, provide their path in the part's local frame.

```
Tubing exit path:
  Enters part at: Y=247, X=90, Z=9
  Exits enclosure at: (system frame position, for reference only)
  Clearance required: 15mm radius semicircle at exit point
```

### 4. Transform summary

A compact reference showing how to convert between frames. This is for verification — downstream agents shouldn't need it, but the orchestrator can use it to check the spatial resolution is self-consistent.

```
Part frame → System frame:
  Rotate 35° about X (part X = system X)
  Translate to (system_x, system_y, system_z)

Verification: part-local (0, 0, 0) maps to system (60, 140, 200) ✓
Verification: part-local Z-up maps to system (0, -sin35°, cos35°) ✓
```

---

## Agent prompt must include

- Path to `hardware/requirements.md` and `hardware/vision.md`
- Path to the conceptual architecture document (4a output)
- Path to the decomposition document (4d output) — identifies which sub-component this agent is resolving, its reference frame, and its interface boundaries
- Path to all research documents that contain physical measurements (bag geometry, off-the-shelf part dimensions, etc.)
- Path to the decision document (for context on the chosen approach)
- All known physical properties that affect geometry derivation: gravity direction relative to the installed part, fluid fill levels, material properties of flexible elements, etc.
- Instruction to resolve EVERY spatial relationship into the part's local frame — no "the agent will figure out the angle" hand-offs
- Instruction to provide cross-sectional profiles as coordinate tables when the shape depends on physics, not just as prose descriptions
- **Instruction NOT to specify parts or features** — this step produces geometry inputs for the parts specification step, not the specification itself

---

## Quality gate

The spatial resolution document must:

1. **Every number is in a named reference frame.** No orphan dimensions. Every coordinate states which part's frame it belongs to.
2. **No downstream derivation required.** A reader should be able to extract every dimension needed for parts.md without performing any trigonometry, coordinate transforms, or physics calculations. If reading the document requires doing math to figure out a dimension, the document is incomplete.
3. **Cross-sectional profiles are tabulated, not described.** "Gently concave" is not a spatial resolution. A table of (X, Z) coordinates at 10mm intervals is.
4. **Interfaces are specified from both sides.** Each interface lists the position in the part's local frame AND names the mating feature on the other part, so the specification agent can verify consistency.
5. **Transform summary is self-consistent.** The forward and inverse transforms produce correct round-trip results for at least 3 test points (origin, one corner, one interface point).

---

## What this step does NOT do

- **Does not specify parts.** No feature lists, no material selections, no assembly sequences. That is Step 4b.
- **Does not explore alternatives.** The concept is settled. This step resolves the geometry of the chosen concept.
- **Does not generate CadQuery.** No code. Only dimensioned geometry in a structured document.
- **Does not handle simple 2.5D parts.** If the mechanism is entirely contained in a single reference frame with no physics-dependent profiles and no angled mounting (e.g., a flat plate with holes), this step's output is trivial: "Part frame = system frame, no transforms needed, no derived geometry." The agent should state this and move on — do not manufacture complexity where none exists.
