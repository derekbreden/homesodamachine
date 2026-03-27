# Cartridge Release Plate

See `../../../planning/cartridge-architecture.md` for cartridge system design rationale.

---

## 3D Printed Part: Release Plate

- **Type:** 3D printed
- **Material:** PETG
- **Envelope:** 59W x 47H mm plate, ~136mm total Y extent (plate + integral strut)
- **Features:**
  - 4x stepped bores in 2x2 grid, 40mm horizontal x 28mm vertical center-to-center (matches JG fitting spacing):
    - Bore centers at: (9.5, 9.5), (49.5, 9.5), (9.5, 37.5), (49.5, 37.5) relative to plate bottom-left corner
    - Tube clearance hole: between 6.30mm and 6.69mm diameter, through full thickness. Must clear tube (6.30mm caliper-verified) but be smaller than collet ID (6.69mm) so plate face contacts collet end face. **Only 0.39mm design window.**
    - Inner lip (collet hugger): just over 9.57mm diameter, 2.0mm depth. Surrounds collet (9.57mm OD, caliper-verified).
    - Outer bore (body end cradle): just over 15.10mm diameter, 2.0mm depth. Surrounds body end (15.10mm OD, caliper-verified).
    - 0.1mm chamfer at tube hole entry edge
    - 0.3mm x 45-degree lead-in chamfer at outer bore entry
  - Axial depth stack: 2.0mm outer bore + 2.0mm inner lip + 2.0mm structural back = 6.0mm total
  - Edge-to-bore clearance: 9.5mm from plate edge to nearest bore center (1.7mm minimum wall around outer bore)
  - **Integral strut:** 12mm OD Tr12x3 2-start trapezoidal threaded strut extending from plate center (29.5, 23.5). ~126mm total strut length (4mm rear wall thickness + 122mm interior span). Threaded sections (~20mm each) at both ends, smooth 12mm cylinder in the middle. Front end threads into the wing knob. The strut is one continuous printed piece with the plate.
  - **Integral guide pins:** 2x 6mm diameter PETG pins, ~15mm long, extending from the plate rear face. Slide in 6.5mm bore printed bushings in the rear wall (0.25mm radial clearance). Prevent plate rotation and ensure parallel travel during 3mm stroke.
- **Interfaces:**
  - Slides on integral guide pins through 6.5mm printed bushings in rear wall
  - Stroke: 3.0mm (min 2.5mm) — collet travel ~1.3mm per side (caliper-verified), 3mm provides ~1.7mm margin
  - Strut passes through 12.5mm rear wall bore, front end threads into wing knob (half turn = 3mm plate travel)
  - Stepped bores engage JG collets (9.57mm OD) and body ends (15.10mm OD)
  - Return spring: 2x small compression springs on guide pins between rear wall and plate
  - Must maintain <0.3mm parallelism deviation across 59mm plate width during full stroke
- **Quantity:** 1
- **Print orientation:** Plate flat on build plate, strut pointing up (vertical). This keeps the thread profile in the XY plane for best resolution. Print with brim for bed adhesion, 40-60mm/s for threaded sections, 0.12-0.16mm layer height on threaded sections, 4+ perimeter walls.
- **Open:** All three bore diameters are constraint-based ranges, not fixed values. Must be validated with single-bore test prints against physical fitting (see `research/release-plate.md` Section 7.1).

---

## Sub-Assembly: Twist-Release Mechanism

Composed of: release plate (with integral strut + guide pins) + wing knob + 2x compression springs.

- **Function:** Half-turn twist releases all 4 JG collets simultaneously
- **Actuation:** 180-degree knob rotation → 3mm axial plate travel via Tr12x3 2-start trapezoidal thread (6mm lead)
- **Force path:** Hand → wing knob → threaded strut (integral to plate) → release plate → 4x collets
- **Self-locking:** Lead angle ~9 deg < friction angle ~17 deg for PETG-on-PETG prevents accidental release
- **Total required force at collets:** 12-20N (4 fittings x 3-5N each)

---

## Purchased Parts

### Compression Springs (x2)

- ~5mm OD x 10mm free length
- Spring rate: ~0.5 N/mm
- Ride on integral guide pins between rear wall and plate
- Returns release plate to retracted position (collets grip)

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **STEP generation standards:** `../../../planning/step-generation-standards.md`
- **JG fitting geometry:** `../../../off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md`
- **Release plate detailed analysis:** `research/release-plate.md`
- **Collet release research:** `research/collet-release.md`
- **Release mechanism alternatives:** `research/release-mechanism-alternatives.md`
- **Cam lever:** `../../cartridge-cam-lever/planning/parts.md`
- **Shell interface:** `../../cartridge-shell/planning/parts.md`
