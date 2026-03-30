# Coupler Tray — Spatial Resolution

**Pipeline step:** 4s — Spatial Resolution
**Part:** Coupler tray (single unit, pass-through from 4d)
**Input documents:** synthesis.md, concept.md, decomposition.md, john-guest-union/geometry-description.md

---

## 1. System-Level Placement

```
Part:        Coupler tray
Parent:      Pump cartridge interior
Position:    Interior flat plate, perpendicular to cartridge front-to-back axis
             Specific Z position within cartridge not yet fixed (Phase 5/6 dependency)
Orientation: Plate face parallel to the cartridge back wall; bore axes parallel to
             the cartridge front-to-back depth axis (horizontal in the installed device)
```

This section is context only. The coupler tray has no angled mounting relative to gravity. The plate face is vertical when installed. Bore axes are horizontal. No physics-dependent profile derivation is needed — gravity acts perpendicular to the bore axes, loading the coupler in the radial direction of the narrow bore (0.095mm radial clearance per side, which provides the gravity support).

The coupler tray's position within the cartridge depth (distance from the back wall) is not yet determined and is not required for this part to be specified or printed. The bore positions are defined in the tray's own frame. The tray slides into side-wall rails (Phase 5); rail geometry and final Z placement in the cartridge are Phase 5 dependencies.

---

## 2. Part Reference Frame

```
Part:    Coupler tray
Origin:  Center of the insertion face (geometric center of the plate, on the large-bore face)
X:       Horizontal, positive right (when viewed from the insertion face, +X = pump 2 / right side)
Y:       Vertical, positive up
Z:       Depth into the plate from the insertion face, positive toward far face
         Z = 0 at the insertion face (large-bore openings)
         Z = +15mm at the far face (narrow-bore openings)

Plate extents in local frame:
  X: -40mm to +40mm   (80mm total width)
  Y: -25mm to +25mm   (50mm total height)
  Z:   0mm to +15mm   (15mm total depth/thickness)

Print orientation:
  Insertion face (Z = 0) placed down on the build plate.
  Bore axes run in the Z direction (vertical, parallel to layer stack).
  Layer lines parallel to plate face (XY plane).
  X and Y axes are horizontal during printing.

Installed orientation:
  Z axis is horizontal (parallel to cartridge front-to-back depth axis).
  Y axis is vertical (parallel to gravity, pointing up).
  X axis is horizontal (parallel to cartridge width axis).
  No rotation relative to gravity — the part installs in the same orientation it prints,
  with the bore axes becoming horizontal when the cartridge is installed upright.
```

---

## 3. Derived Geometry

### 3.1 Bore Center Positions

All four bore axes are parallel to Z. Bore centers are defined as (X, Y) positions on the plate face; they extend from Z = 0 to Z = +15mm.

| Pocket | Pump | Role       |     X |     Y | Bore axis |
|--------|------|------------|------:|------:|-----------|
| A      | 1    | Inlet      | -31mm | +15mm | Z = 0 to +15mm |
| B      | 1    | Outlet     | -31mm | -15mm | Z = 0 to +15mm |
| C      | 2    | Inlet      | +31mm | +15mm | Z = 0 to +15mm |
| D      | 2    | Outlet     | +31mm | -15mm | Z = 0 to +15mm |

Center-to-center spacings (in local frame):
- Horizontal (A–C or B–D): 62mm along X
- Vertical (A–B or C–D): 30mm along Y
- Diagonal (A–D or B–C): sqrt(62² + 30²) = sqrt(3844 + 900) = sqrt(4744) = 68.9mm

These positions match the release plate fitting positions from the release plate synthesis (same four points, same coordinate convention). The coupler tray pocket centers are locked to the release plate bore centers. If the release plate positions change, the coupler tray positions change identically.

### 3.2 Bore Stage Geometry (Z Extents)

Each pocket is a two-stage stepped bore. The following applies identically to all four pockets.

**Stage 1 — Large bore (insertion side):**
```
Diameter (designed CAD value):  15.5mm
Z start:                         0mm  (insertion face, open)
Z end:                          +12.08mm  (bore shoulder, annular step)
Depth:                          12.08mm
Receives:                       Insertion-side body end of coupler (15.10mm OD, 12.08mm long)
```

