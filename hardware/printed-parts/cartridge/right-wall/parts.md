# Right Wall — Parts Specification

Build sequence: Season 2, Phase 7, Item 18
Part: Right wall panel — mirror of left wall. Geometrically identical to the left wall, mirrored across the X axis.

---

## Derivation

The right wall spec is derived entirely from the left wall spec
(`hardware/printed-parts/cartridge/left-wall/planning/parts.md`).
All Y and Z dimensions are identical. Only the X axis is mirrored.

Left wall: exterior face at X=0, interior face at X=WALL_T=3.0mm, lips protrude in +X.
Right wall: exterior face at X=WALL_T=3.0mm, interior face at X=0, lips protrude in -X.

In the cartridge assembly:
- The left wall's interior face (at X=3.0mm in left-wall local coordinates) faces +X (into the cartridge interior).
- The right wall's interior face (at X=0 in right-wall local coordinates) faces -X (into the cartridge interior).
- The interior X span between the two interior faces = 140.0mm (set by the interior plate width).

---

## Coordinate System

Origin: right wall front-bottom-interior corner (interior face, front edge, bottom edge).

- X: wall thickness axis. X=0 = interior face (facing -X into cartridge interior, toward left wall). X=WALL_T=3.0mm = exterior face (facing away from interior, toward the right side of the appliance).
- Y: front-to-back axis. Y=0 = cartridge front. Y increases toward the back. Same as left wall.
- Z: height axis. Z=0 = cartridge bottom. Z increases upward. Same as left wall.

Rail lips protrude from the interior face (X=0) in the -X direction, reaching X=-LIP_H=-3.0mm at tips.

**Right wall outer envelope (wall body only):** 3.0mm (X) × 133.0mm (Y) × 79.0mm (Z)
**Right wall envelope with rail lips:** 6.0mm (X) × 133.0mm (Y) × 79.0mm (Z)

---

## Dimensions

All dimensions are wall-local coordinates as defined above.

**Wall body:**
- WALL_T = 3.0mm (X thickness)
- WALL_Y = 133.0mm (Y depth, front to back)
- WALL_Z = 79.0mm (Z height, bottom to top)

**Rail geometry:**
- LIP_H = 3.0mm (lip protrusion from interior face, in -X direction: from X=0 to X=-3.0mm)
- LIP_W = 2.0mm (lip width in direction perpendicular to slide)
- CHANNEL_W = 3.4mm (gap between lip inner faces: panel 3.0mm + 0.2mm clearance per side)

**Interior face:** X=0.0mm (faces -X into the cartridge)
**Lip tips:** X=-3.0mm

**Interior coordinate span (between panel inner faces, same as left wall):**
- Interior Y: Y=5.0mm to Y=128.0mm (123.0mm span)
- Interior Z: Z=5.0mm to Z=73.6mm (68.6mm span)

---

## Rail Feature Table

All rail lips are rectangular bars attached to the interior face (X=0), protruding in -X to X=-3.0mm.

Y and Z positions of every lip are **identical to the left wall** — only the X direction (protrusion direction) is mirrored.

