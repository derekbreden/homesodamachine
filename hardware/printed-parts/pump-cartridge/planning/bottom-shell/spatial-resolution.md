# Bottom Shell -- Spatial Resolution

This document resolves every multi-frame spatial relationship for the bottom shell into concrete coordinates in the bottom shell's own reference frame. All numbers are final -- no downstream derivation required.

---

## 1. System-Level Placement

The pump cartridge sits at the front-bottom of the enclosure (220 mm wide x 300 mm deep x 400 mm tall per vision.md). The bottom shell is the lower closure of the cartridge, mating with the top shell at a horizontal seam at the cartridge mid-height.

```
Mechanism: Pump Cartridge (Bottom Shell)
Parent: Enclosure interior (via top shell and dock rails)
Position: centered on enclosure width, at the bottom of the enclosure,
  front face flush with enclosure front wall
Orientation: no rotation -- cartridge axes align with enclosure axes
```

When installed, the bottom shell's outer face (the smooth build-plate surface) faces downward toward the enclosure floor. The seam face meets the top shell seam face at installed Z = 25 mm (25 mm above the enclosure floor).

---

## 2. Part Reference Frame

The bottom shell is modeled in its **print orientation** -- the outer bottom face sits on the build plate.

```
Part: Bottom Shell
  Origin: lower-left-front corner of the bounding box as printed
  X: width axis, left-to-right, 0..155 mm
  Y: depth axis, front-to-rear (user side to dock side), 0..170 mm
  Z: height axis, upward from build plate, 0..25 mm

  Z = 0: build plate face = outer bottom of cartridge (cosmetic, smooth)
  Z = 25: top of print = seam mating surface (mates with top shell Z_top = 50)
  Shell interior opens upward (toward Z = 25)
  Interior features (hooks, pins) extrude upward from the floor
```

**Installed orientation:** Flipped 180 degrees about the X axis.
- Z = 0 (build plate, outer bottom) becomes the cartridge underside (installed Z = 0)
- Z = 25 (seam face) becomes the top of the bottom shell (installed Z = 25)
- X and Y remain unchanged

**Envelope:** 155 mm (X) x 170 mm (Y) x 25 mm (Z) for the nominal shell body.

Snap-fit hook arms protrude above Z = 25 (past the seam plane into the top shell interior when assembled). The print bounding box extends to approximately Z = 33, but these are internal assembly features, not part of the external shell envelope.

**Coordinate conventions:**
- All coordinates in this document are in the **bottom shell print frame** unless explicitly labeled otherwise.
- "Forward" / "front" = Y = 0 (user side)
- "Rearward" / "rear" = Y = 170 (dock side)

---

## 3. Frame-to-Frame Mapping

### 3.1 Bottom Shell Print Frame to Installed (System) Frame

The bottom shell print frame maps directly to the installed system frame:

```
X_installed = X_bot
Y_installed = Y_bot
Z_installed = Z_bot
```

No rotation or offset in this direction -- the print frame origin aligns with the installed position (cartridge bottom-left-front corner at the enclosure floor level).

### 3.2 Top Shell Print Frame to Bottom Shell Print Frame

X and Y are identical between frames. Z is inverted with a 75 mm offset (the full cartridge height = 50 mm top shell + 25 mm bottom shell):

```
X_bot = X_top
Y_bot = Y_top
Z_bot = 75.0 - Z_top
```

Key Z mapping verification:

| Feature | Z_top (top shell print frame) | Z_bot (bottom shell print frame) | Meaning |
|---------|-------------------------------|----------------------------------|---------|
| Top shell seam face | 50.0 | 25.0 | Seam alignment -- correct |
| Top shell palm surface | 0.0 | 75.0 | Above bottom shell -- in top shell space |
| Snap-fit ledge top | 44.0 | 31.0 | 6 mm above seam, inside top shell cavity |
| Snap-fit ledge underside | 42.0 | 33.0 | 8 mm above seam, hook engagement surface |
| Alignment pin hole opening | 50.0 | 25.0 | At seam face -- correct |
| Alignment pin hole floor | 44.0 | 31.0 | 6 mm deep into top shell |

---

## 4. Derived Geometry

### 4.1 Outer Walls