**Stage 2 — Narrow bore (far side):**
```
Diameter (designed CAD value):  9.5mm
Z start:                        +12.08mm  (immediately at the large-bore shoulder)
Z end:                          +15mm     (far face, open)
Depth:                          2.92mm
Receives:                       Center body of coupler (9.31mm OD) — passes through and extends beyond
```

**Bore shoulder (annular step):**
```
Z position:    +12.08mm
Inner radius:   4.75mm (half of 9.5mm narrow bore)
Outer radius:   7.75mm (half of 15.5mm large bore)
Annular width:  3.0mm  (7.75 − 4.75)
Face normal:    +Z direction (faces toward insertion face, catches body end 1 shoulder)
```

**FDM compensation note:** Per requirements.md, holes print smaller than designed by approximately 0.2mm. The values above (15.5mm and 9.5mm) are the designed CAD values to be modeled. If empirical calibration shows 0.2mm undersize, update to 15.7mm large bore and 9.7mm narrow bore. The narrow bore is critical — 9.5mm designed on a 9.31mm center body gives 0.095mm radial clearance per side. If printed at 9.3mm it becomes a near-press-fit. Verify with test coupon before final print (see synthesis.md, Open Question 1).

### 3.3 Coupler Zone Mapping in Local Frame

This section confirms the coupler geometry relative to the plate Z axis when a coupler is fully seated. All positions are in the coupler tray local frame.

The coupler body has three zones (symmetric barbell):

| Coupler zone        | OD       | Length  |
|---------------------|----------|---------|
| Body end 1 (insertion side) | 15.10mm | 12.08mm |
| Center body          | 9.31mm   | 12.16mm |
| Body end 2 (far side) | 15.10mm | 12.08mm |
| Total body           | —        | 36.32mm |

**Coupler zone positions when fully seated in the tray (local Z coordinates):**

| Coupler zone | Z start | Z end | Location relative to plate |
|---|---|---|---|
| Body end 1 (insertion side) | Z = 0 | Z = +12.08mm | Inside the plate, within large bore |
| Shoulder 1 (body end 1 → center) | Z = +12.08mm | — | At the large-bore shoulder; annular face bears against bore step |
| Center body | Z = +12.08mm | Z = +24.24mm | Begins inside narrow bore; exits far face at Z = +15mm; extends 9.24mm beyond far face |
| Far face of plate | — | Z = +15mm | Center body passes through here; narrow bore exit lip is here |
| Shoulder 2 (center → body end 2) | Z = +24.24mm | — | 9.24mm beyond far face; annular face cannot pass back through narrow bore |
| Body end 2 (far side) | Z = +24.24mm | Z = +36.32mm | Entirely outside the plate on the far side |

**Axial retention geometry — explicit confirmation:**

The center body is 12.16mm long. The narrow bore section through the plate is only 2.92mm deep (from Z = +12.08mm to Z = +15mm). The center body does NOT fit within the narrow bore section — it extends 12.16mm, of which only 2.92mm is inside the plate. The remaining 9.24mm of center body (and all of body end 2) extends beyond the far face of the plate.

Retention in the ejection direction (-Z, pulling coupler out through insertion face):
- Shoulder 2 (at Z = +24.24mm, between center body and body end 2) is 15.10mm OD
- The narrow bore exit opening (at Z = +15mm) is 9.5mm diameter
- 15.10mm > 9.5mm — shoulder 2 cannot pass back through the narrow bore
- The far face of the plate (Z = +15mm) is the bearing surface
- The annular contact zone: inner radius = 4.75mm (narrow bore), outer radius = 7.55mm (half of 15.10mm body end 2 OD)
- Annular bearing width: 7.55mm − 4.75mm = 2.80mm
- RETAINED: coupler cannot be ejected through the insertion face

Retention in the insertion direction (+Z, pushing coupler further through):
- Shoulder 1 (at Z = +12.08mm, between body end 1 and center body) is 15.10mm OD
- The narrow bore at that depth (immediately past the large-bore shoulder) is 9.5mm diameter
- 15.10mm > 9.5mm — shoulder 1 cannot pass through the narrow bore
- The large-bore shoulder at Z = +12.08mm is the bearing surface
- The annular contact zone: inner radius = 4.75mm (narrow bore), outer radius = 7.55mm (half of 15.10mm body end 1 shoulder)
- Annular bearing width: 7.55mm − 4.75mm = 2.80mm
- RETAINED: coupler cannot be pushed further through in the +Z direction

Both axial directions are constrained. The coupler is fully captured.

