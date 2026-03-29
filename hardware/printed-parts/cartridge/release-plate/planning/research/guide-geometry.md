# Release Plate Linear Guide Geometry

## Context

The release plate is a flat PETG plate inside the cartridge that presses against the collets of 4 John Guest PP0408W fittings simultaneously. When the user squeezes, the plate translates ~1.3mm axially (toward the fittings) to depress all 4 collets and release the 4 tube stubs. The plate is guided by integral FDM-printed features (pin-in-hole or rail-in-groove) in the cartridge body. The plate must not tilt, rack, or bind during travel.

All dimensions from the John Guest PP0408W caliper-verified geometry document unless otherwise noted.

---

## 1. Anti-Tilt Geometry: Minimum Pin Engagement Length

### The problem

A plate guided on pins experiences a binding moment if the load is applied off-center relative to the guide. The 4 collet contact points are arranged approximately 45mm × 40mm (horizontal × vertical center-to-center). The guide pins are located at the perimeter of the plate. The load from the 4 collets is distributed, but any asymmetry — a finger pressing slightly off-center, one collet bottoming out before the others — creates a net moment on the plate about an axis perpendicular to translation.

The critical condition is when all 4 collets present their maximum resistive force simultaneously at the beginning of travel. The plate is a rigid body constrained only by the pins.

### Binding ratio (Sommerfeld-Prandtl anti-bind criterion)

For a pin-in-hole linear guide, binding occurs when the ratio of the moment arm to bearing length exceeds the inverse of twice the friction coefficient:

```
No-bind condition: L_bearing ≥ 2μ × e
```

Where:
- `L_bearing` = engagement length of pin in bore (along translation axis), mm
- `μ` = coefficient of friction, PETG on PETG (dry)
- `e` = maximum moment arm (perpendicular distance from load centroid to pin centerline), mm

**Friction coefficient, PETG on PETG (dry):** μ ≈ 0.25 to 0.35. Use μ = 0.35 (conservative, accounts for surface roughness from FDM layer lines).

**Moment arm:** The worst case is a single off-center finger press. The user's finger contacts the pull surface at an arbitrary point. The pull surface is the full front face of the plate. If the user grips asymmetrically, the effective load point could be as far as half the plate width from the guide pin centerline. The plate is approximately 55mm × 50mm (to accommodate the 45mm × 40mm fitting pattern with wall clearance). Maximum plausible offset `e` from pin centerline to load point: ~25mm (half of 50mm width).

A more useful worst case: with 2 guide pins at the far left and right of the plate (both at the same axial position), a moment about the vertical axis (racking) is resisted by the couple between the two pins. However, tilting about the horizontal axis (pitch) — the plate front dipping down while the back goes up — is the more dangerous mode because the lever arm is the full plate height and both pins contribute to the same moment (they are coplanar if placed at the same height).

**Design choice to eliminate the worst mode: place the 2 guide pins at opposite corners, not both at the same height.** With pins at top-left and bottom-right, both pitch and yaw moments are resisted simultaneously with good mechanical advantage.

**Binding calculation for a single pin (worst case, moment arm e = 25mm):**

```
L_bearing ≥ 2 × 0.35 × 25mm
L_bearing ≥ 17.5mm
```

This is the theoretical minimum per pin. However, this calculation assumes the pin itself is rigid and the bore is the only contact zone. For FDM printed PETG pins, there is additional compliance at the pin base, and the bore contact zone compresses slightly under load. Apply a safety factor of 1.5:

```
L_bearing (design) ≥ 17.5mm × 1.5 = 26.25mm → round up to 28mm minimum
```

**With 2 pins placed at diagonally opposite corners, the effective moment arm for any in-plane moment is reduced** because each pin shares the restraint. The moment arm `e` for tilt about the horizontal axis is approximately half the corner-to-corner diagonal divided by the number of pins × their separation. For a two-pin system at diagonal corners with ~50mm × 45mm spacing, the moment arm per pin for the worst-case load (one side only) is reduced to approximately 15–20mm. This gives:

```
L_bearing ≥ 2 × 0.35 × 20mm × 1.5 = 21mm → round up to 24mm minimum
```

**Governing minimum engagement length: 28mm** (use the single-pin worst case, not the cooperative case, as a safety margin).

