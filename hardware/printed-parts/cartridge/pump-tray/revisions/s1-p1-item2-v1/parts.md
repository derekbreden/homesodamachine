# Pump Tray — Parts Specification

**Season 1, Phase 1, Item 2**
**Pipeline step:** 4b
**Coordinate system source:** spatial-resolution.md

---

## Part Summary

| Property | Value |
|----------|-------|
| Part name | Pump Tray |
| Piece count | 1 |
| Outer dimensions | 137.2mm (X) × 3.0mm (Y) × 68.6mm (Z) |
| Features | Plate body + 2× motor bores + 8× M3 clearance holes |
| Print orientation | Front face (XZ plane, Y=0) down on build plate |
| Material | PLA or PETG |
| Supports required | None |
| User-facing | No |

---

## Coordinate System

Origin: bottom-left corner of the front face of the plate.

```
X: width axis — left to right, 0..137.2mm
Y: thickness axis — front to back through the plate, 0..3.0mm
    Y=0: front face (the face the pump bracket contacts)
    Y=3.0mm: back face (the face the motor bodies extend from; the motor/screw-access side)
Z: height axis — bottom to top, 0..68.6mm
```

Print orientation: the front face (XZ plane, Y=0) is placed down on the build plate. Z is up during printing. This matches the installed orientation — no reorientation is needed between print and installation.

---

## Rubric A — Mechanism Narrative

### What the user sees and touches

The user never sees or touches this part. The pump cartridge presents to the user as a black box with a flat front panel, side tracks, and a squeeze mechanism. The pump tray is one of two interior flat plates inside that cartridge. It is inaccessible during normal use. When the user replaces the cartridge (vision.md, Section 4: "the user can remove and replace the pump cartridge"), they are replacing the entire assembly — they handle the cartridge as a unit and never interact with the pump tray individually.

### What moves

Nothing moves on or through this part during normal operation. The pump tray is a stationary structural plate.

The pumps themselves — two Kamoer KPHM400 peristaltic pumps — are bolted to the front face of this plate. Each pump's motor rotates internally when dispensing. No motion is transmitted to the tray.

### What the pump tray does

The pump tray holds both pumps at a fixed position inside the cartridge. Each pump mounts via its metal bracket face flat against the front face of this plate (Y=0). The motor cylinder (35.73mm diameter) passes through the motor bore (37mm diameter) in the plate — the motor cylinder enters from Y=0 (front face) and exits at Y=3.0mm (back face), extending into the space behind the plate. Eight M3 screws are inserted from the motor side (Y=3.0mm side), pass through the 8× 3.3mm clearance holes in the plate, and thread into the pump head on the front (Y=0) side, clamping the bracket against the plate front face.

The motor bore is necessary for screw access: without it, the motor cylinder — which is 35.73mm in diameter — blocks the screwdriver from reaching the screws. The bore clears the motor cylinder out of the screw path, allowing the assembler to insert and tighten all screws from the motor side.

The tube connectors on each pump protrude from the pump front face, forward of the bracket, in the -Y direction (toward the cartridge front panel). The tray does not interact with the tube connectors — they extend freely in front of the plate.

### What constrains the pumps

The bracket-to-plate contact face (Y=0) prevents the pump from moving in the -Y direction (the pump cannot push through the plate). The bracket contacts the front face (Y=0). The motor cylinder passes through the bore from the front (Y=0) and exits at the back (Y=3.0mm). The 8× M3 screws, inserted from the motor side (Y=3.0mm), pass through the 3.3mm clearance holes and thread into the pump head on the front side — clamping force resists movement in +Y (separation), rotation, and lateral shift. The screws are the only fastening mechanism in scope for Phase 1.

DESIGN GAP: The pump tray itself has no retention feature preventing it from sliding out of the cartridge side wall rails. Rail engagement and retention detents are Season 2 and Season 3 work respectively (vision.md, Phase 9, item 29). In Phase 1, the tray sits unsecured inside the cartridge — or is handled as a standalone part before the cartridge walls exist.

### What provides the return force

Not applicable. This part has no actuated or spring-loaded behavior.

### User interaction summary

The user interacts with this part exactly once per pump cartridge lifetime: during cartridge assembly (installing the pumps onto the plate before the cartridge is assembled). The assembly interaction is described under Rubric E.

---

## Rubric B — Constraint Chain