Radial support:
- Center body OD: 9.31mm; narrow bore diameter: 9.5mm
- Radial clearance: (9.5 − 9.31) / 2 = 0.095mm per side
- The narrow bore provides radial constraint over 2.92mm of depth
- Under gravity (Y direction, perpendicular to bore axis Z), this clearance is sufficient for a coupler weighing a few grams

### 3.4 Pocket Wall Material Check

The tightest wall condition is at the large bore level (15.5mm diameter), at the bore center nearest the plate edge.

**Horizontal direction (X) — nearest plate edge:**
- Bore center at X = ±31mm; plate edge at X = ±40mm
- Wall from bore edge to plate edge: 40 − 31 − (15.5 / 2) = 40 − 31 − 7.75 = **1.25mm**
- Requirements.md structural wall minimum: 1.2mm (3 perimeters)
- 1.25mm meets the 1.2mm minimum. This is the tightest wall in the part.
- At narrow bore level (Z > 12.08mm): wall = 40 − 31 − (9.5 / 2) = 40 − 31 − 4.75 = **4.25mm** — ample

**Vertical direction (Y) — nearest plate edge:**
- Bore center at Y = ±15mm; plate edge at Y = ±25mm
- Wall from bore edge to plate edge: 25 − 15 − (15.5 / 2) = 25 − 15 − 7.75 = **2.25mm**
- 2.25mm exceeds the 1.2mm minimum — adequate

**Between adjacent bores (large bore level):**
- Vertical neighbors (A–B, C–D): center-to-center 30mm, bore diameter 15.5mm
  - Wall between bores: 30 − 15.5 = **14.5mm** — ample
- Horizontal neighbors (A–C, B–D): center-to-center 62mm, bore diameter 15.5mm
  - Wall between bores: 62 − 15.5 = **46.5mm** — ample

Wall check result: The part meets the minimum wall requirement at all locations. The tightest point is 1.25mm at the horizontal bore-edge-to-plate-edge wall, which meets the 1.2mm structural minimum by 0.05mm. This is a marginal pass. If the plate width is reduced in Phase 5 (rail geometry may require it), verify this wall does not drop below 1.2mm.

### 3.5 Interface: Coupler Pocket (all four identical)

The coupler pocket interface in local frame coordinates:

```
Pocket interface geometry (single pocket, applies identically to A, B, C, D):

  Insertion face opening:
    Center (X, Y):   per pocket table in Section 3.1
    Z position:      Z = 0
    Diameter:        15.5mm (designed CAD value)
    Chamfer:         0.3mm × 45° at bore rim (Z = 0, bottom face during print)
                     per requirements.md elephant's foot mitigation

  Large bore:
    Diameter:        15.5mm
    Z extent:        Z = 0 to Z = +12.08mm
    Receives:        Body end 1 of coupler (15.10mm OD), sliding fit

  Bore shoulder (retention step):
    Z position:      Z = +12.08mm
    Inner edge:      R = 4.75mm from bore center axis
    Outer edge:      R = 7.75mm from bore center axis
    Face normal:     Faces -Z (toward insertion face)
    Function:        Blocks shoulder 1 of coupler from advancing in +Z direction

  Narrow bore:
    Diameter:        9.5mm
    Z extent:        Z = +12.08mm to Z = +15mm
    Receives:        Center body of coupler (9.31mm OD), passes through

  Far face opening (narrow bore exit lip):
    Center (X, Y):   same as insertion face center (bore axis is straight, no offset)
    Z position:      Z = +15mm
    Diameter:        9.5mm (narrow bore exit)
    Lip annular surface:
      Inner radius:  4.75mm
      Outer radius:  7.75mm (to the large-bore wall material above, but this is the plate face)
      Width:         see note below
    Function:        Bearing surface for shoulder 2 of coupler (far body end, 15.10mm OD)
                     when coupler is pulled in -Z direction

  Note on far face lip outer radius: The far face of the plate at Z = +15mm exposes the full plate
  face material. The narrow bore exits at 9.5mm diameter. The body end 2 shoulder (15.10mm OD)
  bears against the plate face in the annular zone from R = 4.75mm to R = 7.55mm (half of 15.10mm).
  The bearing annular width is 7.55mm − 4.75mm = 2.80mm. This is well within the 3.0mm annular
  ring of narrow-bore-to-large-bore wall material that exists at that radial zone.

  Mating part:      John Guest PP0408W union coupler
  Mating features:  Body end 1 shoulder (sits in large bore), shoulder 1 annular face (bears on bore
                    step at Z = +12.08mm), center body (slides in narrow bore), shoulder 2 annular
                    face (bears on far face at Z = +15mm when loaded in -Z direction)
```

