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

## How Rails Work

Same as left wall. See left wall parts.md for full explanation.

Two kinds of rails, perpendicular to each other:
- **Vertical rails** (front panel, back panel, pump tray, coupler tray) — lips run in Z, grip in Y, gapped at top and bottom
- **Horizontal rails** (bottom panel, top panel) — lips run in Y, grip in Z, gapped at front and back, with 3.4mm cutouts at each interior plate's Y position

---

## Rail Feature Table

All Y and Z positions identical to left wall. Only X protrusion direction differs (lips at X=-3..0 instead of X=3..6).

### Vertical lips (run in Z, grip in Y)

| # | Name | Y position | Z run span | Notes |
|---|------|-----------|------------|-------|
| 2 | Front panel Lip A | Y=0.0..2.0 | Z=5.4..73.6 | Gapped bottom+top |
| 3 | Front panel Lip B | Y=5.4..7.4 | Z=5.4..73.6 | Channel Y=2.0..5.4 |
| 4 | Back panel Lip A | Y=125.6..127.6 | Z=5.4..73.6 | Gapped bottom+top |
| 5 | Back panel Lip B | Y=131.0..133.0 | Z=5.4..73.6 | Channel Y=127.6..131.0 |
| 10 | Pump tray Lip A | Y=52.8..54.8 | Z=5.4..73.6 | Gapped bottom+top |
| 11 | Pump tray Lip B | Y=58.2..60.2 | Z=5.4..73.6 | Channel Y=54.8..58.2 |
| 12 | Coupler tray Lip A | Y=26.3..28.3 | Z=5.4..73.6 | Gapped bottom+top. Y position TODO |
| 13 | Coupler tray Lip B | Y=31.7..33.7 | Z=5.4..73.6 | Channel Y=28.3..31.7. Y position TODO |

### Horizontal lips (run in Y, grip in Z)

| # | Name | Z position | Y run span | Cutouts | Notes |
|---|------|-----------|------------|---------|-------|
| 6 | Bottom Lip A | Z=0.0..2.0 | Y=0..133.0 | None | Full width |
| 7 | Bottom Lip B | Z=5.4..7.4 | Y=5.4..127.6 | 3.4mm at each plate Y | Channel Z=2.0..5.4 |
| 8 | Top Lip A | Z=71.6..73.6 | Y=5.4..127.6 | 3.4mm at each plate Y | |
| 9 | Top Lip B | Z=77.0..79.0 | Y=5.4..127.6 | 3.4mm at each plate Y | Channel Z=73.6..77.0 |

### Cutout positions in horizontal lips

| Plate | Cutout Y range |
|-------|---------------|
| Pump tray | Y=54.8..58.2 |
| Coupler tray | Y=28.3..31.7 (TODO) |

---

## Mirror Construction

Build left-wall geometry (lips at X=3..6), mirror across YZ plane (negate X), translate +3 in X. Result: body at X=0..3, lips at X=-3..0.

---

## Print Orientation

Exterior face (X=3.0) down on build plate. Lips protrude upward. No overhangs. Footprint: 79.0mm × 133.0mm.