| # | Rail Name                   | Slide Dir | Sep Axis | Lip A (Y or Z range)  | Lip B (Y or Z range)  | Run Length      | Notes |
|---|-----------------------------|-----------|----------|-----------------------|-----------------------|-----------------|-------|
| 1 | Front panel rail — Lip A    | Z (down)  | Y        | Y=0.0..2.0mm          | —                     | Z=0..79.0mm     | Front edge; channel at Y=2.0..5.4mm |
| 2 | Front panel rail — Lip B    | Z (down)  | Y        | Y=5.4..7.4mm          | —                     | Z=0..79.0mm     | Inner lip |
| 3 | Back panel rail — Lip A     | Z (down)  | Y        | Y=125.6..127.6mm      | —                     | Z=0..79.0mm     | Inner lip |
| 4 | Back panel rail — Lip B     | Z (down)  | Y        | Y=131.0..133.0mm      | —                     | Z=0..79.0mm     | Back edge; channel at Y=127.6..131.0mm |
| 5 | Bottom panel rail — Lip A   | Y (back)  | Z        | Z=0.0..2.0mm          | —                     | Y=0..133.0mm    | Bottom edge; channel at Z=2.0..5.4mm |
| 6 | Bottom panel rail — Lip B   | Y (back)  | Z        | Z=5.4..7.4mm          | —                     | Y=0..133.0mm    | Inner lip |
| 7 | Top / plate-top rail — Lip A| Y (back)  | Z        | Z=71.6..73.6mm        | —                     | Y=0..133.0mm    | Shared by top panel and interior plate top edges |
| 8 | Top / plate-top rail — Lip B| Y (back)  | Z        | Z=77.0..79.0mm        | —                     | Y=0..133.0mm    | Top edge; channel at Z=73.6..77.0mm |
| 9 | Plate bottom rail — Lip A   | Y (back)  | Z        | Z=1.3..3.3mm          | —                     | Y=0..133.0mm    | Plate bottom edge centered at Z=5.0mm |
| 10| Plate bottom rail — Lip B   | Y (back)  | Z        | Z=6.7..8.7mm          | —                     | Y=0..133.0mm    | Channel at Z=3.3..6.7mm |

**Total: 1 wall body + 10 rail lip bars = 11 features**

---

## Rail Channel Summary

| Panel / Plate        | Channel Axis | Channel Range          | Notes |
|----------------------|--------------|------------------------|-------|
| Front panel          | Y            | Y=2.0..5.4mm           | Slides in Z (down from top) |
| Back panel           | Y            | Y=127.6..131.0mm       | Slides in Z (down from top) |
| Bottom panel         | Z            | Z=2.0..5.4mm           | Slides in Y (from front) |
| Top panel            | Z            | Z=73.6..77.0mm         | Slides in Z (down from top); shared with plate top rail |
| Pump tray bottom     | Z            | Z=3.3..6.7mm           | Slides in Y; plate bottom edge at Z=5.0mm |
| Pump tray top        | Z            | Z=73.6..77.0mm         | Shared with top panel rail |
| Coupler tray bottom  | Z            | Z=3.3..6.7mm           | Same rail as pump tray bottom |
| Coupler tray top     | Z            | Z=73.6..77.0mm         | Same rail as pump tray top |

---

## Interface Summary

| Interface    | Mating Part        | Channel Position |
|--------------|--------------------|-----------------|
| Front panel  | Front panel        | Y=2..5mm        |
| Back panel   | Back panel         | Y=127.6..131mm  |
| Bottom panel | Bottom panel       | Z=2..5mm        |
| Top panel    | Top panel          | Z=73.6..77mm    |
| Pump tray    | Pump tray          | Z=3.3..6.7mm (bottom), Z=73.6..77mm (top) |
| Coupler tray | Coupler tray       | Same rails as pump tray |

---

## Print Orientation

Print with exterior face (X=WALL_T=3.0mm in right-wall coordinates) down on build plate. The interior face (X=0) is up, with rail lips protruding upward. No overhangs. Rail lips print as upright bars, FDM-compatible.

Wall body dimensions on build plate: 79.0mm (wall Z) × 133.0mm (wall Y). Well within build area.

---

## Mirror Relationship to Left Wall

The right wall is the left wall reflected across the X axis. In CadQuery:
- Build the left wall geometry with origin at front-bottom-exterior corner, lips protruding in +X.
- Mirror across the YZ plane (negate X for all points) to produce the right wall.
- The result has its interior face at X=0 and lips at X=-3.0mm.

Alternatively: build the same wall body box from X=0 to X=WALL_T, then add lip bars with X offset starting at X=-LIP_H (lip tip) to X=0 (interior face). Either approach is valid.