| Wall | Position in bottom shell print frame | Thickness | Notes |
|------|-------------------------------------|-----------|-------|
| Outer bottom surface (floor) | Z = 0 to Z = 1.5 | 1.5 mm | Build-plate face at Z = 0. Cosmetic, smooth. |
| Front wall | Y = 0 to Y = 1.5, full X, Z = 0 to 25 | 1.5 mm | Cosmetic. Contains finger bar slot. |
| Rear wall | Y = 168.5 to Y = 170.0, full X, Z = 0 to 25 | 1.5 mm | Cosmetic. |
| Left side wall | X = 0 to X = 1.5, full Y, Z = 0 to 25 | 1.5 mm | Cosmetic. Carries lower T-slot groove cut. |
| Right side wall | X = 153.5 to X = 155.0, full Y, Z = 0 to 25 | 1.5 mm | Mirror of left. |

All walls are 1.5 mm -- cosmetic, non-structural per concept Section 1. The bottom shell has no load-bearing role beyond closing the enclosure and carrying the lower T-slot rail groove halves.

### 4.2 Seam Mating Surface

| Parameter | Value in bottom shell print frame |
|-----------|----------------------------------|
| Seam plane | Z = 25.0, full XY perimeter |
| Mating part feature | Top shell seam at Z_top = 50.0 (top shell print frame) |
| Seam gap target | 0.3 mm maximum (set by alignment pin registration) |
| Seam edge chamfer | 0.15 mm x 45 deg on all external edges at Z = 25.0 |
| Top shell seam chamfer | 0.15 mm x 45 deg on external edges at Z_top = 50.0 |
| Combined treatment | V-groove, 0.3 mm wide, reads as subtle product seam line |

**Elephant's foot chamfer:** 0.3 mm x 45 deg chamfer on the external perimeter edge at Z = 0 (build-plate face). Prevents first-layer flare on the outer cosmetic bottom surface.

### 4.3 Finger Bar Slot

A rectangular opening cut through the front wall, through which the finger bar protrudes.

| Parameter | Value in bottom shell print frame |
|-----------|----------------------------------|
| Slot center X | 77.5 (centered on shell width) |
| Slot X extent | X = 45.0 to X = 110.0 (65.0 mm wide) |
| Slot Z extent | Z = 7.0 to Z = 22.0 (15.0 mm tall) |
| Slot Y depth | Y = 0 to Y = 1.5 (through 1.5 mm front wall) |
| Slot edge radii | 1.0 mm fillet on all four slot edges |

Slot position relative to walls:
- Bottom of slot to floor: Z = 7.0 - 1.5 = 5.5 mm of solid wall below slot
- Top of slot to seam: Z = 25.0 - 22.0 = 3.0 mm of solid wall above slot
- Left of slot to wall: X = 45.0 mm of solid wall
- Right of slot to wall: 155.0 - 110.0 = 45.0 mm of solid wall

**Print note:** The slot ceiling at Z = 22.0 has a short horizontal overhang of 1.5 mm (the front wall thickness). This is well within the 15 mm unsupported bridge limit. No supports needed.

**X alignment with top shell palm inset:** The top shell palm inset spans X_top = 45.0 to 110.0 (65.0 mm wide, centered on X = 77.5). The finger bar slot spans the identical X range. When installed, the slot sits directly below the palm surface inset, separated by the seam and wall material.

### 4.4 Snap-Fit Hooks (x4)

Four snap-fit hooks on the bottom shell interior that engage matching ledges inside the top shell. The hooks are cantilever arms attached to the interior wall faces, extending upward past the seam plane (Z > 25) to reach the top shell ledge engagement surfaces.

**Top shell ledge positions (from top shell parts.md, mapped to bottom shell frame):**

| Ledge | Wall | Ledge X_top | Ledge Y_top | Ledge underside Z_top | Ledge top Z_top | Engagement Z_bot | Y_bot |
|-------|------|-------------|-------------|----------------------|-----------------|-----------------|-------|
| SL1 | Left | 3.0 to 5.0 | 30.0 | 42.0 | 44.0 | 31.0 to 33.0 | 30.0 |
| SL2 | Left | 3.0 to 5.0 | 140.0 | 42.0 | 44.0 | 31.0 to 33.0 | 140.0 |
| SL3 | Right | 150.0 to 152.0 | 30.0 | 42.0 | 44.0 | 31.0 to 33.0 | 30.0 |
| SL4 | Right | 150.0 to 152.0 | 140.0 | 42.0 | 44.0 | 31.0 to 33.0 | 140.0 |

