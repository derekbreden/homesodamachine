# Spatial Resolution: Sub-G Linkage Rod Guide Slots

## Trivial Case

Sub-G consists of two rectangular through-slots, one in each side wall, for linkage rods connecting the release plate to front pull tabs. The slots are prismatic cuts through 5 mm thick walls along the X axis. No angled mounting, no physics-dependent profiles, no cross-frame transforms. All positions are derived from the release plate's location within the tray frame.

---

## 1. System-Level Placement

```
Mechanism: Linkage Rod Guide Slots
Parent: Tray side walls (Sub-A box shell)
Position: one slot in each side wall, at the Y and Z positions where the release plate's linkage rods exit the interior
Orientation: slots are elongated along Y (depth axis), cut through walls along X (width axis)
```

---

## 2. Part Reference Frame

```
Part: Linkage Rod Guide Slots (Sub-G)
  Frame: tray reference frame (identical to Sub-A)
  Origin: rear-left-bottom corner
  X: width, 0..160 mm
  Y: depth, 0..155 mm (0 = dock/rear, 155 = user/front)
  Z: height, 0..72 mm
  Print orientation: part of the tray; prints open-top-up
  Installed orientation: identical to print orientation
```

No transform. Part frame = tray frame.

---

## 3. Derived Geometry

### Release plate position (source data for slot placement)

The release plate rides on guide posts rising from the rear wall interior face:

- Rear wall interior face: Y = 8.5 mm
- Guide post length: 10 mm, so posts span Y = 8.5 to 18.5 mm
- Release plate: 55 x 55 x 5 mm (X width x Z height x Y thickness)
- Plate Y position at rest (fully retracted, fittings engaged): rear face of plate against rear wall interior at Y = 8.5, front face at Y = 13.5
- Plate Y position when released (pulled toward user by 1.5 mm): rear face at Y = 10.0, front face at Y = 15.0
- Fitting grid: 2x2 at 20 mm center-to-center, centered on the rear wall
- Fitting grid center X: 160 / 2 = 80 mm
- Fitting grid center Z: the plate is centered vertically in the interior. Interior Z range: 3..72 (69 mm). Center Z = 37.5 mm
- Release plate X span: 80 - 27.5 = 52.5 mm to 80 + 27.5 = 107.5 mm
- Release plate Z span: 37.5 - 27.5 = 10.0 mm to 37.5 + 27.5 = 65.0 mm

### Linkage rod attachment points

The linkage rods attach at the left and right edges of the release plate, at the plate's vertical center. The rods are 4 mm diameter and run fore-aft (along Y) from the plate edges through the side wall slots toward the front bezel pull tabs.

- Rod attachment Z: plate vertical center = (10.0 + 65.0) / 2 = 37.5 mm (tray frame)
- Left rod attachment: exits plate left edge at X = 52.5 mm, runs along the inner face of the left wall (X = 5 mm interior face) through the wall to exterior
- Right rod attachment: exits plate right edge at X = 107.5 mm, runs along the inner face of the right wall (X = 155 mm interior face) through the wall to exterior

The rods bend 90 degrees at the plate edges to run parallel to Y along the inner wall faces. The slots are where the rods pass through the side walls.

### Slot positions

The slots must be at a Y position forward of the release plate, where the rods transition from the interior to running along the outer side walls (or remain interior and exit through the front). Given the concept description — rods run along the tray inner side walls from the release plate to the front bezel — the slots allow the rods to pass through the walls so the pull tabs can sit in the bezel's finger channels on the exterior.

However, re-reading the concept: the rods run along the *inner* side walls and attach to pull-tab paddles that sit inside the front bezel's finger channels. The rods stay interior. The slots exist so the rods can slide fore-aft as the release plate moves its 1.5 mm travel. The rods pass through the side walls to mechanically connect the interior release plate to the exterior finger-accessible pull tabs.

**Slot Y position:** The slots should be positioned at the Y location where the rods cross through the wall. The rods connect to the release plate at approximately Y = 8.5..13.5 mm and extend toward the front. The simplest rod geometry has the rods passing through the side walls near the release plate, then running externally (or in channels) to the front bezel. Placing the slots just forward of the release plate zone:

- Slot Y center: 20 mm (just forward of the release plate's front face at Y = 13.5..15.0)
- Slot Y extent: must accommodate 1.5 mm plate travel plus clearance

**Slot Z position:** Aligned with the release plate's linkage attachment height.

- Slot Z center: 37.5 mm (release plate vertical center, matching rod attachment Z)

### Concrete slot dimensions and positions (tray frame)

**Left wall slot (cut through left wall, X = 0 to 5 mm):**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Cut direction | Along X, from X = 0 to X = 5 mm | Through full 5 mm wall thickness |
| Slot center Y | 20.0 mm | Forward of release plate front face |
| Slot center Z | 37.5 mm | Aligned with release plate vertical center |
| Slot length (Y) | 6.0 mm | 1.5 mm travel + 4 mm rod diameter + 0.5 mm clearance (0.25 mm each end) |
| Slot width (Z) | 5.0 mm | 4 mm rod + 1.0 mm clearance (0.5 mm each side) |
| Slot Y range | 17.0 to 23.0 mm | Center 20.0 +/- 3.0 |
| Slot Z range | 35.0 to 40.0 mm | Center 37.5 +/- 2.5 |

**Right wall slot (cut through right wall, X = 155 to 160 mm):**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Cut direction | Along X, from X = 155 to X = 160 mm | Through full 5 mm wall thickness |
| Slot center Y | 20.0 mm | Mirrors left slot |
| Slot center Z | 37.5 mm | Mirrors left slot |
| Slot length (Y) | 6.0 mm | Same as left slot |
| Slot width (Z) | 5.0 mm | Same as left slot |
| Slot Y range | 17.0 to 23.0 mm | Mirrors left slot |
| Slot Z range | 35.0 to 40.0 mm | Mirrors left slot |

Both slots are identical, mirrored about the tray centerline (X = 80 mm).

### Interface specification (both sides)

**Left slot — tray side:**
- Location: left wall, X = 0..5, Y = 17..23, Z = 35..40 (tray frame)
- Mating feature: 4 mm diameter linkage rod sliding fore-aft through the slot

**Left slot — linkage rod side:**
- Rod diameter: 4 mm
- Rod axis: parallel to Y, passing through the slot at Z = 37.5 mm
- Rod travel: 1.5 mm along Y (rod slides within the 6 mm slot length)
- Rod clearance in slot: 0.5 mm radial (Z direction), 0.25 mm axial (Y direction at each end of travel)

**Right slot:** Identical interfaces, mirrored to X = 155..160.

---

## 4. Transform Summary

```
Part frame = Tray frame (identity transform, no rotation, no translation)

Verification:
- Left slot center (2.5, 20.0, 37.5) in part frame = (2.5, 20.0, 37.5) in tray frame ✓
- Right slot center (157.5, 20.0, 37.5) in part frame = (157.5, 20.0, 37.5) in tray frame ✓
- Slot Z center (37.5) matches release plate vertical center (37.5) ✓
```

All correct by identity.
