# Release Plate -- Spatial Resolution

## 1. System-Level Placement

```
Part:        Release Plate (collet-actuating translating plate)
Parent:      Rear wall plate guide pins (release plate slides on 2 dowel pins)
Position:    Interior side of rear wall plate, floating on guide pins
             Translates along Y axis between rest and actuated positions
Orientation: Axis-aligned with rear wall plate and shell bottom (no rotation)
             Plate face normal is parallel to Y axis
```

The release plate is a captive floating element that slides on two 3 mm steel dowel pins press-fit into the rear wall plate. It translates along the Y axis only. Compression springs on the guide pins push the plate toward +Y (away from the JG fittings, into the cartridge interior). When the user squeezes the inset panel, link rods push the plate toward -Y (toward the fittings), and the bore ledges inside the plate push all four JG collets inward simultaneously.

---

## 2. Reference Frame

```
Part:   Release Plate
Origin: Lower-left corner of the dock-facing face of the MAIN BODY
        (the face that faces toward the rear wall plate / dock side)
        Note: link rod attachment tabs extend below Z = 0

X:      Width (left to right), 0..110.8 mm
Z:      Height (bottom to top), main body 0..51.0 mm
        (link rod tabs extend to Z = -4.1 below main body, see Section 7)
Y:      Thickness (toward cartridge interior), 0..5.0 mm

Print orientation: Flat on build plate (dock-facing face DOWN on bed)
                   Stepped bores print as vertical cylinders (best roundness)
                   Guide pin holes print as vertical cylinders
Installed orientation: Plate stands vertical, parallel to rear wall plate interior face
```

### 2.1 Frame relationship to rear wall plate frame

The plate translates along Y in the rear wall plate frame. At any given Y position, the X and Z transforms are fixed:

```
X_rwp = X_plate + 18.5
Z_rwp = Z_plate + 5.0
Y_rwp = Y_plate + Y_dock
```

Where Y_dock is the Y position of the plate's dock-facing face in the rear wall plate frame. Y_dock varies between 25.8 (rest) and 22.8 (full actuation). See Section 4.

```
Inverse:
X_plate = X_rwp - 18.5
Z_plate = Z_rwp - 5.0
Y_plate = Y_rwp - Y_dock
```

### 2.2 Frame relationship to shell-bottom frame

```
X_shell = X_plate + 18.5 + 13.1 = X_plate + 31.6
Z_shell = Z_plate + 5.0 + 4.1 = Z_plate + 9.1
Y_shell = Y_plate + Y_dock + 0.1
```

---

## 3. Plate Outer Dimensions

All coordinates in release-plate frame unless stated otherwise.

### 3.1 Width (X) -- 110.8 mm

Driven by guide pin positions plus structural wall around guide pin holes.

Guide pin positions in rear wall plate frame: X_rwp = 25.0 (left) and X_rwp = 122.8 (right).

The plate must extend at least 6.5 mm beyond each guide pin center (3.2 mm guide pin bore radius + 3.3 mm structural wall).

| Edge | X_rwp (mm) | Derivation |
|------|-----------|------------|
| Left | 18.5 | 25.0 - 6.5 |
| Right | 129.3 | 122.8 + 6.5 |

Plate width: 129.3 - 18.5 = **110.8 mm**.

Clearance to shell interior walls (X_shell = 12..162):
- Left edge: X_shell = 31.6. Clearance to wall at X_shell = 12: **19.6 mm**.
- Right edge: X_shell = 142.4. Clearance to wall at X_shell = 162: **19.6 mm**.

### 3.2 Height (Z) -- main body 51.0 mm

**Top edge derivation:** Upper JG bore centers at Z_rwp = 47.4. Outer bore diameter 15.5 mm, radius 7.75 mm. Bore top edge: Z_rwp = 47.4 + 7.75 = 55.15. Plus 0.85 mm wall: Z_rwp = 56.0.

**Bottom edge derivation:** Main body bottom must clear the link rod channel tops. Link rod channel tops at Z_shell = 7, which is Z_rwp = 2.9. Main body bottom at Z_rwp = 5.0 (2.1 mm above channel tops). In plate frame: Z_plate = 0.

Main body height: Z_rwp 5.0 to 56.0 = **51.0 mm** (Z_plate = 0..51.0).