**Hook geometry in bottom shell print frame:**

Each hook is a cantilever arm growing from the interior face of a side wall, extending upward through and past the seam at Z = 25.

| Hook ID | Wall | Arm X range | Arm base Z | Arm tip Z | Hook lip Z range | Center Y | Arm width (Y) |
|---------|------|------------|-----------|----------|-----------------|----------|---------------|
| SH1 | Left interior | 1.5 to 3.5 | 15.0 | 33.0 | 31.0 to 33.0 | 30.0 | 8.0 mm |
| SH2 | Left interior | 1.5 to 3.5 | 15.0 | 33.0 | 31.0 to 33.0 | 140.0 | 8.0 mm |
| SH3 | Right interior | 151.5 to 153.5 | 15.0 | 33.0 | 31.0 to 33.0 | 30.0 | 8.0 mm |
| SH4 | Right interior | 151.5 to 153.5 | 15.0 | 33.0 | 31.0 to 33.0 | 140.0 | 8.0 mm |

Hook arm details:
- **Arm length:** 18.0 mm (from Z = 15 base to Z = 33 tip)
- **Arm cross-section:** 2.0 mm wide (X) x 8.0 mm long (Y)
- **Hook lip overhang:** 2.0 mm in X (toward shell interior), at Z = 31.0 to 33.0
- **Engagement depth:** 2.0 mm in Z (matching the 2.0 mm top shell ledge undercut)
- **Assembly deflection:** arm deflects ~2.0 mm inward (X direction) to pass the ledge edge, then snaps back
- **Flex direction:** X direction (toward/away from wall) -- parallel to build plate (strong layer orientation per requirements.md)

**Hook lip X positions (the catching overhang):**

| Hook ID | Arm inner face X | Lip extends to X | Lip engagement direction |
|---------|-----------------|------------------|------------------------|
| SH1 (left) | 3.5 | 5.5 | +X (toward interior) |
| SH2 (left) | 3.5 | 5.5 | +X |
| SH3 (right) | 151.5 | 149.5 | -X (toward interior) |
| SH4 (right) | 151.5 | 149.5 | -X |

**Interface verification (both sides):**

| Hook lip (bottom shell) | Ledge protrusion (top shell) | X overlap | Engagement |
|------------------------|-----------------------------|-----------|----|
| SH1: X = 3.5 to 5.5 | SL1: X_top = 3.0 to 5.0 | 3.5 to 5.0 (1.5 mm) | Sufficient -- 1.5 mm catch depth |
| SH3: X = 149.5 to 151.5 | SL3: X_top = 150.0 to 152.0 | 150.0 to 151.5 (1.5 mm) | Sufficient |

The 0.5 mm X offset between hook arm face and ledge face is because the bottom shell walls are 1.5 mm thick (arm starts at X = 1.5) while the top shell walls are 3.0 mm thick (ledge starts at X = 3.0). The 1.5 mm effective engagement depth exceeds the 1.5 mm minimum for clear tactile snap per concept Section 2.

**Print note:** The hook arms print as vertical cantilevers growing upward from Z = 15. The portion from Z = 25 to Z = 33 (8 mm) protrudes above the nominal shell envelope -- this is normal for snap-fit geometry and prints without issue. The hook lip at the tip is a 2.0 mm overhang, well within the 15 mm bridge limit.

### 4.5 Alignment Pins (x2)

Two cylindrical bosses on the bottom shell interior that register into matching holes in the top shell, setting the seam position.

**Top shell hole positions (from top shell parts.md):**
- AH1: X_top = 20.0, Y_top = 85.0, Z_top = 44.0 to 50.0 (6.0 mm deep blind hole), diameter 4.2 mm
- AH2: X_top = 135.0, Y_top = 85.0, Z_top = 44.0 to 50.0, diameter 4.2 mm
- Holes open at the seam face (Z_top = 50.0)

