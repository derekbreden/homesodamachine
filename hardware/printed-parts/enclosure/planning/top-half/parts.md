# Enclosure Top Half — Parts Specification

**Date:** 2026-03-29
**Inputs:** concept.md, synthesis.md, top-half/spatial-resolution.md, bottom-half/parts.md (interface reference)
**Output:** generate_step_cadquery.py → enclosure-top-half-cadquery.step

---

## Rubric A — Part Identity

| Field | Value |
|---|---|
| Part name | Enclosure top half |
| Part number | ENC-TOP-001 |
| Material | ASA, matte black |
| Print orientation | Enclosure top face on build plate (inverted) |
| Build volume | 220×300×215.5mm — fits 325×320×320mm with 105mm Z margin |
| Layer height | 0.1mm (consumer surface quality) |
| Perimeter count | 6 (at 0.4mm nozzle = 2.4mm wall) |
| Infill | 40% gyroid |

---

## Rubric B — Coordinate System

Global enclosure frame. Origin at exterior bottom-left-front corner of assembled enclosure.
- X: 0→220 (left to right), Y: 0→300 (front to back), Z: 0→400 (bottom to top)
- Top half envelope: Z:[184.5, 400] (seam lip at Z=184.5, top face at Z=400)
- Print Z: top face on build plate → print frame Z = enclosure Z inverted

---

## Rubric C — Feature Table

| # | Feature | Operation | Shape | Position | Dimensions | Notes |
|---|---|---|---|---|---|---|
| 1 | Box body | Add | Rect box | Z:[184.5, 400] | 220×300×215.5mm | Seam lip at Z:[184.5, 185] |
| 2 | Interior cavity | Remove | Rect box | X:[2.4,217.6] Y:[2.4,297.6] Z:[185,397.6] | 215.2×295.2×212.6mm | 2.4mm ceiling; open seam face |
| 3 | Groove | Remove | 5 rect segments | 2mm setback from exterior, Z:[185,189.2] | 3.1mm W × 4.2mm D | Matches bottom tongue; 0.05mm clearance |
| 4 | Snap ledge pockets (×24) | Remove | Rect slots | Front/rear: arm X-centers; Left/right: arm Y-centers | 8.2mm W × 2.4mm D × 3.0mm H | Cut through wall at Z:[185,188] |
| 5 | Alignment pin sockets (×4) | Remove | Cylinders Z | (10,10),(210,10),(10,290),(210,290) | Ø4.15mm × 9.0mm deep | Z:[185,194] |
| 6 | Rear wall thickening | Add | Rect slab | X:[15,205] Y:[296.5,297.6] Z:[290,330] | 190×1.1×40mm | 3.5mm total wall at port locations |
| 7 | Port holes (×5) | Remove | Cylinders Y | X=25,60,110,160,195 at Z=310 | Ø17.2mm through rear wall | PP1208W-US bulkhead fittings |
| 8 | Boss rings (×5) | Add | Annular discs Y | Same X,Z as ports; Y:[294.5,296.5] | OD=22mm ID=17.2mm 2.0mm thick | Distribute nut clamping load |
| 9 | Rear exterior bays | Remove | Rect/cylinder | Group A X:[15,70], B X=110, C X:[150,205] | 1.0mm deep, bay dims vary | Visual port grouping |
| 10 | Spine oval slot bosses+slots (×4) | Add+Remove | Boss+rect slot | L: X:[2.4,10.9]; R: X:[209.1,217.6] | Boss 8.5mm deep, slot 10.2×6.2mm | Z=235 and Z=275; Z-axis engagement |
| 11 | Cradle locating ledges (×4) | Add | Rect ridges | Left: X:[2.4,5.4]; Right: X:[214.6,217.6] | 3×3mm; Y:[2.4,297.6] | Z:[195,198] and Z:[295,298] |
| 12 | Electronics tray rails (×2) | Add | Rect ledges | Y:[294.6,297.6] X:[2.4,217.6] | 3mm deep × 3mm tall | Z:[340,343] and Z:[370,373] |
| 13 | Exterior edge fillets | Modify | R=3mm | 4 vertical corners | Full Z height | try/except |
| 14 | Seam lip chamfer | Modify | 0.3mm×45° | Exterior bottom perimeter Z=184.5 | 0.3mm | Assembly entry guide |

---