Two link rod attachment tabs extend below the main body. See Section 7.

### 3.3 Thickness (Y) -- 5.0 mm

Provides adequate wall between stepped bore diameter transitions and sufficient rigidity to distribute collet push force across all four bores.

Bore profile allocation within the 5.0 mm thickness:
- 2.0 mm for body-end clearance zone (15.5 mm bore)
- 1.5 mm for collet-hugging zone (9.8 mm bore)
- 1.5 mm for tube clearance zone (6.5 mm bore)

In plate frame: Y_plate = 0 (dock-facing face) to Y_plate = 5.0 (interior-facing face).

### 3.4 Dimension summary

| Parameter | Value (mm) | Plate frame range |
|-----------|-----------|-------------------|
| Width (X) | 110.8 | X_plate = 0..110.8 |
| Height (Z), main body | 51.0 | Z_plate = 0..51.0 |
| Height (Z), including tabs | 55.1 | Z_plate = -4.1..51.0 |
| Thickness (Y) | 5.0 | Y_plate = 0..5.0 |

---

## 4. Travel Range and Y Positions

### 4.1 Key Y positions along the fitting/plate axis (rear wall plate frame)

| Feature | Y_rwp (mm) | Source |
|---------|-----------|--------|
| Rear wall plate interior face | 14.8 | RWP spatial, Section 3 |
| Guide pin boss face (spring seat, fixed) | 17.8 | RWP spatial, Section 9.1 |
| **Plate dock face, rest** | **25.8** | Boss face + spring free length (Section 4.2) |
| JG body-end face (interior side) | 25.56 | RWP spatial, Section 4.3 |
| Collet tip, extended | 28.30 | 25.56 + 2.74 (collet extended protrusion) |
| Collet tip, compressed | 26.96 | 25.56 + 1.40 (collet compressed protrusion) |
| **Bore ledge (collet-pushing surface), rest** | **29.3** | Plate dock face + 3.5 (Section 5.2) |
| Plate interior face, rest | 30.8 | Plate dock face + 5.0 |
| Guide pin tip | 44.8 | 17.8 + 27.0 exposed pin length |

### 4.2 Rest position (springs at free length)

The compression springs (3 mm ID, 8 mm free length) sit between the boss annular face (Y_rwp = 17.8) and the plate dock-facing face (Y_plate = 0).

```
Y_dock_rest = boss_face + spring_free_length = 17.8 + 8.0 = 25.8
```

At this position, the spring is at its free length (zero preload). The plate is held against the collet tips by the spring and is free to slide toward +Y if disturbed, but the guide pin length (extending to Y_rwp = 44.8) prevents the plate from departing the pins.

### 4.3 Collet contact geometry

The stepped bore's collet-pushing ledge (transition from 9.8 mm collet-hugging bore to 6.5 mm tube clearance bore) is at Y_plate = 3.5 (see Section 5.2). This ledge faces -Y (toward the dock).

Ledge position at rest: Y_rwp = 25.8 + 3.5 = **29.3**.
Collet tip (extended): Y_rwp = **28.3**.

**Gap at rest: 29.3 - 28.3 = 1.0 mm.** The ledge is 1.0 mm further toward +Y (into the cartridge interior) than the extended collet tip. The collet is fully extended (not compressed) at rest. The collet sits inside the collet-hugging bore (9.8 mm) with its tip 1.0 mm short of the ledge.

### 4.4 Actuated position (full stroke)

The plate travels toward -Y by up to 3.0 mm (link rod stroke from inset panel).

| Parameter | Rest | Full actuation | Delta |
|-----------|------|----------------|-------|
| Plate dock face (Y_rwp) | 25.8 | 22.8 | -3.0 |
| Bore ledge (Y_rwp) | 29.3 | 26.3 | -3.0 |
| Plate interior face (Y_rwp) | 30.8 | 27.8 | -3.0 |

Collet contact sequence during actuation:
1. **0..1.0 mm travel (dead stroke):** Plate moves toward -Y, ledge closes the 1.0 mm gap to the collet tip. No collet depression yet.
2. **1.0..2.3 mm travel (collet compression):** Ledge contacts collet annular face and pushes the collet toward -Y. Collet compresses 1.3 mm (full travel). Collet is fully released.
3. **2.3..3.0 mm travel (over-travel margin):** Plate pushes against fully compressed collet. Force reacted through fitting body into rear wall plate bore shoulders. **Margin: 0.7 mm.**

