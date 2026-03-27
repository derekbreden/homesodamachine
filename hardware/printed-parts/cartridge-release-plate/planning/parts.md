# Cartridge Release Plate

See `../../../planning/cartridge-architecture.md` for cartridge system design rationale.

**Coordinate system:** Origin at exterior front-bottom-left corner of shell. X = width (positive right). Y = depth (positive toward rear/fittings). Z = height (positive up). Front face (Y=0) is knob side. Rear face (Y=130) carries JG fittings. The release plate sits on the dock side of the rear wall (Y > 130).

---

## Mechanism Narrative

The release plate is the output element of the twist-release mechanism. It translates along the Y-axis to push all four JG collets inward simultaneously, releasing the dock tubes for cartridge removal. It is a single printed PETG piece that includes the plate body, the threaded strut, and two guide pins.

**What moves:**
- The **release plate + integral strut + integral guide pins** translates along the Y-axis between two positions:
  - **Retracted (operating):** Plate rear face is 3mm from the rear wall dock face. The 4x stepped bores do not engage the JG collets. Collets grip dock tubes naturally.
  - **Advanced (release):** Plate rear face is flush against the rear wall dock face (0mm gap). The stepped bores slide over the JG body ends and the inner lips push collets inward ~1.3mm, releasing all four tubes.
- The plate does not rotate. The two 6mm guide pins (integral, 15mm long) sliding in 6.5mm rear wall bushings prevent rotation. With 0.25mm radial clearance per pin and ~35mm pin spacing, maximum angular play is arctan(0.5/35) = 0.8 degrees.

**What is stationary:**
- The **cartridge shell rear wall** provides the bushing bores for the guide pins, the through-bore for the strut, the spring pocket reaction surfaces, and (on the interior side) the JG fitting pockets.
- The **JG fittings** are press-fit into the rear wall via their 9.31mm center body in 9.8mm pockets. They do not move. Only their collets (9.57mm OD sleeves) translate when pushed by the plate's inner lips.

**How this part participates in the mechanism:**
- The wing knob (see `../../cartridge-twist-release/planning/parts.md`) rotates but cannot translate (constrained by the front wall). The Tr12x3 2-start trapezoidal thread (6.0mm lead) converts knob rotation into strut translation along Y. The strut is integral to this plate, so the plate translates with it.
- Two guide pins (integral to the plate, 6.0mm diameter, 15mm long) slide in 6.5mm bushings in the rear wall, preventing rotation and ensuring parallel travel across the 59mm plate width.
- Two compression springs on the guide pins (between the rear wall dock face spring pocket floor and the plate rear face) push the plate to the retracted position. This is the normal operating state where collets grip the tubes.
- When the knob is twisted clockwise (from front), the thread pulls the strut toward the front wall (-Y direction). The strut is integral to the plate. From the dock side perspective, the plate advances toward the rear wall (+Y direction relative to the dock, but -Y in shell coordinates). The four stepped bores slide over the JG body ends and the inner lips push the collets inward, releasing all four tubes.

**Direction clarification:** The plate sits on the dock side of the rear wall (Y > 130 in shell coordinates). "Retracted" means the plate is further from the rear wall (further into the dock, higher Y value). "Advanced" means the plate moves toward the rear wall (lower Y value, toward Y=130). When the knob pulls the strut toward the front wall (-Y), the plate moves -Y, which means it moves toward the rear wall -- this is the "advanced" (release) position.

