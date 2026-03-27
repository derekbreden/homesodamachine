# Cartridge Release Plate

See `../../../planning/cartridge-architecture.md` for cartridge system design rationale.

**Coordinate system:** Origin at exterior front-bottom-left corner of shell. X = width (positive right). Y = depth (positive toward rear/fittings). Z = height (positive up). Front face (Y=0) is knob side. Rear face (Y=130) carries JG fittings. The release plate sits on the dock side of the rear wall (Y > 130).

---

## Mechanism Narrative

The release plate is the output element of the twist-release mechanism. It translates along the Y-axis to push all four JG collets inward simultaneously, releasing the dock tubes for cartridge removal. It is a single printed PETG piece that includes the plate body, the threaded strut, and two guide pins.

**What moves:**
- The **release plate + integral strut + integral guide pins** translates along the Y-axis between two positions: retracted (3mm from the rear wall dock face, held by springs) and advanced (flush against the rear wall dock face, driven by the knob thread).
- The plate does not rotate. The two guide pins sliding in rear wall bushings prevent rotation.

**What is stationary:**
- The **cartridge shell rear wall** provides the bushing bores for the guide pins, the through-bore for the strut, and the reaction surface for the compression springs.
- The **JG fittings** are press-fit into the rear wall and do not move. Only their collets translate when pushed by the plate.

**How this part participates in the mechanism:**
- The wing knob (see `../../cartridge-twist-release/planning/parts.md`) rotates but cannot translate (constrained by the front wall). The Tr12x3 2-start trapezoidal thread converts knob rotation into strut translation along Y. The strut is integral to this plate, so the plate translates with it.
- Two guide pins (integral to the plate) slide in 6.5mm bushings in the rear wall, preventing rotation and ensuring parallel travel across the 59mm plate width.
- Two compression springs on the guide pins (between the rear wall dock face and the plate rear face) push the plate to the retracted position. This is the normal operating state where collets grip the tubes.
- When the knob is twisted clockwise (from front), the thread pulls the strut toward the front wall. From the dock side, this means the plate advances toward the rear wall. The four stepped bores slide over the JG body ends and the inner lips push the collets inward, releasing all four tubes.