The pump tray is a passive structural element. The constraint chain runs from the pump through the motor bore alignment and screws through the plate:

```
[Pump bracket face]
    | contacts at Y=0 (front face of plate)
    | 68.6mm × 68.6mm flat contact per pump
    v
[Plate front face, Y=0]
    | 2× motor bores (37mm dia, centered on pump motor axis)
    | motor cylinder (35.73mm dia) passes through bore, Y=0 → Y=3.0mm
    | bore provides clearance for screwdriver access from motor side
    v
[Motor side (Y=3.0mm face) — screw insertion point]
    | 8× M3 clearance holes (3.3mm dia, through Y=3.0mm to Y=0)
    | each hole aligned to pump bracket M3 holes (50mm c-c square)
    v
[8× M3 screws]
    | screws inserted from Y=3.0mm side (motor side)
    | screws pass through clearance holes (Y=3.0mm → Y=0)
    | screws thread into pump head at Y=0 (front face side, inside pump)
    | clamp force holds bracket against plate front face
    v
[Pump is stationary relative to plate]
    ^ constrained against -Y motion: plate front face (Y=0 contact surface)
    ^ constrained against +Y motion: M3 screw clamp force
    ^ constrained against lateral (X/Z) motion: M3 screw shear through clearance holes
    ^ constrained against rotation: M3 screw array (4-point pattern)

[Plate itself]
    ^ constrained against lateral motion: Season 2 side wall rails (not in Phase 1)
    ^ constrained against axial motion in cartridge: Season 3 retention detents (not in Phase 1)
    ^ DESIGN GAP: no plate retention in Phase 1 — plate is unsecured in cartridge context
```

Every arrow is labeled. No gap in the screw path — see Rubric D for continuity verification.

---

## Rubric C — Direction Consistency Check

All directional claims converted to axis notation in the pump tray local frame.

| Claim | Direction | Axis | Verified? | Notes |
|-------|-----------|------|-----------|-------|
| Pump bracket contacts front face of plate | Bracket approaches from -Y | -Y | Yes | Bracket rear face sits at Y≈-1.5mm; plate front face is Y=0. Contact at Y=0. |
| Motor cylinder passes through motor bore | Motor cylinder enters at Y=0 (front face), exits at Y=3.0mm (back face) | +Y | Yes | Motor is 35.73mm dia; bore is 37mm dia. Motor passes through the plate, not past it. Center axis parallel to Y. |
| Motor body extends from back face | Motor protrudes in +Y from Y=3.0mm | +Y | Yes | After passing through the bore, the motor body continues in +Y space beyond the plate. |
| Screws inserted from motor side toward pump head | Screw axis travels -Y (Y=3.0mm → Y=0) | -Y | Yes | Screw enters at Y=3.0mm (back/motor face), exits at Y=0.0mm (front face), threads into pump head. Opposite direction from prior incorrect description. |
| Screws thread into pump head | Threads engage at Y=0 (front face side, inside pump head behind bracket) | Y=0 side | Yes | Pump head is on the front (Y=0) side. Threads are internal to pump head. Screws inserted from motor side engage these threads. |
| Tube connectors protrude forward from pump face | Connectors extend in -Y from pump front face | -Y | Yes | Pump front face is forward of bracket. Tube barb protrusion from bracket surface is 34.54mm (geometry-description.md, photo 15). Connectors are fully in -Y space, well clear of the tray. |
| Plate width runs left-to-right | X axis, 0..137.2mm | +X | Yes | Pump 1 occupies X=0..68.6mm; Pump 2 occupies X=68.6..137.2mm. |
| Plate height runs bottom-to-top | Z axis, 0..68.6mm | +Z | Yes | All hole Z coordinates are 9.3mm and 59.3mm, within range. |
| Motor bore axis parallel to Y | Bore axis is Y | Y | Yes | Bore center at X=34.3mm or X=102.9mm, Z=34.3mm. Bore runs Y=0 to Y=3.0mm. |

No contradictions found.

---

## Rubric D — Interface and Path Consistency

### Part 1 — Interface Dimensions