## Rubric D — Interface Dimensions (seam face, matches bottom half exactly)

| Interface | Bottom half value | Top half provides |
|---|---|---|
| Seam plane | Z=185 | Z=185 (interior seam face) |
| Tongue position (front-left) | X:[3.5,31.5] Y:[2.0,5.0] | Groove X:[3.5,31.5] Y:[1.95,5.05] |
| Tongue position (rear) | X:[3.5,216.5] Y:[295.0,298.0] | Groove X:[3.5,216.5] Y:[294.95,298.05] |
| Arm front X-centers | 40,80,120,160,200 | Pockets at same X |
| Arm left/right Y-centers | 40,80,120,160,200,240,280 | Pockets at same Y |
| Pin positions | (10,10),(210,10),(10,290),(210,290) Ø4.0mm | Sockets Ø4.15mm at same XY |
| Seam reveal | Bottom exterior ends at Z=185 | Top exterior starts at Z=184.5 (0.5mm lap) |

---

## Rubric E — Wall Thickness

| Location | Thickness | Reasoning |
|---|---|---|
| Exterior walls | 2.4mm | 6 perimeters; consistent with bottom half |
| Rear wall at port zone | 3.5mm | PP1208W minimum 3.0mm, target 3.0–4.0mm |
| Interior ceiling | 2.4mm | Structural; matches wall thickness |
| Cradle ledge root | 3.0mm + wall = 5.4mm local | Ledge adds 3mm to inner wall |
| Spine boss | 8.5mm local | Required for 8mm post engagement depth |

---

## Rubric F — Overhang Mitigation (print inverted)

When printed inverted (top face on build plate), Z direction is reversed. Features that would overhang in the inverted print:

| Feature | Overhang concern | Resolution |
|---|---|---|
| Groove | Opens upward in inverted print (toward build plate) | Slot grows from build plate surface — no overhang |
| Snap ledge pockets | Open upward in inverted print | Clean upward slots — no overhang |
| Cradle ledges | Bottom face overhangs in inverted print | 45° chamfer on underside — not yet in STEP (DESIGN GAP) |
| Electronics rails | Bottom face overhangs in inverted print | 45° chamfer on underside — not yet in STEP (DESIGN GAP) |
| Boss ring underside | Outer edge overhangs in inverted print | 45° chamfer on outer edge — not yet in STEP (DESIGN GAP) |
| Spine slot bosses | Bottom face of boss overhangs | 45° chamfer required — not yet in STEP (DESIGN GAP) |

**NOTE:** The 45° overhang chamfers for features 8, 10, 11, 12 are specified in the concept but not yet implemented in the STEP. These are interior features; the Bambu H2C can bridge ≤15mm at 45° without explicit support. At the sizes involved (3mm ledge, 3mm rail), the overhang is printable without support but would benefit from chamfers in a production STEP. These are flagged for a subsequent geometry pass once the interfacing parts (spine, dock cradle, electronics tray) are designed and the exact ledge geometry is confirmed.

---

## Rubric G — Validation Results

55 of 55 checks passed. Single body. Valid solid.

| Check | Result |
|---|---|
| Solid validity | PASS |
| Single body | PASS — 1 body |
| Volume | PASS — 732,972 mm³ (5.2% of envelope) |
| Bounding box | PASS — X:[0,220] Y:[0,300] Z:[184.5,400] |
| All 51 feature probes | PASS |

---

## Rubric H — Design Gaps

| Gap | Description | Impact | Resolution path |
|---|---|---|---|
| Overhang chamfers | 45° chamfers on ledge/rail/boss undersides not in STEP | Printable without, but preferred for quality | Add in next geometry pass after interfacing parts confirmed |
| S3 retention bosses | M2.5 retention bracket not in top half (no feature needed — bracket mounts to bottom half pocket) | None for top half | Bottom half design gap |
| Funnel mount interface | Top face reserved zone (X:[70,150] Y:[80,140]) not detailed | Top face is flat placeholder | Add when funnel concept is written |
| Electronics tray rail geometry | Rail cross-section confirmed as 3×3mm ledge; retaining lip geometry TBD | Rail is present; lip requires tray snap geometry to finalize | Update when electronics tray concept is written |
| Spine slot Y-position | Slots at Y=150 (center of interior depth); actual spine post Y TBD | Placeholder centred in bag zone | Update when spine concept finalises post Y |