**Constraint chain (this part's role):**

```
[Strut pulls plate along Y via integral connection]
    │
    ▼
[Release plate: TRANSLATES along Y, constrained rotationally by 2x guide pins in bushings]
    │ 4x stepped bores engage JG body ends and collets
    ▼
[Collet end faces pushed inward → tubes release]

Constraints on this part:
  Rotation:    2x 6mm guide pins in 6.5mm rear wall bushings (0.25mm radial clearance)
  Y-axis:     driven by strut thread at one end, limited by spring free length and thread engagement at the other
  Return:     2x compression springs on guide pins push plate to retracted position (away from rear wall on dock side)
  Parallelism: guide pin spacing (~35mm apart) ensures <0.3mm deviation across 59mm plate width
```

---

## 3D Printed Part: Release Plate with Integral Strut and Guide Pins

- **Type:** 3D printed (single piece)
- **Material:** PETG
- **Plate envelope:** 59W x 47H x 6D mm (X x Z x Y)
- **Total Y extent:** ~136mm (6mm plate + ~4mm rear wall passage + ~122mm interior span + ~4mm front wall passage)
- **Features:**
  - **Plate body (59W x 47H x 6D mm):**
    - 4x stepped bores in 2x2 grid, 40mm horizontal (X) x 28mm vertical (Z) center-to-center, matching JG fitting spacing
    - Bore centers at: (9.5, 9.5), (49.5, 9.5), (9.5, 37.5), (49.5, 37.5) relative to plate bottom-left corner
    - Each stepped bore has three coaxial diameters:
      - **Tube clearance hole:** 6.50mm diameter, through full 6mm plate thickness. Must clear tube (6.30mm caliper-verified OD) but be smaller than collet ID (6.69mm caliper-derived) so the plate face contacts the collet annular end face. Design window is 0.39mm (6.30 to 6.69mm). The 6.50mm value provides 0.20mm clearance to tube and 0.19mm margin to collet ID.
      - **Inner lip (collet hugger):** 9.70mm diameter, 2.0mm depth from dock-facing face. Surrounds collet (9.57mm OD caliper-verified) with 0.065mm radial clearance. Provides lateral constraint to prevent collet wobble during release stroke.
      - **Outer bore (body end cradle):** 15.30mm diameter, 2.0mm depth from dock-facing face. Surrounds JG body end (15.10mm OD caliper-verified) with 0.10mm radial clearance. Aligns and captures each body end during the release stroke.
    - 0.1mm chamfer at tube hole entry edge
    - 0.3mm x 45-degree lead-in chamfer at outer bore entry (dock-facing side)
    - Axial depth stack: 2.0mm outer bore + 2.0mm inner lip + 2.0mm structural back = 6.0mm total
    - Edge-to-bore clearance: 9.5mm from plate edge to nearest bore center (1.7mm minimum wall around outer bore)
  - **Integral strut:**
    - 12mm OD, extends from plate center (29.5, 23.5 in plate-local X, Z coordinates)
    - ~126mm total strut length from plate rear face
    - Front end: ~20mm of male Tr12x3 2-start trapezoidal thread (mates with wing knob)
    - Rear end (where strut meets plate): smooth transition, no thread needed (integral)
    - Middle section: smooth 12mm cylinder
    - A ~20mm threaded section is NOT needed at the plate end because the strut is integral (no joint)
  - **Integral guide pins:**
    - 2x 6mm diameter PETG cylinders, ~15mm long, extending from the plate rear face (toward dock, +Y from plate)
    - Positioned symmetrically about the strut, matching the 6.5mm bushing locations in the rear wall
    - Slide in 6.5mm bore printed bushings in the rear wall (0.25mm radial clearance)
    - Compression springs ride on these pins between the rear wall dock face and the plate rear face
- **Interfaces:**
  - Guide pins slide in 6.5mm printed bushings in rear wall (0.25mm radial clearance per side)
  - Strut passes through 12.5mm rear wall bore (0.25mm radial clearance) and 12.5mm front wall bore
  - Strut front end threads into wing knob (Tr12x3 2-start, 12.0mm major diameter, 0.3mm radial thread clearance)
  - Stroke: 3.0mm total travel (min 2.5mm required). Collet travel is ~1.3mm per side (caliper-verified), so 3mm stroke provides ~1.7mm margin.
  - Stepped bores engage JG collets (9.57mm OD) and body ends (15.10mm OD) during release stroke
  - Return springs: 2x compression springs (~8-9mm OD, ~6.5mm ID, 12mm free length, ~0.5 N/mm) on guide pins, seated in ~8mm deep spring pockets in rear wall dock face, preloaded at all positions
  - Must maintain <0.3mm parallelism deviation across 59mm plate width during full stroke
- **Quantity:** 1
- **Print orientation:** Plate flat on build plate (dock-facing side up), strut pointing up (vertical). This keeps the thread profile in the XY plane for best FDM resolution. Print with brim for bed adhesion, 40-60mm/s for threaded sections, 0.12-0.16mm layer height on threaded sections, variable layer height (0.20mm for smooth shaft), 4+ perimeter walls, 30%+ infill.
- **Open questions:**
  - All three bore diameters are constraint-based ranges, not fixed values. Must be validated with single-bore test prints against physical fitting (see `research/release-plate.md` Section 7.1).
  - Thread clearance: start with 0.3mm radial (0.6mm on diameter), tune with 15-minute Tr12x3 test print pair.
  - Guide pin straightness and wear over 36 cycles -- sand with 400+ grit and apply silicone grease if needed.

---

## Sub-Assembly: Twist-Release Mechanism

Composed of: release plate with integral strut + guide pins (this part) + wing knob + 2x compression springs.

- **Function:** Half-turn twist releases all 4 JG collets simultaneously for cartridge removal
- **Operating state (knob loose):** Springs hold plate retracted (3mm from rear wall dock face). Collets grip tubes. No user action needed.
- **Release state (knob twisted 180 deg CW from front):** Thread pulls plate flush against rear wall dock face. Stepped bores push all 4 collets inward. Tubes release. User pulls cartridge out by knob wings.
- **Self-locking:** Lead angle ~9 deg < friction angle ~17 deg for PETG-on-PETG. The thread does not back-drive under the ~2-3N spring return force.
- **Total collet release force:** 12-20N (4 fittings x 3-5N each). Thread mechanical advantage at 45mm knob wingspan reduces required fingertip force to ~1-2N.

---

## Purchased Parts

### Compression Springs (x2)

- ~8-9mm OD, ~6.5mm ID (must clear 6mm guide pin), 12mm free length
- Spring rate: ~0.5 N/mm, stainless steel
- Ride on integral guide pins, seated in ~8mm deep counterbored spring pockets in the rear wall dock face
- Preloaded: ~1mm compression at retracted (operating) position, ~4mm at advanced (release) position
- Return force: ~0.5N per spring at retracted, ~2N per spring at advanced

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **STEP generation standards:** `../../../planning/step-generation-standards.md`
- **JG fitting geometry:** `../../../off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md`
- **Release plate detailed analysis:** `research/release-plate.md`
- **Collet release research:** `research/collet-release.md`
- **Twist-release mechanism:** `../../cartridge-twist-release/planning/parts.md`
- **Shell interface:** `../../cartridge-shell/planning/parts.md`