**Pin positions in bottom shell print frame:**

| Pin ID | Center X | Center Y | Z base | Z tip | Diameter | Height |
|--------|----------|----------|--------|-------|----------|--------|
| AP1 | 20.0 | 85.0 | 20.0 | 25.0 | 4.0 mm | 5.0 mm |
| AP2 | 135.0 | 85.0 | 20.0 | 25.0 | 4.0 mm | 5.0 mm |

Pin details:
- **Diameter:** 4.0 mm (mates with 4.2 mm holes -- 0.1 mm clearance per side for snug press fit)
- **Height:** 5.0 mm (Z = 20 to Z = 25). Tip is flush with the seam face at Z = 25.
- **Engagement:** Pin tip enters top shell hole at Z_top = 50. Hole is 6.0 mm deep. Pin is 5.0 mm tall. Full pin length engages with 1.0 mm clearance at the hole floor.
- **Support pad:** Each pin sits on a circular reinforcement pad (8.0 mm diameter, 2.0 mm tall, Z = 18.0 to 20.0) providing a solid base

**Clearance verification:** Pin at X = 20.0, Y = 85.0 is well clear of all wall features and the finger bar slot (X = 45-110). Pin at X = 135.0 is also clear. Both are at the mid-depth of the cartridge (Y = 85 of 170 total), centered between the finger bar zone (front) and the pump zone (rear).

### 4.6 T-Slot Rail Grooves (x2, lower half)

The bottom shell carries the lower half of the T-profile groove on each side wall exterior. The groove runs the full depth Y = 0 to Y = 170.

**T-slot position relative to seam:** The top shell spatial resolution states the T-neck midpoint is at Z_top = 39.5 (top shell print frame), with the top shell carrying neck at Z_top = 38 to 41 and upper undercut at Z_top = 41 to 42.5. These features map to installed Z = 32.5 to 37, which is 7.5 mm above the seam at installed Z = 25.

However, the concept (Section 3) and the top shell parts.md (Section 5.1) both state that the seam "crosses" the T-slot groove. For the groove to straddle the seam, it must be centered at or near the seam plane (installed Z = 25 / Z_bot = 25 / Z_top = 50).

**Resolution adopted for the bottom shell:** The bottom shell T-groove is positioned at the seam face (top of the bottom shell walls), forming the lower half of the T-profile. The upper half is at the corresponding position on the top shell walls (near Z_top = 50). This placement satisfies the concept requirement that the seam crosses the groove.

**Note:** The top shell spatial resolution positions its T-groove at Z_top = 38 to 42.5, which is 7.5 to 12 mm from the seam face (Z_top = 50). If the top shell groove stays at that position, it would not mate with the bottom shell groove specified here. The top shell T-groove Z positions may need revision to align with the seam. This discrepancy should be resolved before CadQuery generation. The bottom shell groove positions below are correct for a seam-straddling T-slot.

**Full T-slot profile (assembled, centered on seam at installed Z = 25):**

```
Cross-section at left wall, looking in +Y:

  Installed Z
     28.0 ----+----------+    Upper T-bar undercut ceiling (in top shell)
              |  5.0mm   |    Upper T-bar undercut (1.5 mm tall)
     26.5 ----+----+-----+    Neck top
                   | 2.0 |    Neck upper half (1.5 mm, in top shell wall)
     25.0 ----seam-+------    SEAM LINE
                   | 2.0 |    Neck lower half (1.5 mm, in bottom shell wall)
     23.5 ----+----+-----+    Neck bottom
              |  5.0mm   |    Lower T-bar undercut (1.5 mm tall)
     22.0 ----+----------+    Lower T-bar undercut floor (in bottom shell)

  Neck width (X): 2.0 mm from exterior surface
  T-bar slot width (X): 5.0 mm from exterior surface
  Total groove depth (X): 5.0 mm into wall
```

**Left wall lower T-groove in bottom shell print frame:**

| Feature | X range | Z range | Y range |
|---------|---------|---------|---------|
| Neck opening (lower half) | X = 0 to X = 2.0 | Z = 23.5 to Z = 25.0 | Y = 0 to 170 |
| T-bar undercut (lower lobe) | X = 0 to X = 5.0 | Z = 22.0 to Z = 23.5 | Y = 0 to 170 |

