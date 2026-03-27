# Cartridge Release Plate

See `../../../planning/cartridge-architecture.md` for cartridge system design rationale.

---

## 3D Printed Part: Release Plate

- **Type:** 3D printed
- **Material:** PETG
- **Envelope:** 59W x 47H x 6D mm (enlarged from 55x43mm to accommodate 15.10mm body end OD)
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
  - 2x guide pin slots: 3.3mm wide x 7.3mm long, positioned at X=(-5.5, 23.5) and X=(64.5, 23.5) relative to plate bottom-left
  - Push rod contact point: centered boss on back face at (29.5, 23.5), 8mm diameter x 1mm proud
- **Interfaces:**
  - Slides on 2x 3mm steel dowel pins mounted in outer shell rear wall
  - Stroke: 3.0mm (min 2.5mm) — collet travel ~1.3mm per side (caliper-verified), 3mm provides ~1.7mm margin
  - Receives axial push from cam lever push rod on back face
  - Stepped bores engage JG collets (9.57mm OD) and body ends (15.10mm OD)
  - Return spring: 2x small compression springs on dowel pins
  - Must maintain <0.3mm parallelism deviation across 59mm plate width during full stroke
- **Quantity:** 1
- **Open:** All three bore diameters are constraint-based ranges, not fixed values. Must be validated with single-bore test prints against physical fitting (see `research/release-plate.md` Section 7.1).

---

## Sub-Assembly: Release Mechanism

Composed of: cam lever + pivot pin + E-clip + push rod + release plate + 2x dowel pins + 2x compression springs.

- **Function:** Single lever flip releases all 4 JG collets simultaneously
- **Actuation:** 180-degree lever rotation → 3mm axial plate travel via 1.5mm eccentric cam
- **Force path:** Hand → lever handle (76mm arm) → eccentric cam → push rod (118mm, 5mm steel) → release plate → 4x collets
- **Mechanical advantage:** ~10:1
- **Total required force at collets:** 12-20N (4 fittings x 3-5N each)
- **Required hand force:** ~2-3N

---

## Purchased Parts

### Compression Springs (x2)

- ~5mm OD x 10mm free length, 3.2mm ID (rides on 3mm dowel pin)
- Spring rate: ~0.5 N/mm
- Returns release plate to retracted position

### Steel Dowel Pins (x2)

- 3mm diameter x 20mm long
- Press-fit into shell rear wall (10mm engagement), 10mm protrudes for plate travel + spring

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
