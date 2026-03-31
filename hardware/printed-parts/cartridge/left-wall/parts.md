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

- Channel width: 3.4mm (3.0mm panel/plate + 0.2mm clearance per side)
- Lip protrusion (LIP_H): 3.0mm from interior face (X=3.0 to X=6.0)
- Lip width (LIP_W): 2.0mm perpendicular to slide direction
- PASS_THRU_GAP: 5.4mm (LIP_W + CHANNEL_W) — gap at each end of a lip where a perpendicular panel needs to pass through

---

## Interior Spans

- Interior Y: 5.0mm to 128.0mm (123.0mm between front and back panel inner faces)
- Interior Z: 5.0mm to 73.6mm (68.6mm between bottom and top panel inner faces)

---

## How Rails Work

There are two kinds of rails on the wall, perpendicular to each other:

**Vertical rails** (lips run in Z) grip panels/plates in Y. The front panel, back panel, pump tray, and coupler tray each have a vertical rail pair. These rails have PASS_THRU_GAPs at top and bottom where horizontal rails cross.

**Horizontal rails** (lips run in Y) grip panels in Z. The bottom panel and top panel each have a horizontal rail pair. These rails have PASS_THRU_GAPs at front and back where the front/back panel vertical rails cross. They also have 3.4mm cutouts at each interior plate's Y position so the plates can slide down through them.

Bottom Lip A is the exception — it runs full width because it sits at Z=0..2, below where any vertical lips begin (Z=5.4).

---

## Interior Plate Y Positions

| Plate | Y center | Channel (Y) | Lip A (Y) | Lip B (Y) |
|-------|----------|-------------|-----------|-----------|
| Pump tray | 56.5 | 54.8..58.2 | 52.8..54.8 | 58.2..60.2 |
| Coupler tray | 30.0 (TODO) | 28.3..31.7 | 26.3..28.3 | 31.7..33.7 |

These are the same structure as the front/back panel rails — vertical lip pairs at fixed Y positions, running Z=5.4..73.6.

---

## Rail Feature Table

All lips are rectangular bars on the interior face (X=3.0), protruding to X=6.0.

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
| 6 | Bottom Lip A | Z=0.0..2.0 | Y=0..133.0 | None | Full width, below all vertical lips |
| 7 | Bottom Lip B | Z=5.4..7.4 | Y=5.4..127.6 | 3.4mm at each plate Y | Gapped front+back. Channel Z=2.0..5.4 |
| 8 | Top Lip A | Z=71.6..73.6 | Y=5.4..127.6 | 3.4mm at each plate Y | Gapped front+back |
| 9 | Top Lip B | Z=77.0..79.0 | Y=5.4..127.6 | 3.4mm at each plate Y | Gapped front+back. Channel Z=73.6..77.0 |

### Cutout positions in horizontal lips

Each cutout is 3.4mm wide in Y (= CHANNEL_W), centered on the plate's Y center. Applied to Bottom Lip B, Top Lip A, and Top Lip B. These are the same concept as the PASS_THRU_GAPs at the front/back ends — a gap in a horizontal lip so a vertical panel can pass through.

| Plate | Cutout Y range |
|-------|---------------|
| Pump tray | Y=54.8..58.2 |
| Coupler tray | Y=28.3..31.7 (TODO) |

---

## Print Orientation

Exterior face (X=0) down on build plate. Lips protrude upward. No overhangs. Footprint: 79.0mm × 133.0mm.