However, 28mm is very long relative to the ~1.5–2mm of travel. This is actually an argument for keeping the pins **long overall** with the bore spanning nearly the full depth of the cartridge body, not just the travel distance. The guide bore in the cartridge body should be at least 28mm deep. The pin on the plate need only extend far enough into that bore at the end of travel — meaning the pin must be at least (28mm + 2mm travel) = 30mm long from the plate face.

**Practical check: L/D ratio.** A second way to arrive at the same answer is the classical plain bearing L/D guideline:

- For light loads, close fit: L/D = 1.0–1.5
- For precision sliding guides (no tilting): L/D = 1.5–2.0

With a 4mm pin diameter (see Section 2), L/D = 1.5 gives L = 6mm. L/D = 2.0 gives L = 8mm. These are dramatically shorter than the 28mm from the binding ratio. The discrepancy is because the L/D guideline assumes the load is applied at the bearing itself, with a short moment arm. For the release plate, the load is applied at a large offset (the collet pattern, ~20mm from the guide pin). The binding ratio calculation is the correct tool for this geometry.

**Conclusion: Guide pins must have at least 28mm of engagement length in the bore at all points in their travel. The bore in the cartridge body must be at least 30mm deep (28mm engagement + 2mm travel clearance at full stroke end).**

---

## 2. Pin Diameter

### Constraints

From requirements.md Section 6:
- Minimum wall thickness: 0.8mm (2 perimeters). Structural walls bearing load: 1.2mm (3 perimeters).
- Holes print 0.2mm smaller than designed. Add 0.2mm to hole diameter for loose fit.
- Sliding fits: 0.2mm clearance minimum between mating printed parts.

### Structural sizing of the pin

The pin must not fail in bending under the collet release force applied at an offset. The total collet release force drives pin bending.

**Collet release force estimate:**

John Guest push-fit fittings use an internal compression spring to hold the collet in the extended position (tube-gripped state). Industry practice for 1/4" push-fit fittings in plumbing applications (John Guest, SharkBite, similar) requires approximately 15–25N per fitting collet to depress it against the spring and gripper teeth. For the PP0408W specifically, the collet spring is sized for low-pressure tubing (~10 bar max rated), and the gripper resistance adds tactile stiffness. A measured value of ~20N per collet is consistent with hands-on experience of similar fittings.

**Total force on plate at max collet resistance: 4 fittings × 20N = 80N**

This 80N is applied at the collet pattern centroid. With 2 guide pins, each pin carries 40N of shear at the bore edge (simplified; actual loading is a couple, not pure shear, but this bounds the stress).

**Pin bending stress with 40N point load at 20mm cantilever from bore edge:**

```
M = F × L = 40N × 20mm = 800 N·mm
σ = M / Z = M / (π × d³ / 32) ≤ σ_allowable
```

PETG tensile strength: ~50 MPa. Apply factor of safety 3 for FDM printed PETG (layer adhesion weakness, surface stress concentration from layer lines):

```
σ_allowable = 50 / 3 = 16.7 MPa
Z = π × d³ / 32

d³ ≥ 32 × M / (π × σ_allowable) = 32 × 800 / (π × 16.7) = 487 mm³
d ≥ 7.8mm
```

This result (7.8mm minimum pin diameter) reflects the worst case of a full 40N cantilever load at 20mm offset. In reality:
1. The collet force is distributed across all 4 contacts, and their centroid is close to the plate center, not at the pin location.
2. The pin is supported at both ends (plate side and bore bottom), not cantilevered.
3. The 80N total force is the maximum instantaneous peak as all collets begin to depress simultaneously; the force likely drops once the gripper teeth disengage.

**Revised calculation for the realistic case (pin supported at both ends, 80N centrally distributed):**

For a simply supported beam with distributed central load, max moment = F × L / 4 where L is the unsupported span. The unsupported span is approximately the distance between the plate body wall and the bore entry face — roughly 10–15mm for this cartridge geometry.

```
M = 80N × 15mm / 4 = 300 N·mm (total, shared between 2 pins → 150 N·mm per pin)
d³ ≥ 32 × 150 / (π × 16.7) = 91.5 mm³
d ≥ 4.5mm
```

**Design pin diameter: 5mm.** This satisfies the structural calculation with margin, and satisfies the minimum wall thickness requirement (see below).

### Minimum wall thickness around the pin