### 3.6 No Routing Paths

There are no tubes, wires, or flexible elements that pass through or are routed in this part in Phase 1. The couplers seat in the pockets; the tubing connects to the coupler ends outside the tray. No routing geometry is needed.

---

## 4. Transform Summary

The coupler tray has no angled mounting and no multi-frame spatial relationships. The part frame and the cartridge system frame share the same axis orientations — they differ only by a translation.

```
Part frame → Cartridge system frame:
  Rotation:    None (part axes are parallel to cartridge axes)
  Translation: (Tx, Ty, Tz) — not yet determined (Phase 5/6 dependency)
               Tx: distance from cartridge centerline to tray center (likely ~0, centered)
               Ty: distance from cartridge vertical center to tray center (TBD)
               Tz: distance from cartridge back wall to tray insertion face (TBD)

Cartridge system frame → Part frame:
  Translation: (-Tx, -Ty, -Tz)
  Rotation:    None
```

Since translation values are not yet determined, three verification test points are stated in part-local frame and their system-frame equivalents are expressed symbolically:

**Verification test point 1 — Part origin:**
```
Part-local:    (X=0, Y=0, Z=0)  — center of insertion face
System-frame:  (Tx, Ty, Tz)
Check:         Part origin is at the insertion face center, which is the reference point for
               all bore positions. Bore A center is at part-local (-31, +15, 0) — in system
               frame this is (Tx − 31, Ty + 15, Tz). Bore D center is at part-local (+31, −15, 0)
               — in system frame (Tx + 31, Ty − 15, Tz). Self-consistent. ✓
```

**Verification test point 2 — Far face center:**
```
Part-local:    (X=0, Y=0, Z=+15)  — center of far face
System-frame:  (Tx, Ty, Tz + 15)
Check:         The far face is 15mm deeper into the cartridge (in the +Z direction in both frames,
               since there is no rotation). The center body of any seated coupler exits the far
               face at this Z depth. Shoulder 2 of each coupler is at Z = +24.24mm in part-local
               frame, which is Tz + 24.24mm in system frame. This is 9.24mm deeper than the
               far face — consistent with the coupler extending beyond the plate. ✓
```

**Verification test point 3 — Bore A center at bore shoulder depth:**
```
Part-local:    (X=−31, Y=+15, Z=+12.08)  — bore A, at the large-bore-to-narrow-bore shoulder
System-frame:  (Tx − 31, Ty + 15, Tz + 12.08)
Check:         This point is the shoulder that blocks shoulder 1 of coupler A from advancing.
               The part-local X and Y coordinates match the bore center position from Section 3.1.
               The Z coordinate (12.08mm) matches the large bore depth from Section 3.2.
               Round-trip: system → part: subtract (Tx, Ty, Tz) → (−31, +15, +12.08). ✓
```

---

## 5. Hidden Spatial Dependencies — Verification

The following spatial dependencies were checked:

**1. Coupler axial protrusion beyond far face.**
The center body and body end 2 extend 9.24mm + 12.08mm = 21.32mm beyond the far face (Z = +15mm). This protrusion exists in the cartridge depth space between the coupler tray far face and the back wall. The back wall must have clearance for the collet-extended coupler length on the far side: body end 2 (12.08mm) plus collet extension (~2.74mm) = ~14.82mm minimum clearance between tray far face and back wall interior surface. This is a Phase 5 cartridge geometry dependency. No action required for this part specification — flagged for cartridge layout.

**2. Coupler protrusion beyond insertion face.**
When a coupler is fully seated, body end 1 fills the large bore from Z = 0 to Z = +12.08mm and does not protrude beyond the insertion face. The collet extends from the body end face by ~2.74mm (extended). The collet protrudes from the insertion face of the plate by ~2.74mm in the -Z direction. The pump tray (on the insertion face side of the coupler tray) must have clearance for these collet protrusions. This is a Phase 5 inter-plate spacing dependency. Flagged for cartridge layout.

