# Left Wall — Parts Specification

Build sequence: Season 2, Phase 7, Item 17

---

## Coordinate System

Origin: front-bottom-exterior corner (X=0, Y=0, Z=0)

- X: wall thickness. Exterior face X=0, interior face X=3.0mm. Lips protrude +X to X=6.0mm.
- Y: front-to-back. Y=0 = front, Y=133.0mm = back.
- Z: height. Z=0 = bottom, Z=79.0mm = top.

---

## Dimensions

- Wall body: 3.0mm (X) × 133.0mm (Y) × 79.0mm (Z)
- Wall body + lips: 6.0mm (X) × 133.0mm (Y) × 79.0mm (Z)

---

## Rail Parameters

- Channel width: 3.4mm (3.0mm panel + 0.2mm clearance per side)
- Lip protrusion (LIP_H): 3.0mm from interior face (X=3.0 to X=6.0)
- Lip width (LIP_W): 2.0mm perpendicular to slide direction
- PASS_THRU_GAP: 5.4mm (LIP_W + CHANNEL_W) — gap at each end of a lip where a perpendicular panel needs to pass through

---

## Interior Spans

- Interior Y: 5.0mm to 128.0mm (123.0mm between front and back panel inner faces)
- Interior Z: 5.0mm to 73.6mm (68.6mm between bottom and top panel inner faces)

---

## Rail Feature Table

All lips are rectangular bars on the interior face (X=3.0), protruding to X=6.0.

Each lip has a PASS_THRU_GAP (5.4mm) cut from each end where a perpendicular rail crosses, so panels can be inserted without colliding with crossing lip bars.

Exception: Bottom Lip A runs full Y width because it sits at Z=0..2, below where vertical lips begin (Z=5.4).

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

Total: 1 wall body + 10 lip bars = 11 features.

---

## Rail Channel Summary

| Channel | Axis | Range | Slides in |
|---------|------|-------|-----------|
| Front panel | Y | 2.0..5.4mm | Z (down from top) |
| Back panel | Y | 127.6..131.0mm | Z (down from top) |
| Bottom panel | Z | 2.0..5.4mm | Y (from front) |
| Top panel | Z | 73.6..77.0mm | Z (down from top) |
| Plate bottom (pump+coupler tray) | Z | 3.3..6.7mm | Y (from front) |
| Plate top (pump+coupler tray) | Z | 73.6..77.0mm | Y (shared with top panel rail) |

---

## Print Orientation

Exterior face (X=0) down on build plate. Lips protrude upward. No overhangs. Footprint: 79.0mm × 133.0mm.