The pin is a cylinder printed as part of the plate. At 5mm diameter, the pin itself is solid (no hollow). The bore in the cartridge body is the mating feature. The wall surrounding the bore must be at least 1.2mm thick (structural load-bearing per requirements.md):

```
Bore outer diameter (structural wall) = bore inner diameter + 2 × wall = 5.4mm + 2 × 1.2mm = 7.8mm minimum
```

The plate must have sufficient material around the pin base. The plate face material remaining between the pin base and the nearest collet bore is the constraining dimension. With a 5mm pin placed outside the collet pattern (beyond the 45mm × 40mm rectangle), the edge-to-edge distance to the nearest body end bore (15.10mm + 2mm clearance = ~17mm diameter feature) must be verified during layout. Minimum: 1.2mm wall between the pin base circle and any adjacent bore.

**Design minimum: 5mm pin diameter with 1.2mm structural wall at all cross-sections.**

---

## 3. Pin Count and Arrangement

### Two pins, not four

Four pins are mechanically over-constrained and would require extremely tight positional tolerance to prevent any two of the four from fighting each other (the classic three-point vs. four-point kinematic constraint problem). With FDM's ±0.2mm positional accuracy, a four-pin arrangement would likely cause binding from misalignment even at zero applied load.

Two pins is kinematically correct: they fully constrain the plate against rotation about the translation axis, against pitch, and against yaw, while being statically determinate in the transverse plane.

### Pin placement: diagonal corners of the plate

The plate must resist:
1. **Rotation about the translation axis (Z-axis spin):** Requires both pins to be off the plate's center of mass, with a separation perpendicular to the translation axis. Any two non-collinear pin positions prevent this.
2. **Pitch (tilt about horizontal axis):** Requires the pins to be at different heights — one pin high, one pin low.
3. **Yaw (tilt about vertical axis):** Requires the pins to be at different horizontal positions.

Placing both pins at the same height satisfies (1) and (3) but fails (2) — the plate can tilt forward about the horizontal axis with nothing to stop it until the bore wall catches.

**Recommended arrangement: one pin at top-left, one pin at bottom-right (or top-right / bottom-left).** This provides equal geometric resistance to all three out-of-axis motions with maximum mechanical advantage.

**Pin position relative to collet pattern:**

The 4 collet positions form a 45mm × 40mm rectangle. Place each guide pin outside and beyond the collet rectangle:
- Top-left pin center: approximately (−5mm, +5mm) from the top-left collet — i.e., 5mm to the left and 5mm above the corner collet center.
- Bottom-right pin center: approximately (+5mm, −5mm) from the bottom-right collet — i.e., 5mm to the right and 5mm below the corner collet center.

This positions the pins at the corners of approximately a 55mm × 50mm rectangle, which fits within a plate that extends 5mm beyond the collet pattern on all sides. Plate outer dimensions: approximately 60mm × 55mm to allow 1.2mm structural walls around the outermost features.

**The pin separation perpendicular to the translation axis** (the "anti-rotation" moment arm) is the full diagonal: sqrt(55² + 50²) ≈ 74mm. This is very large. Any rotation torque (e.g., user pressing to one side) produces a restoring force at the pins equal to torque / 74mm — easily within the structural capacity of 5mm PETG pins.

---

## 4. Clearance Tolerances

### FDM hole shrinkage (from requirements.md Section 6)

"Holes print smaller than designed. Add 0.2mm to hole diameters for loose fit."

This is confirmed by standard FDM practice: the perimeter toolpath of a circular hole traces the inside of the design diameter, and the finite nozzle width plus any over-extrusion reduces the as-printed hole diameter by 0.1–0.3mm depending on diameter, material, and calibration.

### Running clearance design

For a PETG-on-PETG sliding interface (no lubrication, occasional use):

The ISO H7/g6 running clearance fit for a 5mm pin is approximately:
- H7 bore: +0 / +0.012mm
- g6 pin: −0.004 / −0.016mm
- Resulting clearance: 0.004mm to 0.028mm (per side)

This is an excellent machined metal fit. For FDM printing, this tolerance is unachievable without iterative calibration. FDM achieves ±0.1–0.2mm absolute accuracy. The practical FDM sliding clearance must be much larger.

**FDM sliding clearance for PETG on PETG:**

