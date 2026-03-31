# Right Wall — Parts Specification

Build sequence: Season 2, Phase 7, Item 18
Mirror of left wall across the X axis.

---

## Coordinate System

Origin: front-bottom-interior corner (X=0, Y=0, Z=0)

- X: wall thickness. Interior face X=0 (facing -X into cartridge), exterior face X=3.0mm. Lips protrude -X to X=-3.0mm.
- Y: front-to-back. Y=0 = front, Y=133.0mm = back. Same as left wall.
- Z: height. Z=0 = bottom, Z=79.0mm = top. Same as left wall.

---

## Dimensions

- Wall body: 3.0mm (X) × 133.0mm (Y) × 79.0mm (Z)
- Wall body + lips: 6.0mm (X) — from X=-3.0mm to X=3.0mm

---

## Rail Parameters

Identical to left wall. Only X direction is mirrored (lips protrude -X instead of +X).

- Channel width: 3.4mm
- Lip protrusion (LIP_H): 3.0mm (from X=0 to X=-3.0)
- Lip width (LIP_W): 2.0mm
- PASS_THRU_GAP: 5.4mm

---

## Interior Spans

Same as left wall:
- Interior Y: 5.0mm to 128.0mm (123.0mm)
- Interior Z: 5.0mm to 73.6mm (68.6mm)

---

## Rail Feature Table

All Y and Z positions identical to left wall. Only X protrusion direction differs.

| # | Name | Sep Axis Position | Run Span | Notes |
|---|------|-------------------|----------|-------|
| 1 | Wall body | — | — | 3.0 × 133.0 × 79.0 base slab |
| 2 | Front panel Lip A | Y=0.0..2.0 | Z=5.4..73.6 | Gapped bottom+top |
| 3 | Front panel Lip B | Y=5.4..7.4 | Z=5.4..73.6 | Channel Y=2.0..5.4 |
| 4 | Back panel Lip A | Y=125.6..127.6 | Z=5.4..73.6 | Gapped bottom+top |
| 5 | Back panel Lip B | Y=131.0..133.0 | Z=5.4..73.6 | Channel Y=127.6..131.0 |
| 6 | Bottom Lip A | Z=0.0..2.0 | Y=0..133.0 | Full width |
| 7 | Bottom Lip B | Z=5.4..7.4 | Y=5.4..127.6 | Gapped front+back. Channel Z=2.0..5.4 |
| 8 | Top / plate-top Lip A | Z=71.6..73.6 | Y=5.4..127.6 | Gapped front+back. Shared: top panel + plate top edge |
| 9 | Top / plate-top Lip B | Z=77.0..79.0 | Y=5.4..127.6 | Gapped front+back. Channel Z=73.6..77.0 |
| 10 | Plate bottom Lip A | Z=1.3..3.3 | Y=5.4..127.6 | Gapped front+back |
| 11 | Plate bottom Lip B | Z=6.7..8.7 | Y=5.4..127.6 | Gapped front+back. Channel Z=3.3..6.7 |

---

## Mirror Construction

Build left-wall geometry (lips at X=3..6), mirror across YZ plane (negate X), translate +3 in X. Result: body at X=0..3, lips at X=-3..0.

---

## Print Orientation

Exterior face (X=3.0) down on build plate. Lips protrude upward. No overhangs. Footprint: 79.0mm × 133.0mm.