**Right wall lower T-groove (mirror about X = 77.5):**

| Feature | X range | Z range | Y range |
|---------|---------|---------|---------|
| Neck opening (lower half) | X = 153.0 to X = 155.0 | Z = 23.5 to Z = 25.0 | Y = 0 to 170 |
| T-bar undercut (lower lobe) | X = 150.0 to X = 155.0 | Z = 22.0 to Z = 23.5 | Y = 0 to 170 |

**45-degree chamfer:** 1.0 mm x 45 deg on the inward-facing floor edge of the T-bar undercut (at Z = 22.0) to eliminate the overhang for printing. This mirrors the top shell's chamfer on its T-bar undercut ceiling.

**Profile dimensions (matching top shell):**
- Neck width: 2.0 mm (X)
- Neck height (lower half only): 1.5 mm (Z = 23.5 to 25.0)
- T-bar slot width: 5.0 mm (X)
- T-bar undercut depth below neck: 1.5 mm (Z = 22.0 to 23.5)
- Total groove depth from exterior: 5.0 mm (X)

**Print note:** The T-bar undercut has a horizontal floor at Z = 22.0. The overhang depth is 3.0 mm (the T-bar extends 3.0 mm beyond the neck in X). This is within the 15 mm bridge limit. The 45-degree chamfer further reduces the unsupported span. No designed supports needed.

**Interface with top shell T-groove (both sides specified):**

| Feature | Bottom shell | Top shell (revised to seam position) |
|---------|-------------|-------------------------------------|
| Neck lower half | Z_bot = 23.5 to 25.0, X = 0 to 2.0 | Neck upper half: Z_top = 48.5 to 50.0, X = 0 to 2.0 |
| Lower T-bar undercut | Z_bot = 22.0 to 23.5, X = 0 to 5.0 | Upper T-bar undercut: Z_top = 47.0 to 48.5, X = 0 to 5.0 |
| Combined neck | 3.0 mm total (1.5 mm per shell) | Continuous across seam |
| Combined T-bar | 5.0 mm wide, 3.0 mm total height (1.5 mm per side of neck) | Symmetric about neck center |

### 4.7 Electrical Connector Recess

A rectangular pocket on the outer bottom face for the blind-mate electrical connector.

| Parameter | Value in bottom shell print frame |
|-----------|----------------------------------|
| Pocket center X | 77.5 (centered on width) |
| Pocket center Y | 155.0 (near rear, aligned with bulkhead zone) |
| Pocket X extent | X = 70.0 to X = 85.0 (15.0 mm wide) |
| Pocket Y extent | Y = 150.0 to Y = 160.0 (10.0 mm deep) |
| Pocket Z extent | Z = 0 to Z = 5.0 (5.0 mm deep, cut into the floor from the build-plate face) |

This pocket is on the exterior bottom face (Z = 0 side). It contains the cartridge-side electrical contact pads. When inserted in the dock, a spring-loaded pogo-pin connector on the dock floor mates into this recess.

**Print note:** The pocket is a rectangular recess in the build-plate face. It prints as a simple pocket (open at Z = 0 on the build plate). The pocket floor at Z = 5.0 is a bridge of 15 mm (X direction) -- exactly at the 15 mm bridge limit. If this sags, reduce to 14 mm width or add a 0.5 mm support rib across the center.

### 4.8 External Corner Treatment

| Feature | Treatment |
|---------|-----------|
| All external edges | 1.0 mm fillet (C1 radius) |
| Internal edges (not user-facing) | 0.5 mm chamfer |
| Seam edges at Z = 25.0 | 0.15 mm x 45 deg chamfer (seam treatment, overrides general fillet) |
| Build plate edges at Z = 0 | 0.3 mm x 45 deg elephant's foot chamfer (overrides general fillet) |

---

## 5. Interface Positions Summary

### 5.1 Bottom Shell to Top Shell