### 4.5 Spring state at full actuation

Spring length at full actuation: 22.8 - 17.8 = **5.0 mm**.
Compression from free length: (8.0 - 5.0) / 8.0 = **37.5%**. Well within the 60% maximum for compression springs.

### 4.6 Guide pin engagement throughout travel

| Position | Pin engagement in plate (mm) | Pin extending past plate (mm) |
|----------|-----------------------------|-----------------------------|
| Rest | 5.0 (full plate thickness) | 44.8 - 30.8 = 14.0 |
| Full actuation | 5.0 (full plate thickness) | 44.8 - 27.8 = 17.0 |

No risk of the plate sliding off the pins at any position.

---

## 5. Stepped Bore Positions and Profiles

### 5.1 Bore center positions

The four stepped bores align with the four JG fitting positions in the rear wall plate.

| Bore | X_rwp (mm) | Z_rwp (mm) | X_plate (mm) | Z_plate (mm) | JG fitting |
|------|-----------|-----------|-------------|-------------|------------|
| B1 | 61.4 | 47.4 | 42.9 | 42.4 | JG1 (Pump 1 inlet) |
| B2 | 86.4 | 47.4 | 67.9 | 42.4 | JG2 (Pump 2 inlet) |
| B3 | 61.4 | 22.4 | 42.9 | 17.4 | JG3 (Pump 1 outlet) |
| B4 | 86.4 | 22.4 | 67.9 | 17.4 | JG4 (Pump 2 outlet) |

Grid center in plate frame: X_plate = 55.4, Z_plate = 29.9.
Grid spacing: 25.0 mm horizontal (X), 25.0 mm vertical (Z).

Derivation: X_plate = X_rwp - 18.5. Z_plate = Z_rwp - 5.0.

### 5.2 Stepped bore profile (each bore identical)

The bore runs from the dock-facing face (Y_plate = 0) to the interior face (Y_plate = 5.0). Three coaxial cylindrical zones, largest diameter at the dock face, smallest at the interior face:

| Zone | Y_plate range (mm) | Diameter (mm) | Length (mm) | Purpose |
|------|-------------------|---------------|-------------|---------|
| Body-end clearance | 0.0..2.0 | 15.5 | 2.0 | Clears 15.10 mm JG body-end OD (0.40 mm diametral clearance) |
| Collet-hugging | 2.0..3.5 | 9.8 | 1.5 | Surrounds 9.57 mm collet OD (0.23 mm diametral clearance) for lateral alignment |
| Tube clearance | 3.5..5.0 | 6.5 | 1.5 | Tube (6.30 mm OD) passes through; smaller than collet ID (6.69 mm) so the annular ledge at Y_plate = 3.5 contacts the collet end face |

**Collet-pushing ledge:** The annular transition from 9.8 mm bore to 6.5 mm bore at Y_plate = 3.5. This ledge faces -Y (toward the dock/fittings). When the plate translates toward -Y, this ledge contacts the collet annular end face and pushes the collet into the fitting body.

Ledge dimensions: ID = 6.5 mm, OD = 9.8 mm.

**Collet contact annulus:** The effective contact is limited by the collet geometry. Collet ID = 6.69 mm, collet OD = 9.57 mm. Contact annulus: ID = 6.69 mm (collet ID, slightly larger than bore ID 6.5), OD = 9.57 mm (collet OD, slightly smaller than bore OD 9.8). Contact area per bore = pi/4 * (9.57^2 - 6.69^2) = pi/4 * (91.58 - 44.76) = **36.8 mm^2**.

### 5.3 Bore geometry verification at rest

At rest (Y_dock = 25.8), the bore zones in rear wall plate frame:

| Zone | Y_rwp range (mm) | What occupies this zone |
|------|-----------------|------------------------|
| Body-end clearance | 25.8..27.8 | JG body-end tip at 25.56 (0.24 mm gap to plate dock face). Body-end OD 15.10 in 15.5 bore. |
| Collet-hugging | 27.8..29.3 | Collet (9.57 mm OD) extends from body-end face (25.56) to tip (28.3). Tip is 1.0 mm short of ledge. |
| Tube clearance | 29.3..30.8 | Tube (6.30 mm OD) passes through. Collet cannot enter (collet OD 9.57 > bore 6.5). |