| Interface | Part A | Part A Dimension | Part B | Part B Dimension | Clearance | Source |
|-----------|--------|-----------------|--------|-----------------|-----------|--------|
| Pump bracket hole → plate clearance hole | Pump bracket M3 hole | 3.13mm diameter (caliper, photo 06) | Plate clearance hole | 3.3mm diameter | 0.17mm diametric (0.085mm radial) | Caliper-verified bracket; plate per requirements.md +0.2mm nominal |
| Pump bracket face → plate front face | Bracket rear face (flat) | Nominally flat, ~68.6mm × 68.6mm | Plate front face (Y=0) | Flat, 137.2mm × 68.6mm | 0mm gap (contact fit) | Both are flat surfaces; contact is the functional condition |
| Motor cylinder → motor bore | Motor cylinder OD | 35.73mm (caliper, photo 16) | Bore diameter | 37mm | 1.27mm diametric (0.635mm radial) | Caliper photo 16; bore per vision.md Section 4 Season 1 Phase 1 Item 2 |

Notes:
- The 0.17mm diametric clearance between the bracket M3 hole (3.13mm) and the plate clearance hole (3.3mm) means the screw passes through the bracket hole first with ~0.13mm clearance, then through the plate hole with ~0.3mm clearance (nominal M3 body diameter is ~3.0mm). Both are loose-clearance passes. No binding.
- The plate clearance hole is sized per requirements.md: nominal M3 = 3.0mm, +0.2mm for loose fit = 3.2mm nominal design intent, then 3.3mm as printed due to the hole-shrinkage compensation already applied. The 3.3mm figure in synthesis.md is the compensated diameter.
- The bracket-to-plate contact is a metal-to-plastic face contact. No tolerance stack issue — both faces are flat.
- The 1.27mm diametric clearance in the motor bore (35.73mm motor into 37mm bore) allows the motor cylinder to pass through freely with 0.635mm radial gap on all sides.

### Part 2 — Path Continuity

Eight screw paths, all identical. Verifying one representative path (Hole 1-A at X=9.3mm, Z=59.3mm). Note: screws are inserted from the motor side (Y=3.0mm) and travel toward the front face (Y=0).

| Path | Segment | Start (Y) | Stop (Y) | Diameter / Section | Connects to next? |
|------|---------|-----------|----------|--------------------|-------------------|
| Screw path, hole 1-A | Open space at motor side | Y=3.0mm (back face, motor side) | Y=3.0mm | Open air — screw entry point | Yes — enters plate hole at Y=3.0mm |
| Screw path, hole 1-A | Plate clearance hole | Y=3.0mm (back face) | Y=0mm (front face) | 3.3mm through-hole in plate | Yes — exits into bracket hole region at Y=0 |
| Screw path, hole 1-A | Bracket hole | Y≈0mm (bracket rear face / plate front face) | Y≈-1.5mm (bracket front face) | 3.13mm clearance hole in metal bracket | Yes — exits into pump head thread zone |
| Screw path, hole 1-A | Pump head threads | Y < -1.5mm (inside pump head) | — | M3 threaded bore in pump head | Terminal — screw engages threads here |

Path continuity confirmed: the screw path runs continuously from the motor side (Y=3.0mm) through the plate clearance hole, through the bracket hole, and into the pump head threads at Y=0. No gap, no discontinuity, and no solid material blocking the path. The motor bore (37mm dia) gives the screwdriver access to the plate holes from the motor side — without the bore the 35.73mm motor cylinder would obstruct the screwdriver at holes 1-A, 1-B, 1-C, 1-D (all within the motor cylinder footprint).

Same analysis applies identically to all 8 holes (1-A through 2-D) by symmetry of the hole geometry.

---

## Rubric E — Assembly Feasibility

### Assembly sequence

1. Orient the plate with the front face (Y=0) facing away from the assembler (plate flat, motor side / back face facing the assembler).
2. Insert one pump from the front — motor cylinder (35.73mm dia) passes through the motor bore (37mm dia). Bracket contacts the front face (Y=0). Align the 4 bracket holes to the corresponding 4 plate holes (either Pump 1 pattern or Pump 2 pattern). The bracket is 68.6mm × ~68.6mm; it fits within the half-plate footprint (0..68.6mm or 68.6..137.2mm in X, 0..68.6mm in Z).
3. Insert 4× M3 screws from the motor side (Y=3.0mm side), passing through the plate clearance holes and threading into the pump head on the front (Y=0) side.
   - Hand clearance: the motor bore (37mm dia) is centered on the pump motor axis. The screw holes are at 25mm from the bore center (35.36mm from bore center to hole center, leaving 16.86mm from bore edge to hole center). The motor bore does not obstruct the screw hole positions — the screwdriver reaches each screw hole from the motor side without interference. The minimum edge clearance to the plate edge is 9.3mm on all sides — adequate for a standard screwdriver shaft.