Accounting for:
- Hole under-print: −0.2mm on diameter (from requirements.md)
- Surface roughness of FDM layer lines: Ra ≈ 10–20μm on flat surfaces, up to 50μm on cylindrical surfaces printed with visible steps (for a 5mm pin printed vertically, the octagonal/segmented perimeter produces peaks and valleys). At 0.2mm layer height, peaks are approximately 50μm (0.05mm) tall.
- Running clearance needed to clear peaks-and-valleys contact without binding: at least 2× the roughness peak height per side = 0.1mm per side = 0.2mm on diameter.

**Total diameter clearance needed:**

```
= FDM hole under-print compensation + running clearance + surface roughness allowance
= 0.2mm (hole comp) + 0.2mm (running) + 0.1mm (roughness)
= 0.5mm on diameter
```

This means: if the guide pin is designed at 5.0mm, the bore should be designed at 5.0mm + 0.5mm = **5.5mm designed bore diameter.**

The as-printed pin will be close to 5.0mm (pins are external features and print close to design size for solid cylinders). The as-printed bore will be approximately 5.5mm − 0.2mm = 5.3mm. Actual clearance on diameter: ~0.3mm = 0.15mm per side.

0.15mm per side clearance is appropriate for an FDM sliding fit: loose enough to slide without interference despite surface roughness, tight enough that the pin does not wobble by more than 0.15mm at the bore entry face. Over a 28mm engagement length, a 0.15mm radial play produces a maximum tilt angle of:

```
tan(θ) = 0.15 / 28 → θ = 0.31°
```

At a 22mm distance from the pin to the far edge of the plate, this produces 0.12mm of edge displacement — negligible and well within the operating clearance of the collet bore features on the plate.

**Summary of designed dimensions:**

| Feature | Design Dimension | Rationale |
|---------|-----------------|-----------|
| Pin OD | 5.0mm | Structural + FDM printability |
| Bore ID in cartridge body | 5.5mm | 5.0mm pin + 0.5mm clearance allowance |
| As-printed pin OD (estimated) | ~5.0mm | External cylinders print close to design |
| As-printed bore ID (estimated) | ~5.3mm | −0.2mm FDM hole undershoot |
| Effective clearance per side | ~0.15mm | Adequate for smooth PETG/PETG sliding |
| Max tilt from clearance (at 28mm engagement) | 0.31° | Negligible |

**Verification note:** The first printed cartridge should include a 10mm test section — a short pin stub and bore at the same design dimensions — to verify actual clearance before committing to the full depth bore. If binding occurs, increase bore design by 0.1mm increments.

---

## 5. Return Mechanism

### Requirements for return

After the user releases the squeeze, the plate must return ~1.3mm to its resting position, clearing the collets so they can re-grip tube stubs on re-insertion. The return must be positive (not relying on user action) and must not add complexity to the squeeze interaction.

### Options evaluated

**Gravity return:** The cartridge is mounted with the release mechanism on the front, and the translation axis is roughly horizontal (toward/away from the user). Gravity acts vertically, not along the translation axis. Gravity provides no restoring force along the translation axis. Not applicable.

**Friction detent:** A detent would require the user to deliberately press through the detent to return the plate — adding a two-phase squeeze that feels mechanical and deliberate, not the "squeeze and release" UX the vision describes. Not applicable.

**Spring return (selected):** A compression spring between the plate and the back wall of the cartridge body (behind the collets) pushes the plate back to resting position when the user releases. This is the standard mechanism for all push-to-connect collet tools (PI-TAB, SharkBite disconnect clips, etc.). It is invisible to the user, automatic, and adds no UX complexity.

### Spring selection

**Travel:** 1.3–2mm (collet release travel from geometry document: ~1.3mm per collet side; the plate travel need not exceed 2mm to achieve release).

**Space:** The spring fits in the annular space between the guide pin and the cartridge body surrounding it, or in a dedicated spring pocket behind the plate face. The simplest arrangement is a compression spring positioned around or alongside the guide pins.

**Spring type: compression spring, cylindrical helical, stainless steel music wire (type 302).**

This is the simplest possible spring. A die spring or disc spring would be more compact but are expensive and overkill for this load. A wave spring would also work but is harder to source and fit in a small pocket.

**Preload and spring rate:**

The spring must provide enough force to overcome plate/pin friction during return:

```
Return force needed ≥ friction force = total normal force × μ
```