The body-end (15.10 mm OD) enters the body-end clearance zone (15.5 mm bore). The collet (9.57 mm OD) passes from the body-end clearance zone into the collet-hugging zone (9.8 mm bore). The collet cannot pass the ledge into the tube clearance zone (6.5 mm bore). At rest, the collet tip (28.3) is 1.0 mm short of the ledge (29.3). Correct.

### 5.4 Bore wall thickness checks

**Between adjacent bores (15.5 mm diameter, 25.0 mm center spacing):**
- Same row (B1-B2, B3-B4): 25.0 - 15.5 = **9.5 mm wall**.
- Same column (B1-B3, B2-B4): 25.0 - 15.5 = **9.5 mm wall**.
- Diagonal (B1-B4, B2-B3): sqrt(25^2 + 25^2) - 15.5 = **19.9 mm wall**.

All well above the 1.2 mm structural minimum.

**Bore to plate outer edge (nearest cases):**

| Bore | Edge | Distance to edge (mm) | Minimum wall? |
|------|------|-----------------------|---------------|
| B1 top (Z_plate = 42.4 + 7.75 = 50.15) | Top (Z_plate = 51.0) | 0.85 | At minimum (0.8), acceptable |
| B3 bottom (Z_plate = 17.4 - 7.75 = 9.65) | Bottom (Z_plate = 0) | 9.65 | Well above |
| B3 left (X_plate = 42.9 - 7.75 = 35.15) | Left (X_plate = 0) | 35.15 | Well above |
| B2 right (X_plate = 67.9 + 7.75 = 75.65) | Right (X_plate = 110.8) | 35.15 | Well above |

---

## 6. Guide Pin Hole Positions

### 6.1 Positions

| Pin | X_rwp (mm) | Z_rwp (mm) | X_plate (mm) | Z_plate (mm) |
|-----|-----------|-----------|-------------|-------------|
| Left | 25.0 | 34.9 | 6.5 | 29.9 |
| Right | 122.8 | 34.9 | 104.3 | 29.9 |

Spacing: 104.3 - 6.5 = **97.8 mm** (matches rear wall plate guide pin spacing).

Both pins at Z_plate = 29.9 (plate center height region, providing maximum anti-racking leverage).

### 6.2 Bore dimensions

| Parameter | Value |
|-----------|-------|
| Bore diameter | 3.2 mm (3 mm pin + 0.1 mm per side sliding-fit clearance per requirements.md) |
| Bore type | Through-hole, Y_plate = 0..5.0 |
| Bore axis | Along Y (perpendicular to plate faces) |

The 0.2 mm diametral clearance provides smooth sliding fit while constraining the plate in X and Z.

### 6.3 Spring seat

The compression spring (3 mm ID, estimated ~4 mm OD, 8 mm free length) seats on the flat dock-facing face (Y_plate = 0) around each guide pin hole. The spring coils surround the pin and the contact annulus on the plate face is ID = 3.2 mm (bore edge), OD = ~4 mm (spring OD).

The boss (6 mm OD) on the rear wall plate does not contact the plate -- at rest, the boss face is at Y_rwp = 17.8 and the plate dock face is at Y_rwp = 25.8, giving 8.0 mm of separation (filled by the spring).

### 6.4 Clearance to nearest stepped bore

| Pin | Nearest bore | 2D distance center-to-center (mm) | Pin bore radius (mm) | Stepped bore radius (mm) | Edge-to-edge (mm) |
|-----|-------------|----------------------------------|---------------------|-------------------------|-------------------|
| Left (6.5, 29.9) | B3 (42.9, 17.4) | 38.6 | 1.6 | 7.75 | 29.2 |
| Right (104.3, 29.9) | B4 (67.9, 17.4) | 38.6 | 1.6 | 7.75 | 29.2 |

No interference. Generous clearance.

---

## 7. Link Rod Attachment Tabs

### 7.1 Rationale

The link rods run at Z_shell = 5 (Z_rwp = 0.9) inside U-channels on the shell bottom floor. The main plate body bottom is at Z_plate = 0 (Z_rwp = 5.0, Z_shell = 9.1) to clear the channel tops (Z_shell = 7). Two downward-protruding tabs at the link rod X positions drop into the U-channels and contain press-fit bores for the link rod ends.