4. Tighten all 4 screws to clamp the pump bracket against the plate front face.
5. Repeat steps 2–4 for the second pump.

### Feasibility check

| Step | Physically feasible? | Notes |
|------|---------------------|-------|
| Insert motor cylinder through bore | Yes | 35.73mm motor into 37mm bore. 1.27mm diametric clearance — slides through without binding. |
| Place bracket against plate front face | Yes | Bracket footprint fits within half the plate. No interference. |
| Align bracket holes to plate holes | Yes | Both patterns are 50mm c-c squares. Alignment is by hole-to-hole visual registration. No keying feature exists in Phase 1. |
| Insert screws from motor side | Yes | Motor side (Y=3.0mm) is fully accessible. The motor bore clears the motor cylinder, and screw holes are 16.86mm from the bore edge — well outside the motor cylinder footprint. No obstruction at any of the 8 hole entries at Y=3.0mm. |
| Reach all screws with driver | Yes | All hole entries are at Y=3.0mm on the motor-side flat face. Minimum edge clearance is 9.3mm. The bore (37mm dia) provides clearance for the motor cylinder — the screwdriver approaches the screw holes from outside the bore, where there is no obstruction. |
| Second pump install after first | Yes | The second pump occupies the other half of the plate. No interference between pump bodies at this stage. |

DESIGN GAP: No keying feature exists to enforce pump bracket orientation (0°/90°/180°/270° rotation). The 50mm × 50mm hole pattern is rotationally symmetric — a pump could be mounted in any of 4 rotational orientations and all holes would align. The correct rotational orientation for tube routing will be determined in Season 2, at which time a keying feature (or documented assembly instruction) will be added. This does not affect Phase 1 — the holes are the deliverable and they are orientation-agnostic.

### Disassembly (for pump replacement)

The pumps are replaced by replacing the entire cartridge (vision.md, Section 4). The pump tray is not individually serviceable. Disassembly of the pump tray itself (removing pumps from the plate) is a manufacturing/repair procedure, not a user procedure. It is the reverse of the assembly sequence: remove 8× M3 screws, slide pumps off plate (motor cylinder withdraws through the bore).

---

## Rubric F — Part Count Minimization

This part is a single flat plate. There are no sub-parts, no joints between printed components, and no reason to split the part.

| Candidate split | Rationale to split? | Decision |
|----------------|---------------------|----------|
| Split plate at X=68.6mm (between pumps) | No. Both halves are permanently co-located, carry identical loads, and have no geometric feature requiring access from inside a closed form. Splitting would create a joint with no benefit and would require a joining feature that adds complexity (Season 3 is where joinery work happens). | One piece. |
| Split plate at any other axis | No. No geometric feature, assembly constraint, or FDM requirement justifies any split. | One piece. |

One piece is correct. No further justification required.

---

## Rubric G — FDM Printability

### Step 1 — Print Orientation

**Front face (XZ plane, Y=0) down on the build plate. Z is up during printing.**

Rationale: The plate is 137.2mm (X) × 68.6mm (Z) × 3.0mm (Y). Printing flat (3.0mm in the Z/build-height axis) gives maximum XY dimensional accuracy for the hole pattern, which is the only critical feature of this part. Holes printed as Z-axis cylinders (axis parallel to the print Z direction) have the best roundness and positional accuracy on an FDM printer.

Alternative orientations considered and rejected:
- Edge-on (137.2mm or 68.6mm in Z): Creates a 3.0mm-wide base on the build plate. At 3.0mm width, the part has low lateral stability during printing. Hole axes would be parallel to the XY plane, degrading hole roundness. No benefit.
- Any other orientation: No improvement over flat-on-build-plate.

The front face (Y=0) is placed down rather than the back face because both faces are functionally equivalent in Phase 1 (no mating features on either face in this phase). No bottom-edge chamfer is required in Phase 1 — the bottom face is not a mating surface at this stage.

### Step 2 — Overhang Audit