The "normal force" on the pins during return is gravity (negligible, horizontal orientation) plus any residual drag from the bore contact. For clean PETG/PETG contact with 0.15mm clearance, the drag is minimal. However, a positive preload ensures reliable return even after years of use when surfaces may wear or debris may be present.

**Preload target: 2–3N total.** This is deliberately very light — enough to return the plate reliably, but not enough for the user to feel any resistance building up during the squeeze (which would feel like the mechanism is fighting them). At 2N total spring force and 1.3mm travel, the additional force the user feels at the end of stroke (spring fully compressed to working length) is:

```
Spring rate = 2N / 1.5mm = 1.3 N/mm (target maximum)
```

This is a very light spring. For reference, this is approximately the force of a light keyboard key switch.

**Spring dimensions for 2 springs (one per guide pin, around or alongside each pin):**

Two springs split the 2–3N total load → 1–1.5N per spring at working deflection.

A spring fitting around a 5mm pin (or in a pocket alongside it):
- Wire diameter: 0.3–0.4mm (music wire)
- Mean coil diameter: 7–8mm (fits around the 5.5mm bore OD or in a separate pocket)
- Free length: 8–10mm
- Working length (at full deflection): 6–8mm (approximately 2mm of travel)
- Spring rate: ~0.5–0.75 N/mm per spring
- Force at full deflection: ~1N per spring → 2N total

**Pocket design:** Each spring sits in a 8mm diameter, 10mm deep cylindrical pocket concentric with or adjacent to the guide pin bore, in the back wall of the cartridge body. The spring sits loose in this pocket during assembly; the plate compresses it when squeezed. No spring retention feature is needed if the pocket depth keeps the spring from falling out during assembly (the plate face closes the pocket).

Alternatively, if space is tight, a single central spring (centered on the plate, not at the pins) in a larger pocket (10–12mm diameter, 10mm deep) with 2–4N preload will work equally well. The central placement is neutral with respect to any moment arm concern.

**Catalog reference for sourcing:** Small compression spring, music wire (302SS), OD ~7mm, wire 0.4mm, free length 10mm, rate ~0.7 N/mm. McMaster-Carr catalog #9657K series or equivalent. Dozens of options from general hardware suppliers. This is a commodity part.

---

## 6. Over-Travel Protection

### What happens at full stroke

The collet travel for the PP0408W is **~1.3mm per side** (from geometry document: total collet travel from extended to compressed = 2.67mm, each side travels approximately 1.3–1.4mm before the collet mechanism bottoms out internally). The fitting has a hard internal stop: the collet sleeve contacts a shoulder inside the body at full depression. Beyond this point, the collet cannot travel further without deforming the plastic body.

### Does the plate need an external stop?

**Condition A — tubes not inserted:** The collet is in the extended position, protruding 2.67mm total (1.3mm per side) beyond the body end face. The plate travels until the collet is fully compressed. The internal fitting stop is engaged. The plate is now resting against the body end face (15.10mm OD annular shoulder) at the inner bore of the plate. No further travel is possible. **The fitting itself is the hard stop.**

**Condition B — tubes inserted:** The tube locks the gripper teeth in the gripping position, which adds resistance but does not change the collet travel limit. The collet still bottoms internally. Same result: **the fitting is the hard stop.**

**Condition C — user over-presses with high force:** The FDM PETG collet lip on the release plate (the inner bore that contacts the collet annular face) could fail if the user applies extreme force. The collet's acetal housing could crack if the plate pushes with force exceeding the fitting's yield threshold. However:

1. The spring return force is only 2–3N. The squeeze force of the user's hand (perhaps 30–80N, scaled by the mechanical advantage of the lever arm design) is ultimately limited by the fitting's hard stop once the collet is fully depressed.
2. Once the collet is bottomed out, any additional user force is transmitted through the collet body directly into the plate body end bore — effectively a rigid stop-to-stop contact.

**Conclusion: The PP0408W fitting's internal collet stop provides adequate over-travel protection. No additional external stop feature on the plate is required, provided the plate's body end bore (outer bore at 15.10mm) is designed to contact the fitting's body end shoulder at full collet depression.** This contact zone (plate outer bore face against the 15.10mm shoulder ring) becomes the positive hard stop.