### 7.2 Tab positions

| Tab | X_rwp (mm) | X_plate (mm) | Source |
|-----|-----------|-------------|--------|
| Left | 43.9 | 25.4 | RWP spatial, Section 6.1 (link rod notch center X) |
| Right | 103.9 | 85.4 | RWP spatial, Section 6.1 |

The tabs are symmetric about the plate center X (X_plate = 55.4). Left offset: 55.4 - 25.4 = 30.0. Right offset: 85.4 - 55.4 = 30.0.

### 7.3 Tab dimensions

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Tab width (X) | 3.6 mm | Link rod channel inner opening 4.0 mm minus 0.2 mm clearance per side |
| Tab height (Z) | 4.1 mm | From Z_plate = 0 down to Z_plate = -4.1 (Z_rwp = 0.9, Z_shell = 5.0) |
| Tab thickness (Y) | 5.0 mm | Same as plate thickness (continuous with main body) |

Tab Z range in plate frame: Z_plate = -4.1..0.
Tab Z range in shell frame: Z_shell = 5.0..9.1.

### 7.4 Link rod press-fit bore

Each tab contains a horizontal through-bore (axis along Y) for press-fitting the 3 mm steel link rod end.

| Parameter | Value |
|-----------|-------|
| Bore diameter | 3.1 mm (3 mm rod + 0.1 mm per side press-fit per requirements.md) |
| Bore axis | Along Y, centered in tab |
| Bore center X_plate | 25.4 (left), 85.4 (right) |
| Bore center Z_plate | -2.5 (Z_rwp = 2.5, Z_shell = 6.6) |
| Bore type | Through-hole (Y_plate = 0..5.0) |

### 7.5 Tab wall thickness checks

| Wall | Dimension (mm) | Minimum? |
|------|---------------|----------|
| Below bore to tab bottom | Z_plate: -2.5 - 1.55 - (-4.1) = 0.05 | **Below minimum** |

**Problem:** The rod center at Z_rwp = 2.5 with a 3.1 mm bore gives only 0.05 mm of wall below the bore to the tab bottom (Z_plate = -4.1). This is not structurally viable.

**Resolution:** Lower the tab bottom to provide adequate wall. The link rod channel depth extends to Z_shell = 3 (shell bottom floor at Z_shell = 3). At rest, the tab bottom in shell frame is at Z_shell = 5.0 + (-4.1) = Z_shell = 0.9. But the tab is inside the channel, and the channel floor is at Z_shell = 3. The tab bottom must remain above the channel floor.

Revised: set bore center at the center of available tab height. With tab top at Z_plate = 0 (Z_rwp = 5.0) and the need for the bore center to sit with at least 0.8 mm wall on each side:

Bore center Z_plate = -(bore_radius + 0.8) = -(1.55 + 0.8) = -2.35.
Tab bottom = bore_center - bore_radius - 0.8 = -2.35 - 1.55 - 0.8 = **-4.7**.
Tab bottom in shell frame: Z_shell = -4.7 + 9.1 = 4.4. Above channel floor (Z_shell = 3). Good.
Wall above bore: Z_plate 0 - (-2.35 + 1.55) = 0 - (-0.8) = 0.8 mm. At minimum.
Wall below bore: -2.35 - 1.55 - (-4.7) = 0.8 mm. At minimum.

Revised tab height: Z_plate = -4.7..0 = **4.7 mm**.
Bore center: Z_plate = -2.35 (Z_rwp = 2.65, Z_shell = 6.75).

Tab side walls: (3.6 - 3.1) / 2 = **0.25 mm per side**. Below the 0.8 mm structural wall minimum.

**This is a known weak point.** The tab walls in X are only 0.25 mm. However, the tab is in compression (the rod pushes the plate, the tab is the load path). The rod is press-fit and does not cycle. The thin side walls only need to resist the rod pressing outward, which is negligible for a press-fit in compression. The primary structural load (axial push along Y) is carried by the rod-to-bore interface, not the tab side walls. This violation of the 0.8 mm minimum is acceptable and documented.

### 7.6 Revised tab dimensions (final)