| Surface / Feature | Angle from horizontal (build plate = 0°) | Printable? | Resolution |
|------------------|------------------------------------------|------------|------------|
| Front face (Y=0, XZ plane) | 0° — horizontal, on build plate | OK — build plate surface | N/A |
| Back face (Y=3.0mm, XZ plane) | 0° — horizontal, parallel to build plate | OK — top surface, no overhang concern | N/A |
| Left edge (X=0, YZ plane) | 90° — vertical wall | OK — vertical wall, no overhang | N/A |
| Right edge (X=137.2mm, YZ plane) | 90° — vertical wall | OK — vertical wall, no overhang | N/A |
| Bottom edge (Z=0, XY plane) | 90° — vertical wall | OK — vertical wall, no overhang | N/A |
| Top edge (Z=68.6mm, XY plane) | 90° — vertical wall | OK — vertical wall, no overhang | N/A |
| Motor bore cylinder walls (2×, 37mm dia, Y-axis) | 90° — vertical cylinders in stated print orientation | OK — vertical cylinders print without overhang issues | N/A |
| Hole cylinder walls (8× holes, 3.3mm dia, Y-axis) | 90° — vertical cylinders when printed in stated orientation | OK — vertical cylinders print without overhang issues | N/A |
| Hole entry (front face, Y=0) | 0° — coincident with build plate face | OK | N/A |
| Hole exit (back face, Y=3.0mm) | 0° — horizontal top surface | OK | N/A |

No overhangs. No supports required.

### Step 3 — Wall Thickness Check

| Feature | Thickness | Minimum required | Pass? |
|---------|-----------|-----------------|-------|
| Plate body (Y axis) | 3.0mm | 1.2mm (structural per requirements.md) | Yes — 2.5× the structural minimum |
| Material between adjacent hole edges (Pump 1 holes 1-A and 1-B, same Z row) | 59.3 - 9.3 - 3.3 = 46.7mm between outer hole edges | 0.8mm | Yes — large margin |
| Material between inner hole pair (Pump 1 hole 1-B at X=59.3mm and Pump 2 hole 2-A at X=77.9mm) | 77.9 - 59.3 - 3.3 = 15.3mm between outer hole edges | 0.8mm | Yes |
| Material from outermost hole edge to plate edge (all four sides) | 9.3mm center - 1.65mm radius = 7.65mm from plate edge to nearest hole wall | 0.8mm | Yes |
| Material between motor bore edge and nearest screw hole wall | 16.86mm (bore edge to screw hole center) − 1.65mm (screw hole radius) = 15.21mm | 0.8mm | Yes — 19× the minimum |

All walls well above minimum. No violations.

### Step 4 — Bridge Span Check

No unsupported horizontal spans exist in this part. The plate is solid between holes. M3 hole diameters are 3.3mm — the top of each hole spans 3.3mm, well under the 15mm bridge limit. Motor bore diameters are 37mm — the top of each bore spans 37mm. At 3.0mm plate thickness (print height), a 37mm bridge across a through-bore is within normal FDM capability; however, in the stated print orientation (front face down), the motor bore is a vertical cylinder and does not create a bridge span at all. No unsupported bridge exists.

### Step 5 — Layer Strength Check

The pump weight load is static and negligible (under 200g per pump). Load direction is perpendicular to the plate face — this is a bending load across layers. At 3.0mm plate thickness with this load magnitude, layer delamination is not a failure mode. No snap-fit or flex features exist on this part.

---

## Rubric H — Feature Traceability