| Interface | Bottom shell feature | Top shell feature | Clearance / fit |
|-----------|---------------------|-------------------|----------------|
| Seam plane | Z = 25.0, full XY perimeter | Z_top = 50.0, full XY perimeter | 0.3 mm max gap |
| Seam chamfer | 0.15 mm x 45 deg at Z = 25.0 | 0.15 mm x 45 deg at Z_top = 50.0 | Combined V-groove |
| Snap-fit hooks x4 | SH1-SH4: arms from Z=15 to Z=33, lips at Z=31-33 | SL1-SL4: ledges at Z_top=42-44, Y=30/140 | 1.5 mm catch depth (X) |
| Alignment pins x2 | AP1/AP2: 4.0 mm dia, 5 mm tall, tips at Z=25 | AH1/AH2: 4.2 mm dia, 6 mm deep, opening at Z_top=50 | 0.1 mm/side press fit |
| T-slot lower half | Neck Z=23.5-25, undercut Z=22-23.5 | Neck Z_top=48.5-50, undercut Z_top=47-48.5 | Continuous profile at seam |

### 5.2 Bottom Shell to Finger Bar

| Interface | Bottom shell feature | Finger bar feature |
|-----------|---------------------|-------------------|
| Slot opening | 65 mm x 15 mm opening at Y=0, X=45-110, Z=7-22 | Bar ~65 mm wide x 13 mm deep x 4 mm thick protrudes through slot |
| Slot constrains bar | Slot edges prevent finger bar from escaping radially | Bar is retained axially by lever arm connection (inside top shell) |
| Gap around bar | ~1 mm clearance on each side of finger bar within slot | Bar moves 12-15 mm in the squeeze direction (toward palm / +Z installed) |

### 5.3 Bottom Shell to Dock Cradle

| Interface | Bottom shell feature | Dock cradle feature |
|-----------|---------------------|-------------------|
| T-slot lower groove (x2) | Lower T-profile on each side wall exterior, Y=0 to 170 | T-profile dock rails engage combined T-slot (upper from top shell + lower from bottom shell) |
| Electrical connector recess | Pocket on bottom face: X=70-85, Y=150-160, Z=0-5 | Pogo-pin connector on dock floor mates into pocket |

### 5.4 Bottom Shell to Lever Arms

The bottom shell has no direct interface with the lever arms. The lever pivot bosses are at Z_top = 15.0 in the top shell print frame, which maps to installed Z = 60 -- deep inside the top shell cavity, well above the bottom shell's range (installed Z = 0 to 25). The pivot pins are fully captured within the top shell bosses (blind bore pockets on both ends). The bottom shell does not provide pin capture or any other lever constraint.

---

## 6. Transform Summary

### Bottom Shell Print Frame to Installed (System) Frame

```
X_sys = X_bot + 32.5    (center 155 mm cartridge in 220 mm enclosure)
Y_sys = Y_bot            (front face flush with enclosure front)
Z_sys = Z_bot            (outer bottom at enclosure floor)
```

### Bottom Shell Print Frame to Top Shell Print Frame

```
X_top = X_bot
Y_top = Y_bot
Z_top = 75.0 - Z_bot
```

### Verification Points

**Point 1: Origin (bottom-left-front corner, outer bottom face)**
- Bottom shell print frame: (0, 0, 0)
- System frame: (0 + 32.5, 0, 0) = (32.5, 0, 0)
- Check: front-left corner of cartridge bottom face, on the enclosure floor. Correct.
- Top shell frame equivalent: (0, 0, 75) -- above the top shell (in the top shell frame, Z_top = 75 is outside the 0-50 range). Expected -- this point is on the bottom shell exterior, not within the top shell.

**Point 2: Alignment pin AP1 tip**
- Bottom shell print frame: (20.0, 85.0, 25.0)
- System frame: (52.5, 85.0, 25.0)
- Top shell frame: (20.0, 85.0, 75 - 25) = (20.0, 85.0, 50.0)
- Check: Pin tip at the seam face. In top shell frame, Z_top = 50.0 is the seam face where hole AH1 opens. X_top = 20.0 and Y_top = 85.0 match the hole center. Correct.