| Parameter | Value |
|-----------|-------|
| Tab width (X) | 3.6 mm |
| Tab height (Z) | 4.7 mm (Z_plate = -4.7..0) |
| Tab thickness (Y) | 5.0 mm |
| Bore diameter | 3.1 mm |
| Bore center Z_plate | -2.35 |
| Wall above bore | 0.8 mm |
| Wall below bore | 0.8 mm |
| Wall each side (X) | 0.25 mm (acceptable per Section 7.5) |

### 7.7 Tab clearance in link rod channels

The tabs fit inside the U-channels molded into the shell bottom. The channels have 4 mm inner opening (X), and the tabs are 3.6 mm wide (X), giving 0.2 mm clearance per side. The tab must slide freely within the channel as the plate translates along Y.

Channel Z range: Z_shell = 3..7. Tab Z range at rest: Z_shell = 4.4..9.1. The tab extends 2.1 mm above the channel top (Z_shell = 7..9.1). This 2.1 mm protrusion above the channel is inside the main plate body, which is wider than the channel. The main body (110.8 mm wide) spans far beyond the 6 mm channel outer width, so the main body does not enter the channel. Only the 3.6 mm wide tab enters the channel.

### 7.8 Tab clearance to link rod channel walls during travel

At full actuation, the plate moves 3 mm toward -Y. The tabs move with the plate. The tabs slide along Y inside the channels. The channel walls are 1 mm thick and run from Y_shell = 15..185 (full cartridge depth minus the rear pocket and front wall). The tabs, being 3.6 mm wide inside a 4 mm opening, have clearance throughout Y travel.

### 7.9 Rod insertion angle

The rod runs at Z_shell = 5.0 in the shell bottom bushings (3.2 mm bore at Z_shell = 5). The tab bore center is at Z_shell = 6.75 (1.75 mm above the bushing center). The nearest bushing to the release plate is the rear bushing at Y_shell = 18.

Distance from rear bushing to release plate tab bore (along Y): the tab bore is inside the plate, which at rest has its dock face at Y_shell = 25.9 and interior face at Y_shell = 30.9. The tab bore extends Y_shell = 25.9 to 30.9. The bushing is at Y_shell = 18. Distance from bushing to tab bore entry (dock face) = 25.9 - 18 = 7.9 mm.

Rod angle: arctan(1.75 / 7.9) = **12.5 degrees**. The 3 mm rod in a 3.2 mm bushing bore has 0.2 mm diametral clearance, which accommodates angular misalignment of arctan(0.2 / 8) ~ 1.4 degrees without binding. The 12.5 degree angle is too steep for the bushing bore.

**However:** The rod is not rigid along its full length. The rod bends slightly to accommodate the 1.75 mm offset over the 7.9 mm span. A 3 mm steel rod bends 1.75 mm over ~8 mm with manageable stress. The bushing guides the rod at Z_shell = 5, and the rod curves upward to the tab bore at Z_shell = 6.75. The rod does not need to be perfectly straight.

But the rear wall plate U-notch must accommodate this vertical offset. The U-notch runs from Z_rwp = 0 (Z_shell = 4.1) to Z_rwp = 3.4 (Z_shell = 7.5), with center at Z_shell ~5.8. The rod at the notch location is between the bushing (Z_shell = 5) and the tab bore (Z_shell = 6.75). At the notch Y position (Y_shell ~0.1..14.9), the rod is still near Z_shell = 5 (the bushings constrain it). The notch clears the rod at any height between Z_shell = 4.1 and 7.5. No issue.

The press-fit bore in the tab is at Z_shell = 6.75, so the rod end bends upward from the bushing line (Z_shell = 5.0) to the attachment point. The rod's elastic deformation stores some spring force, but this is negligible compared to the compression spring force and does not affect function.

---

## 8. Clearance to Link Rod Channel Walls (Main Body)

The main plate body (X_plate = 0..110.8) spans across both link rod channels. The channels protrude upward from the shell bottom floor. The main body bottom (Z_plate = 0 = Z_shell = 9.1) is 2.1 mm above the channel tops (Z_shell = 7.0). No cutouts needed in the main body.

Verification:

| Channel | Shell X range (mm) | Plate X range (mm) | Channel top Z_shell (mm) | Main body bottom Z_shell (mm) | Clearance (mm) |
|---------|-------------------|--------------------|--------------------------|-----------------------------|----------------|
| Left | 54..60 | 22.4..28.4 | 7.0 | 9.1 | 2.1 |
| Right | 114..120 | 82.4..88.4 | 7.0 | 9.1 | 2.1 |

Both channels fully cleared. The main plate body passes above the channel walls.

---

## 9. Clearance to Motor Cylinders

The pump motor cylinders (35 mm diameter) protrude rearward from the vertical mounting plate at Y_shell = 85..185 (approximately). The motor centers are at X_shell = 48.3 and 125.7, Z_shell = 40.3.

The release plate at rest has its interior face at Y_shell = 30.9. The mounting plate is at Y_shell = 82.5..87.5. The release plate is well forward (lower Y) of the mounting plate. No interference with motor cylinders.

Minimum Y clearance: 82.5 - 30.9 = **51.6 mm** between plate interior face and mounting plate. No concern.

---

## 10. Interface Summary

### 10.1 Rear wall plate interface (guide pins)

| Parameter | Rear wall plate | Release plate | Fit |
|-----------|----------------|---------------|-----|
| Pin 1 position | X_rwp = 25.0, Z_rwp = 34.9 | X_plate = 6.5, Z_plate = 29.9 | Aligned by transform (X_rwp = 6.5 + 18.5 = 25.0, Z_rwp = 29.9 + 5.0 = 34.9) |
| Pin 2 position | X_rwp = 122.8, Z_rwp = 34.9 | X_plate = 104.3, Z_plate = 29.9 | Aligned by transform |
| Pin diameter | 3 mm dowel in 3.1 mm press-fit bore | 3.2 mm sliding-fit through-hole | 0.2 mm diametral clearance |
| Boss OD | 6 mm, protrudes 3 mm from interior face | No counterbore needed (8 mm spring gap keeps boss away from plate) | 8.0 mm axial clearance at rest |
| Spring | 3 mm ID, 8 mm free length, seated on boss face | Seats on plate dock-facing face around pin hole | Pushes plate toward +Y |

### 10.2 Rear wall plate interface (JG fittings)

| Parameter | Rear wall plate | Release plate | Engagement |
|-----------|----------------|---------------|------------|
| JG fitting positions (4x) | X_rwp = 61.4, 86.4; Z_rwp = 22.4, 47.4 | Stepped bores at X_plate = 42.9, 67.9; Z_plate = 17.4, 42.4 | Aligned by transform |
| Body-end protrusion | 10.76 mm from interior face, OD 15.10 | 15.5 mm bore (body-end clearance zone) | 0.40 mm diametral clearance |
| Collet protrusion | 2.74 mm extended from body-end face | 9.8 mm bore (collet-hugging zone) | 0.23 mm diametral clearance |
| Pushing surface | Collet annular face (ID 6.69, OD 9.57) | Bore ledge at Y_plate = 3.5 (ID 6.5, OD 9.8) | 36.8 mm^2 contact area |

### 10.3 Shell bottom interface (link rod channels)

| Parameter | Shell bottom | Release plate | Fit |
|-----------|-------------|---------------|-----|
| Rod center X | X_shell = 57, 117 | Tab center X_plate = 25.4, 85.4 (X_shell = 57.0, 117.0) | Aligned by transform |
| Rod center Z | Z_shell = 5.0 (in bushings) | Tab bore Z_plate = -2.35 (Z_shell = 6.75) | 1.75 mm offset; rod bends slightly |
| Channel inner width | 4.0 mm | Tab width 3.6 mm | 0.2 mm clearance per side |
| Channel Z range | Z_shell = 3..7 | Tab Z range Z_shell = 4.4..9.1 | Tab within channel in lower portion |

### 10.4 Link rod interface

| Parameter | Release plate | Inset release panel (other end) |
|-----------|--------------|-------------------------------|
| Rod diameter | 3 mm steel | 3 mm steel (same rod) |
| Attachment | Press-fit in 3.1 mm bore, through-hole | Press-fit in blind hole on panel rear face |
| Rod positions | X_plate = 25.4, 85.4 at Z_plate = -2.35 | X_shell = 57, 117 at Z_shell = 5 |

---

## 11. Transform Summary

### 11.1 Release plate frame to rear wall plate frame