| Feature | Justification source | Specific reference |
|---------|---------------------|-------------------|
| Plate body (137.2mm × 68.6mm × 3.0mm rectangular solid) | Physical necessity — structural | The plate must occupy the correct spatial envelope to hold two Kamoer KPHM400 pumps side by side. Width 137.2mm = 2 × 68.6mm bracket width (two pump brackets flush, no gap). Height 68.6mm = bracket outer dimension. Thickness 3.0mm provides 6 M3 thread engagements minimum (0.5mm pitch); below this, pull-out risk under vibration increases. |
| Plate width = 137.2mm | Physical necessity — assembly | Derived from 2 × pump bracket width (68.6mm). Two brackets placed flush consume exactly this width. No additional margin is justified — synthesis.md Section 3. |
| Plate height = 68.6mm | Physical necessity — assembly | Matches pump bracket outer dimension (68.6mm). Outermost hole centers land 9.3mm from each plate edge — 2.3× the minimum M3 edge clearance (~4mm). |
| Plate thickness = 3.0mm | Physical necessity — structural | M3 thread engagement minimum: 6 passes at 0.5mm pitch = 3.0mm. Below 3.0mm thread engagement drops below 4 passes and risks pull-out under vibration (synthesis.md Section 3). |
| Motor bore (2×, 37mm dia) | Vision | vision.md Section 4 Season 1 Phase 1 Item 2: "flat plate with 2 motor bores (~37mm, for the motor cylinder to pass through)...The screws approach from the motor side — you cannot reach them without the motor bore." |
| Motor bore diameter = 37mm | Vision + physical necessity | Motor cylinder is 35.73mm (caliper photo 16). Vision specifies ~37mm bore. Diametric clearance = 1.27mm (0.635mm radial). Sufficient for assembly and any FDM dimensional variation. |
| Motor bore center positions (34.3mm, 34.3mm) and (102.9mm, 34.3mm) | Physical necessity — assembly | Each bore is centered on the pump motor axis in the plate XZ plane. Motor axes are at the center of each pump half-plate region. Derived in spatial-resolution.md Section 3.3. |
| 8× M3 clearance holes, 3.3mm diameter | Physical necessity — assembly | The pumps must be fastened to the plate. The Kamoer KPHM400 bracket has 4× M3 holes per pump (caliper-verified, geometry-description.md photo 06). 2 pumps × 4 holes = 8 holes required. Diameter 3.3mm = nominal M3 (3.0mm) + 0.2mm loose clearance per requirements.md. |
| Hole pattern: 50mm × 50mm square per pump | Physical necessity — assembly | Must match pump bracket hole pattern. Center-to-center spacing is 50mm × 50mm per datasheet and caliper-verified (geometry-description.md). |
| Pump 1 hole pattern centered at X=34.3mm, Z=34.3mm | Physical necessity — assembly | Pump 1 occupies X=0..68.6mm, Z=0..68.6mm on the plate face. Center of that region is (34.3, 34.3). Holes at ±25mm from center in X and Z. |
| Pump 2 hole pattern centered at X=102.9mm, Z=34.3mm | Physical necessity — assembly | Pump 2 occupies X=68.6..137.2mm, Z=0..68.6mm. Center of that region is (102.9, 34.3). Holes at ±25mm from center in X and Z. |
| Through-hole geometry (Y=0 to Y=3.0mm, no partial depth) | Physical necessity — assembly | Screws must pass completely through the plate to engage threads in the pump head on the far side. A blind hole would block the screw path. |

No unjustified features. Every geometric feature on this part traces directly to physical assembly necessity or the vision document.

---

## Feature Specification

### Feature 1 — Plate Body

| Property | Value |
|----------|-------|
| Geometry | Rectangular solid |
| Width (X) | 137.2mm |
| Height (Z) | 68.6mm |
| Thickness (Y) | 3.0mm |
| Front face | Y=0, spanning X=0..137.2mm, Z=0..68.6mm |
| Back face | Y=3.0mm, spanning X=0..137.2mm, Z=0..68.6mm |
| All corners | Square (no chamfer, no fillet required in Phase 1) |

### Feature 2 — Motor Bores (2×)

| Property | Value |
|----------|-------|
| Geometry | Cylindrical through-bore |
| Diameter | 37mm |
| Bore axis | Parallel to Y |
| Entry | Y=0 (front face) |
| Exit | Y=3.0mm (back face) |
| Bore 1 center (X, Z) | X=34.3mm, Z=34.3mm |
| Bore 2 center (X, Z) | X=102.9mm, Z=34.3mm |
| Purpose | Motor cylinder (35.73mm dia) passes through the plate; screws are installed from the motor side (Y=3.0mm side) and can only be reached with the bore present |

### Feature 3 — M3 Clearance Holes (8×)

All holes are through-holes. Hole axis is parallel to Y. Entry at Y=0 (front face), exit at Y=3.0mm (back face).

