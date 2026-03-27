# Two-Port Cap

Custom cap for Platypus bags with two fluid ports: P1 (main fluid, JG bulkhead) and P2 (dip tube, barb fitting).

See `../../../planning/architecture.md` for system architecture.

---

## 3D Printed or Machined Part: Custom Two-Port Cap

- **Type:** 3D printed or machined
- **Material:** PETG, nylon, or machined Delrin (food-safe, threaded)
- **Envelope:** 28mm thread diameter x ~25H mm
- **Features:**
  - 28mm thread to match Platypus bag opening (standard 28mm PCO-1881 or equivalent)
  - Two through-holes:
    - P1 (main fluid port): 15.9mm (5/8") hole for JG PP1208W bulkhead fitting
    - P2 (dip tube port): ~8mm hole for 1/4" barb fitting
  - Usable cap face diameter: ~24mm (inside thread ring)
  - P1 and P2 arranged to fit within 24mm usable diameter
  - O-ring groove or gasket face for thread seal
- **Interfaces:**
  - Threads onto Platypus bag 28mm opening
  - P1 JG fitting exterior connects to bag-to-pump tubing (b->i direct line)
  - P2 barb fitting exterior connects to dip tube air bleed line (to v9/v10)
  - Interior: P2 has dip tube hard tube insertion
- **Quantity:** 2 (one per bag)
- **Open:** Exact thread spec (measure from physical bag), JG + barb spacing within 24mm, material selection

## Purchased Part: Dip Tube (Hard Tube)

- **Material:** 1/4" OD (6.35mm) hard polyethylene or polyurethane
- **Envelope:** 6.35mm OD x ~350mm length (full bag length)
- **Features:**
  - Runs from P2 barb fitting in cap up through bag interior to sealed end
  - Slight flex to follow bag interior curvature on 35-degree diagonal
- **Quantity:** 2 (one per bag)
- **Open:** Exact tube length (~340-350mm)

## Purchased Part: 1/4" Barb Fitting for P2 (x2)

- Brass or food-grade nylon
- ~8mm diameter x ~15mm length
- Barb grips 1/4" OD hard dip tube on interior, connects to silicone tubing on exterior

## Purchased Part: JG PP1208W Bulkhead Union for P1 (x2)

Full geometry: `../../../off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md`

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **Dip tube analysis:** `research/dip-tube-analysis.md`
- **Valve routing (v9/v10 dip tube evacuation):** `../../../planning/research/valve-architecture.md`
- **Bag cradle:** `../../bag-cradle/planning/parts.md`