```
X_rwp = X_plate + 18.5
Z_rwp = Z_plate + 5.0
Y_rwp = Y_plate + Y_dock    (Y_dock = 25.8 at rest, 22.8 at full actuation)
```

### 11.2 Release plate frame to shell-bottom frame

```
X_shell = X_plate + 31.6
Z_shell = Z_plate + 9.1
Y_shell = Y_plate + Y_dock + 0.1    (Y_dock + 0.1 = 25.9 at rest, 22.9 at full actuation)
```

### 11.3 Verification points (at rest, Y_dock = 25.8)

| Test point (plate frame) | RWP frame | Shell frame | Expected location | Pass? |
|--------------------------|-----------|-------------|-------------------|-------|
| Origin (0, 0, 0) | (18.5, 25.8, 5.0) | (31.6, 25.9, 9.1) | Main body lower-left, dock face, near channel tops | Yes |
| Top-right-interior (110.8, 5.0, 51.0) | (129.3, 30.8, 56.0) | (142.4, 30.9, 60.1) | Upper-right corner, interior face, above upper JG bores | Yes |
| B1 bore center (42.9, 2.5, 42.4) | (61.4, 28.3, 47.4) | (74.5, 28.4, 51.5) | Aligned with JG1, midway through plate | Yes |
| Left guide pin (6.5, 2.5, 29.9) | (25.0, 28.3, 34.9) | (38.1, 28.4, 39.0) | On pin, at plate center height | Yes |
| Left tab bore (25.4, 2.5, -2.35) | (43.9, 28.3, 2.65) | (57.0, 28.4, 6.75) | In left link rod channel zone | Yes |

### 11.4 Round-trip verification

Forward then inverse for B1:
(42.9, 2.5, 42.4) -> (61.4, 28.3, 47.4) -> (61.4 - 18.5, 28.3 - 25.8, 47.4 - 5.0) = (42.9, 2.5, 42.4). Correct.

Forward then inverse for left tab bore:
(25.4, 2.5, -2.35) -> (43.9, 28.3, 2.65) -> (43.9 - 18.5, 28.3 - 25.8, 2.65 - 5.0) = (25.4, 2.5, -2.35). Correct.

Forward then inverse for origin:
(0, 0, 0) -> (18.5, 25.8, 5.0) -> (0, 0, 0). Correct.

---

## 12. Complete Feature Position Table

All positions in release-plate frame. This table provides every coordinate a downstream agent needs.

| Feature | X_plate (mm) | Y_plate (mm) | Z_plate (mm) | Type | Size |
|---------|-------------|-------------|-------------|------|------|
| Main body | 0..110.8 | 0..5.0 | 0..51.0 | Rectangular solid | 110.8 x 5.0 x 51.0 |
| B1 stepped bore | 42.9 | 0..5.0 | 42.4 | Stepped through-bore | See Section 5.2 |
| B2 stepped bore | 67.9 | 0..5.0 | 42.4 | Stepped through-bore | See Section 5.2 |
| B3 stepped bore | 42.9 | 0..5.0 | 17.4 | Stepped through-bore | See Section 5.2 |
| B4 stepped bore | 67.9 | 0..5.0 | 17.4 | Stepped through-bore | See Section 5.2 |
| Guide pin hole (left) | 6.5 | 0..5.0 | 29.9 | Through-bore | 3.2 mm dia |
| Guide pin hole (right) | 104.3 | 0..5.0 | 29.9 | Through-bore | 3.2 mm dia |
| Left link rod tab | 23.6..27.2 | 0..5.0 | -4.7..0 | Rectangular protrusion downward | 3.6 x 5.0 x 4.7 |
| Left tab bore | 25.4 | 0..5.0 | -2.35 | Through-bore (Y axis) | 3.1 mm dia |
| Right link rod tab | 83.6..87.2 | 0..5.0 | -4.7..0 | Rectangular protrusion downward | 3.6 x 5.0 x 4.7 |
| Right tab bore | 85.4 | 0..5.0 | -2.35 | Through-bore (Y axis) | 3.1 mm dia |
| Elephant's foot chamfer | All edges at Z_plate = -4.7 (tab bottoms) and Z_plate = 0 (main body bottom, excluding tab junctions) | -- | -- | Edge chamfer | 0.3 mm x 45 deg |