| Hole ID | X (mm) | Z (mm) | Diameter | Depth | Notes |
|---------|--------|--------|----------|-------|-------|
| 1-A | 9.3 | 59.3 | 3.3mm | Through (Y=0 to Y=3.0mm) | Pump 1, top-left |
| 1-B | 59.3 | 59.3 | 3.3mm | Through (Y=0 to Y=3.0mm) | Pump 1, top-right |
| 1-C | 59.3 | 9.3 | 3.3mm | Through (Y=0 to Y=3.0mm) | Pump 1, bottom-right |
| 1-D | 9.3 | 9.3 | 3.3mm | Through (Y=0 to Y=3.0mm) | Pump 1, bottom-left |
| 2-A | 77.9 | 59.3 | 3.3mm | Through (Y=0 to Y=3.0mm) | Pump 2, top-left |
| 2-B | 127.9 | 59.3 | 3.3mm | Through (Y=0 to Y=3.0mm) | Pump 2, top-right |
| 2-C | 127.9 | 9.3 | 3.3mm | Through (Y=0 to Y=3.0mm) | Pump 2, bottom-right |
| 2-D | 77.9 | 9.3 | 3.3mm | Through (Y=0 to Y=3.0mm) | Pump 2, bottom-left |

**Derivation check (from spatial-resolution.md):**
- Pump 1 center: X=34.3mm, Z=34.3mm. Holes at ±25mm: X ∈ {9.3, 59.3}, Z ∈ {9.3, 59.3}. All four holes verified.
- Pump 2 center: X=102.9mm, Z=34.3mm. Holes at ±25mm: X ∈ {77.9, 127.9}, Z ∈ {9.3, 59.3}. All four holes verified.
- Edge clearances: 9.3mm from plate edge to nearest hole center on all four sides (left: X=9.3mm; right: 137.2-127.9=9.3mm; bottom: Z=9.3mm; top: 68.6-59.3=9.3mm). Minimum required for M3: ~4mm. All clear.

---

## Bill of Materials

| Item | Specification | Qty | Notes |
|------|--------------|-----|-------|
| Pump Tray (this part) | 137.2mm × 68.6mm × 3.0mm, PLA or PETG | 1 | Print flat on build plate |
| M3 screws | M3 × 10mm (tentative — confirm against pump head thread depth measurement) | 8 | 4 per pump. Length = 3.0mm plate + ~1.5mm bracket + ~5mm engagement in pump head. Measure pump head thread depth before ordering; use M3 × 8mm if thread depth is less than 4mm. |

---

## Design Gaps (Phase 1)

The following gaps are identified but are explicitly out of scope for Phase 1. They are flagged here for future phases.

| Gap | Description | Phase |
|----|-------------|-------|
| Pump bracket rotational orientation | The 50mm × 50mm hole pattern is rotationally symmetric. Any of 4 pump orientations (0°/90°/180°/270°) produce correct hole alignment. The correct orientation for tube routing is not determinable until Season 2 cartridge wall geometry exists. No keying feature can be designed without this information. | Season 2 |
| Plate retention in cartridge rails | The pump tray has no feature preventing it from sliding out of the cartridge side wall rails. Rail engagement and retention detents are future work. | Season 2 (rail geometry), Season 3 (retention detents) |
| Strut bores | 4× bores for the lever struts to pass through the plate are not in Phase 1. | Phase 4 (vision.md item 12) |
| Rail features (tabs/slots on X=0 and X=137.2mm plate edges) | The side wall rail interface is not designed. Left and right plate edges are plain cut surfaces in Phase 1. | Season 2 (vision.md Phase 5) |
| M3 screw length (confirmed) | Screw length requires measurement of pump head thread depth from bracket face. Tentative M3 × 10mm. | Before ordering hardware |

---

## Excluded Features (Phase 1)

The following features are explicitly excluded. Their absence is correct and intentional.

| Feature | Excluded because |
|---------|-----------------|
| Strut bores | Phase 4 work (vision.md item 12). |
| Rail tabs or slots on plate edges | Season 2 work (vision.md Phase 5). |
| Retention detents or snap features | Season 3 work (vision.md Phase 9). |
| Chamfers or fillets on plate corners | No mating surface, no cosmetic requirement in Phase 1. |
| Bottom edge chamfer (elephant's foot per requirements.md) | Bottom face is not a mating surface in Phase 1. |
| Bosses around screw holes | No load justification. 9.3mm of solid plate material surrounds each hole — structurally adequate. Bosses are Season 3 refinement work (vision.md Phase 10, item 31). |
| Surface texture or finish features | Interior part; no cosmetic requirements. |