**Constraint chain (this part's role):**

```
[Strut pulls plate along -Y via integral connection]
    |
    v
[Release plate: TRANSLATES along Y, constrained rotationally by 2x guide pins in bushings]
    | 4x stepped bores engage JG body ends and collet end faces
    v
[Collet end faces pushed inward -> tubes release]

Constraints on this part:
  Rotation:    2x 6mm guide pins in 6.5mm rear wall bushings (0.25mm radial clearance)
               Pin spacing: ~35mm center-to-center -> 0.8 deg max angular play
  Y-axis:     driven by strut thread (advance via knob twist, retract via springs)
  Advance limit: plate rear face contacts rear wall dock face (0mm gap)
  Retract limit: thread engagement limit (knob bottoms against front wall)
  Return:     2x compression springs on guide pins (~0.5 N/mm, 12mm free length)
               1.0N total at retracted, 4.0N total at advanced
  Parallelism: 35mm pin spacing with 0.25mm clearance per pin -> <0.5mm lateral deviation
               across 59mm plate width at any stroke position
```

---

## 3D Printed Part: Release Plate with Integral Strut and Guide Pins

- **Type:** 3D printed (single piece)
- **Material:** PETG
- **Plate envelope:** 59W x 47H x 6D mm (X x Z x Y)
- **Total Y extent from plate dock-facing face to strut threaded tip:** ~136mm (6mm plate body + ~4mm rear wall passage + ~106mm interior span + ~4mm front wall passage + ~20mm threaded section protruding beyond front wall for knob engagement). The exact interior span adjusts to fit within the 122mm interior depth (Y=4 to Y=126).
- **Features:**

  ### Plate Body (59W x 47H x 6D mm)

  4x stepped bores in 2x2 grid, 40mm horizontal (X) x 28mm vertical (Z) center-to-center, matching JG fitting spacing in the rear wall.

  **Bore centers** (relative to plate bottom-left corner): (9.5, 9.5), (49.5, 9.5), (9.5, 37.5), (49.5, 37.5) in (X, Z) coordinates.

  Each stepped bore has three coaxial diameters. All dimensions are grounded in caliper-verified JG fitting measurements:

  - **Tube clearance hole:** 6.50mm diameter, through full 6mm plate thickness.
    - Must clear tube OD (6.30mm caliper-verified) but be smaller than collet ID (6.69mm caliper-derived: 9.57mm collet OD - 2 x 1.44mm wall thickness).
    - Design window: 6.30mm to 6.69mm (0.39mm total).
    - At 6.50mm: provides 0.20mm diametral clearance to tube and 0.19mm margin to collet ID.
    - The annular plate face between 6.50mm and 9.70mm (inner lip) contacts the collet end face to push it inward during release.

  - **Inner lip (collet hugger):** 9.70mm diameter, 2.0mm depth from dock-facing face.
    - Surrounds collet (9.57mm OD caliper-verified) with 0.065mm radial clearance (0.13mm diametral).
    - Purpose: lateral constraint to prevent collet wobble during the release stroke. The lip surrounds the collet cylindrical OD and prevents it from deflecting sideways as it is pushed inward.
    - **Note:** 0.065mm radial clearance is very tight for FDM printing. This may need to increase to 0.15-0.20mm radial (9.97-10.07mm bore) after test prints. The function (lateral constraint) works with up to ~0.5mm radial clearance.

  - **Outer bore (body end cradle):** 15.30mm diameter, 2.0mm depth from dock-facing face.
    - Surrounds JG body end (15.10mm OD caliper-verified) with 0.10mm radial clearance (0.20mm diametral).
    - Purpose: aligns the plate concentrically with each fitting during the release stroke. The body end is the fixed reference; the plate slides over it.

  - **Chamfers:**
    - 0.1mm chamfer at tube hole entry edge (prevents tube snagging during cartridge insertion)
    - 0.3mm x 45-degree lead-in chamfer at outer bore entry (dock-facing side, guides plate over body end)

  - **Axial depth stack:** 2.0mm outer bore + 2.0mm inner lip + 2.0mm structural back = 6.0mm total plate thickness. The outer bore and inner lip share the same 2.0mm-deep pocket from the dock-facing face; the inner lip is a smaller-diameter step within the outer bore.

  - **Edge-to-bore clearance:** 9.5mm from plate edge to nearest bore center. Minimum wall between outer bore edge (15.30mm dia = 7.65mm radius) and plate edge: 9.5 - 7.65 = **1.85mm**. This is thin but structurally adequate for the low forces involved (<5N per bore).

  ### Integral Strut

  - 12.0mm OD cylinder, extends from the center of the plate rear face (the face opposite the dock-facing/bore side).
  - Plate-local position: X=29.5, Z=23.5 (center of 59x47mm plate).
  - Total strut length from plate rear face: ~130mm (spans the cartridge interior from rear wall to front wall and protrudes ~20mm beyond front wall for knob engagement).
  - **Front end (Y-axis, furthest from plate):** 20mm of male Tr12x3 2-start trapezoidal thread.
    - Major diameter: 12.0mm
    - Minor diameter: 12.0 - 2 x 1.5mm = 9.0mm
    - Pitch: 3.0mm per start, lead: 6.0mm
    - Flank angle: 29 degrees
  - **Middle section:** Smooth 12.0mm cylinder. No thread engagement with the front or rear wall bores (12.5mm bore, 0.25mm radial clearance).
  - **Plate end:** Smooth integral transition to plate body. No thread or joint needed (one continuous printed piece).
  - **DESIGN GAP: Thread start alignment mark.** The strut has two thread starts (2-start thread). If a rotation stop feature is added to the knob (see twist-release parts.md DG-1), the knob must be assembled in the correct rotational orientation. A printed flat, notch, or raised dot on the strut near the threaded section would provide a visual alignment reference. Without this, the assembler must trial-and-error the orientation.

  ### Integral Guide Pins

  - 2x 6.0mm diameter PETG cylinders, 15mm long, extending from the plate rear face (toward dock, same direction as the stepped bores face).
  - Positioned symmetrically about the strut at plate-local coordinates: (~12, 23.5) and (~47, 23.5) in (X, Z), giving ~35mm center-to-center spacing. (Exact X positions must match the rear wall bushing positions at shell X=57 and X=91, which are 34mm apart -- plate-local X positions adjust accordingly based on plate mounting offset.)
  - Slide in 6.5mm bore printed bushings in the rear wall (0.25mm radial clearance per side).
  - Compression springs (6.5mm ID, 8-9mm OD) ride on these pins between the rear wall spring pocket floor and the plate rear face.

- **Interfaces:**
  - Guide pins slide in 6.5mm printed bushings in rear wall (0.25mm radial clearance per side)
  - Strut passes through 12.5mm rear wall bore (0.25mm radial clearance) and 12.5mm front wall bore (0.25mm radial clearance)
  - Strut front end threads into wing knob (Tr12x3 2-start, 12.0mm major diameter, 0.3mm radial thread clearance = 0.6mm diametral)
  - Stroke: 3.0mm total travel. Collet travel is ~1.3mm per side (caliper-verified). 3.0mm stroke provides 1.7mm margin beyond the required collet depression.
  - Stepped bores engage JG collets (9.57mm OD) and body ends (15.10mm OD) during release stroke
  - Return springs: 2x compression springs (~8-9mm OD, ~6.5mm ID, 12mm free length, ~0.5 N/mm) on guide pins, seated in ~8mm deep spring pockets in rear wall dock face, preloaded at all positions
- **Quantity:** 1
- **Print orientation:** Plate flat on build plate (dock-facing side up, so outer bore pockets face upward as shallow recesses). Strut extends vertically upward from the plate rear face (the face now on the build plate). Guide pins also extend vertically upward. This keeps the Tr12x3 thread profile in the XY plane for best FDM resolution. Print with brim for bed adhesion, 40-60mm/s for threaded sections, 0.12-0.16mm layer height on threaded sections, variable layer height (0.20mm for smooth shaft), 4+ perimeter walls, 30%+ infill.
- **Open questions:**
  - All three bore diameters (6.50, 9.70, 15.30mm) are constraint-based values within narrow design windows. Must be validated with single-bore test prints against the physical JG fitting.
  - Thread clearance: start with 0.3mm radial (0.6mm on diameter), tune with 15-minute Tr12x3 test print pair.
  - Guide pin straightness over 15mm length and wear over 36 cycles -- sand with 400+ grit and apply silicone grease to pins (not threads) if needed.
  - Inner lip (9.70mm) clearance to collet (9.57mm) is 0.065mm radial -- very tight for FDM. Likely needs 0.15-0.20mm radial after test prints.

---

## Stepped Bore Engagement Sequence

When the plate advances from retracted (3mm gap) to flush (0mm gap) against the rear wall dock face:

1. **At 2.0mm of travel (1.0mm gap remaining):** The outer bore (15.30mm) begins to slide over the JG body end (15.10mm OD, 12.08mm long). The body end protrudes ~4mm from the rear wall dock face (half of 12.08mm body end minus 4mm wall thickness, minus the portion inside the wall -- exact protrusion depends on fitting seating depth). The 0.3mm chamfer on the outer bore aids entry.
2. **At 2.5-3.0mm of travel:** The inner lip (9.70mm) reaches the collet (9.57mm OD) annular end face. The plate face between 6.50mm (tube hole) and 9.70mm (inner lip) contacts the collet end face.
3. **At 3.0mm of travel (flush):** The collet is pushed inward ~1.3mm (the full collet travel). The collet teeth disengage from the tube. All four tubes release simultaneously.

**DESIGN GAP: Engagement timing depends on JG body end protrusion.** The exact distance the body end protrudes from the rear wall dock face depends on how deeply the fitting sits in its rear wall pocket. The fitting center body (9.31mm, 12.16mm long) sits in a 4mm-thick wall, so the body end protrudes (12.08 - (12.16 - 4)/2) -- this calculation depends on whether the fitting is centered in the wall or seated against one shoulder. The protrusion distance determines at what plate travel the outer bore first engages the body end. This must be verified with the physical fitting in the printed wall.

---

## Purchased Parts

### Compression Springs (x2)

- ~8-9mm OD, ~6.5mm ID (must clear 6mm guide pin with 0.25mm radial gap), 12mm free length
- Spring rate: ~0.5 N/mm, stainless steel
- Ride on integral guide pins, seated in ~8mm deep counterbored spring pockets in the rear wall dock face
- Preloaded: ~1mm compression at retracted (operating) position, ~4mm at advanced (release) position
- Return force: ~0.5N per spring at retracted (1.0N total), ~2.0N per spring at advanced (4.0N total)
- Spring solid height must be <8mm (the pocket depth) to avoid bottoming out at full stroke

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **STEP generation standards:** `../../../planning/step-generation-standards.md`
- **JG fitting geometry:** `../../../off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md`
- **Release plate detailed analysis:** `research/release-plate.md`
- **Collet release research:** `research/collet-release.md`
- **Twist-release mechanism:** `../../cartridge-twist-release/planning/parts.md`
- **Shell interface:** `../../cartridge-shell/planning/parts.md`