**Point 3: Snap-fit hook SH1 engagement surface**
- Bottom shell print frame: (5.0, 30.0, 31.0)
- System frame: (37.5, 30.0, 31.0)
- Top shell frame: (5.0, 30.0, 75 - 31) = (5.0, 30.0, 44.0)
- Check: In top shell frame, ledge SL1 top is at Z_top = 44.0, X_top = 3.0 to 5.0, Y_top = 30.0. The hook engagement at X = 5.0, Y = 30, Z_top = 44 falls on the ledge top face. Correct.

**Inverse verification (System to Bottom Shell Print):**
```
X_bot = X_sys - 32.5
Y_bot = Y_sys
Z_bot = Z_sys
```

Point 2 inverse: (52.5 - 32.5, 85.0, 25.0) = (20.0, 85.0, 25.0). Matches. Round-trip verified.

---

## Appendix: Coordinate Summary Table

All positions in the bottom shell print frame.

| Feature | X (mm) | Y (mm) | Z (mm) | Size / Notes |
|---------|--------|--------|--------|-------------|
| **Outer envelope** | 0-155 | 0-170 | 0-25 | Nominal bounding box |
| **Outer bottom surface** | 0-155 | 0-170 | 0-1.5 | Build-plate face, smooth |
| **Front wall** | 0-155 | 0-1.5 | 0-25 | 1.5 mm thick |
| **Rear wall** | 0-155 | 168.5-170 | 0-25 | 1.5 mm thick |
| **Left wall** | 0-1.5 | 0-170 | 0-25 | 1.5 mm thick |
| **Right wall** | 153.5-155 | 0-170 | 0-25 | 1.5 mm thick |
| **Seam face** | 0-155 | 0-170 | 25.0 | Mating surface |
| **Finger bar slot** | 45-110 | 0-1.5 | 7-22 | 65 x 15 mm opening |
| **Alignment pin AP1** | 20.0 ctr | 85.0 ctr | 20-25 | 4.0 mm dia, 5 mm tall |
| **Alignment pin AP2** | 135.0 ctr | 85.0 ctr | 20-25 | 4.0 mm dia, 5 mm tall |
| **Snap-fit hook SH1** | 1.5-5.5 | 26-34 (Y ctr 30) | 15-33 | Left front, lip at Z=31-33 |
| **Snap-fit hook SH2** | 1.5-5.5 | 136-144 (Y ctr 140) | 15-33 | Left rear, lip at Z=31-33 |
| **Snap-fit hook SH3** | 149.5-153.5 | 26-34 (Y ctr 30) | 15-33 | Right front, lip at Z=31-33 |
| **Snap-fit hook SH4** | 149.5-153.5 | 136-144 (Y ctr 140) | 15-33 | Right rear, lip at Z=31-33 |
| **Left T-groove neck** | 0-2.0 | 0-170 | 23.5-25.0 | Lower half of neck |
| **Left T-groove undercut** | 0-5.0 | 0-170 | 22.0-23.5 | Lower T-bar lobe |
| **Right T-groove neck** | 153.0-155.0 | 0-170 | 23.5-25.0 | Lower half of neck |
| **Right T-groove undercut** | 150.0-155.0 | 0-170 | 22.0-23.5 | Lower T-bar lobe |
| **Electrical recess** | 70-85 | 150-160 | 0-5 | Pogo-pin connector pocket |

---

## Appendix: Discrepancy Note -- T-Slot Groove Z Position

The top shell spatial resolution (Section 3.9) positions its T-groove at Z_top = 38.0 to 42.5, which maps to installed Z = 32.5 to 37.0 -- entirely above the seam at installed Z = 25. The concept architecture (Section 3) states the seam "crosses the T-slot rail groove" and the groove is "split: the upper half of the T-profile is in the top shell, the lower half in the bottom shell."

For the seam to cross the groove, the groove must straddle the seam plane. This document positions the bottom shell T-groove at Z_bot = 22.0 to 25.0, corresponding to installed Z = 22.0 to 25.0 (at and just below the seam). The matching top shell groove should be at Z_top = 47.0 to 50.0 (at and just above the seam from the top shell side).

The top shell T-groove Z values (38.0 to 42.5) need to be revised to 47.0 to 50.0 for the two halves to form a continuous profile at the seam. This revision should be made in the top shell spatial resolution and parts specification before CadQuery generation proceeds.