**3. Bore position dependency on release plate.**
The four bore centers in this part (±31mm X, ±15mm Y) are locked to the release plate fitting positions. The synthesis notes that the ±15mm vertical value is an assumption from the release plate synthesis, not a caliper-verified pump tube connector exit position (Open Question 3 in synthesis.md). If this value changes, both the release plate and this coupler tray must be updated together. No hidden dependency within this part — the dependency is documented and external.

**4. Gravity direction relative to bore axes.**
The bore axes are horizontal when installed (Z axis of part = front-to-back axis of cartridge). Gravity acts in the -Y direction (down). Gravity is perpendicular to the bore axes. This means the couplers are radially loaded by gravity, supported by the narrow bore walls. The 0.095mm radial clearance per side is sufficient for gravity support (coupler weighs approximately 5–10 grams). No physics derivation is required for the part geometry — the bore diameter drives this, and it is specified in Section 3.2.

**5. Print orientation and bore axis alignment.**
The bore axes are Z in the part frame. The print orientation places bores vertical (Z up during printing). The installed orientation rotates Z from vertical (print) to horizontal (installed). This is a rigid body rotation in the system frame — it does not affect any dimension in the part frame. No hidden dependency.

**6. Elephant's foot chamfer location.**
The insertion face (Z = 0) is placed down on the build plate during printing. The elephant's foot affects the bore rim at Z = 0. The chamfer (0.3mm × 45°) is applied to the bore entrance at Z = 0 on the insertion face. This is noted in Section 3.5. No hidden geometry — the chamfer is a small point addition to each bore's revolved profile.

**Result: No hidden spatial dependencies found.** All dimensional dependencies are either self-contained within the part frame or explicitly flagged as external (cartridge layout, release plate alignment, empirical printer calibration).

---

## 6. Complete Dimension Reference

All dimensions in coupler tray local frame. No downstream derivation required.

**Plate body:**

| Dimension | Value | Frame |
|---|---|---|
| Width (X extent) | 80mm | part-local, −40mm to +40mm |
| Height (Y extent) | 50mm | part-local, −25mm to +25mm |
| Depth/thickness (Z extent) | 15mm | part-local, 0 to +15mm |

**Bore center positions (all four, at insertion face Z = 0):**

| Pocket | X | Y |
|---|---|---|
| A (Pump 1 Inlet) | −31mm | +15mm |
| B (Pump 1 Outlet) | −31mm | −15mm |
| C (Pump 2 Inlet) | +31mm | +15mm |
| D (Pump 2 Outlet) | +31mm | −15mm |

**Bore stage dimensions (identical for all four pockets):**

| Feature | Designed diameter | Z start | Z end | Depth |
|---|---|---|---|---|
| Large bore | 15.5mm | Z = 0 | Z = +12.08mm | 12.08mm |
| Bore shoulder (annular step) | 9.5mm inner / 15.5mm outer | Z = +12.08mm | — | — |
| Narrow bore | 9.5mm | Z = +12.08mm | Z = +15mm | 2.92mm |

**Entry chamfer (elephant's foot mitigation):**

| Feature | Value | Z position |
|---|---|---|
| Chamfer size | 0.3mm × 45° | at Z = 0, bore rim on insertion face |

**Coupler seating positions in local frame (reference, not part geometry):**

| Coupler zone | Z start | Z end | Relative to plate |
|---|---|---|---|
| Body end 1 (insertion side) | Z = 0 | Z = +12.08mm | Inside plate, in large bore |
| Shoulder 1 (retention stop) | Z = +12.08mm | — | At bore shoulder, cannot advance in +Z |
| Center body | Z = +12.08mm | Z = +24.24mm | Passes through plate and extends 9.24mm beyond far face |
| Plate far face | — | Z = +15mm | Center body passes through here |
| Shoulder 2 (retention stop) | Z = +24.24mm | — | 9.24mm beyond far face; cannot retract in -Z through narrow bore |
| Body end 2 (far side) | Z = +24.24mm | Z = +36.32mm | Entirely outside plate on far side |

**Wall thicknesses at tightest points:**

| Location | Wall thickness | Minimum required | Status |
|---|---|---|---|
| Horizontal, large bore to plate edge | 1.25mm | 1.2mm | Marginal pass |
| Vertical, large bore to plate edge | 2.25mm | 1.2mm | Pass |
| Between vertical bore pair (large bore) | 14.5mm | 1.2mm | Pass |
| Narrow bore exit lip, annular bearing | 3.0mm wide | 1.2mm | Pass |