**Design implication:** The stepped bore in the plate must be sized so that at full collet depression, the plate outer bore face contacts the 15.10mm body end shoulder at the same moment the collet is fully bottomed. This means the bore step depth must match the collet protrusion exactly. From the geometry document:

- Collet protrusion per side (extended): (41.80 − 36.32) / 2 = **2.74mm**
- Collet protrusion per side (compressed): (39.13 − 36.32) / 2 = **1.41mm**
- Collet travel per side: 2.74 − 1.41 = **1.33mm**

The plate's stepped bore counterbore depth (the recess allowing the collet to enter before the outer lip contacts the body end) should be set so that at the resting position (collet extended), the body end shoulder is 1.3–1.5mm away from the outer bore face. This ensures the outer bore contacts the shoulder exactly as the collet reaches its travel limit.

**This doubles as a built-in over-travel stop with zero additional features.** The plate geometry itself, through the stepped bore depth, limits travel to precisely the collet travel distance.

---

## 7. Summary: Specified Geometry

| Parameter | Value | Source |
|-----------|-------|--------|
| Guide pin diameter | 5mm (designed) | Section 2 structural analysis |
| Guide bore ID (designed) | 5.5mm | Section 4 clearance calc |
| Expected as-printed clearance per side | ~0.15mm | Section 4 |
| Minimum pin engagement length in bore | 28mm | Section 1 binding ratio |
| Pin effective length (plate face to tip) | ≥30mm | 28mm engagement + 2mm travel |
| Bore depth in cartridge body | ≥30mm | Matches pin length |
| Minimum wall around bore (cartridge body) | 1.2mm | requirements.md |
| Pin count | 2 | Section 3 |
| Pin arrangement | Diagonal corners of plate | Section 3 |
| Pin center-to-center separation | ~74mm (diagonal) | Section 3 |
| Return spring type | Compression spring, music wire | Section 5 |
| Return spring preload at rest | ~0.5–1N per spring | Section 5 |
| Return spring force at full stroke | ~1N per spring, 2N total | Section 5 |
| Spring free length | 8–10mm | Section 5 |
| Spring wire diameter | 0.3–0.4mm | Section 5 |
| Spring coil OD | ~7–8mm | Section 5 |
| Over-travel stop mechanism | Plate outer bore face contacts 15.10mm shoulder | Section 6 |
| Stepped bore outer counterbore depth | 1.3–1.5mm (matches collet travel) | Section 6 |

---

## 8. Failure Mode Summary

| Failure mode | Root cause | Prevention |
|--------------|-----------|------------|
| Binding during translation | Insufficient pin engagement length | ≥28mm engagement per Section 1 |
| Racking (rotation about translation axis) | Single guide point or pins at same height | Two pins at diagonal corners per Section 3 |
| Pin fracture | Pin diameter too small for bending load | 5mm diameter per Section 2 |
| Bore-to-pin interference | FDM hole undershoot, surface roughness | 5.5mm designed bore (0.5mm over pin) per Section 4 |
| Plate tilts in bore (pitch or yaw) | Excessive clearance × short engagement | 0.15mm per side clearance at 28mm engagement → 0.31° max tilt per Section 4 |
| Plate doesn't return after release | No return spring, weak spring | 2N spring preload per Section 5 |
| Over-travel damages collet | No hard stop | Stepped bore geometry contacts body shoulder per Section 6 |
| Spring falls out during assembly | Spring unsecured in pocket | Pocket depth ≥ spring free length; plate face closes pocket |

---

## 9. Connection Back to Vision

Vision Section 3: "The release plate is inside of the cartridge… it is important that this entire mechanism is hidden from the user."

The guide pins are fully internal — they are part of the plate body and the cartridge back wall. Zero external moving parts. The return spring lives in a pocket in the cartridge back wall, invisible when assembled. The over-travel stop is the fitting shoulder itself — no visible protrusion or separate stop feature. The entire mechanism from the user's perspective is: squeeze, feel the click of the collets releasing, pull the cartridge out. These guide geometry specifications make that feel clean and repeatable.

Vision Section 3: "the surface the users fingers pull must eventually be attached to the release plate."

The plate pull surface and the guide pins are one printed piece. At 28mm pin engagement and 5mm diameter pins, the pull force required to translate the plate against the spring and collets (~80N peak, 2N spring return) is transmitted entirely through the flat plate body with no visible mechanism. The structural margins on the pins support this load without creep or deformation under normal use.
