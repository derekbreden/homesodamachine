# Spatial Resolution: Sub-J Electrical Contact Pad Areas

## 1. System-Level Placement

```
Mechanism: Electrical Contact Pad Areas (blade terminal mounts + wire routing)
Parent: Tray (Sub-A box shell), rear wall and interior
Position: Rear wall exterior face (Y=0 plane) for blade terminal slots;
          interior wall and floor surfaces for wire routing channels
Orientation: Blade terminal slots oriented with blade engagement axis along Y
             (parallel to cartridge insertion direction)
Purpose: Provide mounting positions for female spade terminals on pump motor wires
         and cartridge-present jumper wire; route wires from pump motor terminals
         to rear wall blade positions
```

The cartridge slides along Y (0=dock, 155=user). Male blade tabs on the dock protrude in the +Y direction. As the cartridge inserts (moving in -Y toward the dock), the female spade terminals on the cartridge rear wall engage the dock's male blades during the last ~5 mm of travel. This is a blind-mate connection, aligned by the T-rails.

---

## 2. Part Reference Frame

```
Part: Electrical Contact Pad Areas (Sub-J)
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

### 3.1 Fitting bore exclusion zone (from Sub-D, for clearance reference)

The fitting bore array occupies the center of the rear wall exterior. Terminal positions must avoid this zone.

Fitting grid: 2x2 at 20 mm center-to-center, centered on the rear wall.
- Grid center X: 80.0 mm
- Grid center Z: 37.5 mm (centered in interior height: (3 + 72) / 2 = 37.5)
- Fitting positions (X, Z): (70.0, 27.5), (90.0, 27.5), (70.0, 47.5), (90.0, 47.5)
- Entry funnels on rear wall exterior: 15.5 mm diameter countersinks at each bore
- **Exclusion envelope** (funnels plus 3 mm clearance): X = 54.3 .. 105.8, Z = 11.8 .. 63.3

### 3.2 Blade terminal hosting surface

**Surface: rear wall exterior, Y = 0 plane.**

This is the correct surface because:
- Blade engagement direction must be parallel to the insertion axis (Y) for blind-mate
- Male blades on the dock protrude in +Y; female spades on the tray face -Y
- The rear wall is 8.5 mm thick (Y = 0 to 8.5), providing ample material for retention slots
- The T-rails provide lateral (X) and vertical (Z) alignment to within 0.3 mm, sufficient for 6.3 mm blade self-centering

### 3.3 Terminal position layout

Five terminal positions on the rear wall exterior (Y = 0 plane). Positions are given as (X, Z) in the tray frame.

**Keying strategy:** Pump 1 and Pump 2 blade pairs use different vertical (Z) spacing so connectors cannot be cross-mated. The cartridge-present pair uses a different blade width (4.8 mm vs 6.3 mm) for additional differentiation.

#### Pump 1 blades (left side of rear wall, below fitting exclusion zone)

Pump 1 is the left pump, centered at approximately X = 43.2 mm.

| Terminal | Function | X (mm) | Z (mm) | Blade width |
|----------|----------|--------|--------|-------------|
| T1 | Pump 1 (+) | 25.0 | 18.0 | 6.3 mm |
| T2 | Pump 1 (-) | 25.0 | 30.0 | 6.3 mm |

- Pair spacing (Z): 12.0 mm center-to-center
- X position: centered on the left wall zone (X = 25), clear of fitting exclusion (starts at X = 54.3)
- Z positions: 18.0 and 30.0 mm, within the lower half of the wall

#### Pump 2 blades (right side of rear wall, below fitting exclusion zone)

Pump 2 is the right pump, centered at approximately X = 116.8 mm.

| Terminal | Function | X (mm) | Z (mm) | Blade width |
|----------|----------|--------|--------|-------------|
| T3 | Pump 2 (+) | 135.0 | 18.0 | 6.3 mm |
| T4 | Pump 2 (-) | 135.0 | 34.0 | 6.3 mm |

- Pair spacing (Z): 16.0 mm center-to-center (different from Pump 1's 12.0 mm for polarity keying)
- X position: centered on the right wall zone (X = 135), clear of fitting exclusion (ends at X = 105.8)

#### Cartridge-present detection pair (bottom center, below fittings)

| Terminal | Function | X (mm) | Z (mm) | Blade width |
|----------|----------|--------|--------|-------------|
| T5 | Cartridge present (pair) | 80.0 | 8.0 | 4.8 mm |

- Single housing position containing 2 pins at 4.8 mm width, spaced 7.0 mm center-to-center within the housing
- Z = 8.0 mm places it below the fitting exclusion zone (starts at Z = 11.8)
- X = 80.0 mm centers it on the tray, directly below the fitting grid
- The 4.8 mm blade width (vs 6.3 mm for motor blades) provides additional mechanical differentiation

#### Keying verification

| Test | Pump 1 spacing | Pump 2 spacing | Match? |
|------|----------------|----------------|--------|
| Correct insertion | 12.0 mm | 16.0 mm | Yes — each pair matches its dock counterpart |
| Pump 1 spades on Pump 2 dock blades | 12.0 mm spade pair vs 16.0 mm blade pair | No match — T1 would hit T3 but T2 misses T4 by 4.0 mm |
| Pump 2 spades on Pump 1 dock blades | 16.0 mm spade pair vs 12.0 mm blade pair | No match — T3 would hit T1 but T4 misses T2 by 4.0 mm |

The 4.0 mm difference in pair spacing prevents any cross-connection. Combined with the left/right X separation (25 vs 135 mm = 110 mm apart), accidental cross-mating is physically impossible.

### 3.4 Terminal retention slot geometry

Each terminal position requires a rectangular slot cut into the rear wall exterior face to retain the female spade terminal housing. The slot captures the terminal so it cannot be pushed inward when the dock's male blade engages during insertion.

**6.3 mm terminal slot (T1, T2, T3, T4):**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Slot width (X) | 8.0 mm | 6.3 mm blade housing + 1.7 mm clearance for alignment |
| Slot height (Z) | 8.5 mm | Standard 6.3 mm flag terminal housing height + clearance |
| Slot depth into wall (Y) | 3.0 mm | Into rear wall from Y=0 toward Y=3.0. Leaves 5.5 mm wall behind slot. |
| Blade opening width (X) | 7.0 mm | Centered in slot, for male blade entry |
| Blade opening height (Z) | 2.0 mm | Centered vertically in slot, for 0.8 mm thick blade + clearance |

The slot captures the terminal housing on all 4 sides. The blade opening in the bottom of the slot allows the dock's male blade to enter and mate with the female spade.

**4.8 mm terminal slot (T5, cartridge-present):**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Slot width (X) | 18.0 mm | 2-pin housing: 2 x 4.8 mm blades at 7.0 mm c-c + housing walls |
| Slot height (Z) | 7.0 mm | Smaller housing for 4.8 mm terminals |
| Slot depth into wall (Y) | 3.0 mm | Same as motor terminals |
| Blade openings (X) | 5.5 mm each, at 7.0 mm c-c within the slot | Two openings for the 2-pin pair |
| Blade opening height (Z) | 1.5 mm | For 0.5 mm thick blade + clearance |

### 3.5 Terminal slot positions — rear wall exterior face coordinate table

All positions are slot centers on the Y = 0 plane, in tray frame coordinates.

| Slot | Center X (mm) | Center Z (mm) | Width (X, mm) | Height (Z, mm) | Depth (Y, mm) |
|------|---------------|---------------|---------------|-----------------|----------------|
| T1 | 25.0 | 18.0 | 8.0 | 8.5 | 3.0 |
| T2 | 25.0 | 30.0 | 8.0 | 8.5 | 3.0 |
| T3 | 135.0 | 18.0 | 8.0 | 8.5 | 3.0 |
| T4 | 135.0 | 34.0 | 8.0 | 8.5 | 3.0 |
| T5 | 80.0 | 8.0 | 18.0 | 7.0 | 3.0 |

### 3.6 Wire routing channels

Motor wires must route from the pump motor terminals (at the user-facing end of each pump, high Y) back to the rear wall terminal slots (Y = 0). The wires are 18-22 AWG stranded copper with female spade terminals crimped on the ends.

**Motor terminal exit positions (approximate, in tray frame):**

Pumps are oriented with motors facing forward (high Y), pump heads toward the rear (low Y). Motor terminals are solder tabs at the rear of the motor (which is the user-facing end in installed orientation). Given pump head front face starts around Y = 8.5 + small gap, and total pump length is ~116 mm, motor terminals are at approximately Y = 8.5 + 116 = 124.5 mm.

| Wire source | X (mm) | Y (mm) | Z (mm) | Notes |
|-------------|--------|--------|--------|-------|
| Pump 1 motor (+) | 40.0 | 124.5 | 37.5 | Approximate, at motor terminal tabs, mid-height |
| Pump 1 motor (-) | 46.0 | 124.5 | 37.5 | ~6 mm lateral offset between solder tabs |
| Pump 2 motor (+) | 114.0 | 124.5 | 37.5 | Mirror of Pump 1 |
| Pump 2 motor (-) | 120.0 | 124.5 | 37.5 | Mirror of Pump 1 |

**Wire routing paths (tray frame):**

Each pair of motor wires follows the same general path: down from the motor terminal zone to the tray floor, along the floor toward the rear wall, then up the interior face of the rear wall to exit through the wall at the terminal slot position.

**Pump 1 wire channel (2 wires):**

| Segment | Start (X, Y, Z) | End (X, Y, Z) | Surface | Notes |
|---------|-----------------|---------------|---------|-------|
| Drop to floor | (43, 124, 37) | (25, 124, 3) | Left interior wall face (X=5) or open air along pump body | Wires drop alongside pump body |
| Floor run rearward | (25, 124, 3) | (25, 9, 3) | Interior floor surface (Z=3 plane) | U-channel in floor, runs along left side |
| Rise to T1/T2 | (25, 9, 3) | (25, 3, 18..30) | Rear wall interior face (Y=8.5 plane) | Wires rise up rear wall interior to pass through wall |
| Through wall T1 | (25, 8.5, 18) | (25, 0, 18) | Through rear wall | Wire exits to terminal slot T1 |
| Through wall T2 | (25, 8.5, 30) | (25, 0, 30) | Through rear wall | Wire exits to terminal slot T2 |

**Pump 2 wire channel (2 wires):**

| Segment | Start (X, Y, Z) | End (X, Y, Z) | Surface | Notes |
|---------|-----------------|---------------|---------|-------|
| Drop to floor | (117, 124, 37) | (135, 124, 3) | Right interior wall face (X=155) or open air along pump body | Wires drop alongside pump body |
| Floor run rearward | (135, 124, 3) | (135, 9, 3) | Interior floor surface (Z=3 plane) | U-channel in floor, runs along right side |
| Rise to T3/T4 | (135, 9, 3) | (135, 3, 18..34) | Rear wall interior face (Y=8.5 plane) | Wires rise up rear wall interior to pass through wall |
| Through wall T3 | (135, 8.5, 18) | (135, 0, 18) | Through rear wall | Wire exits to terminal slot T3 |
| Through wall T4 | (135, 8.5, 34) | (135, 0, 34) | Through rear wall | Wire exits to terminal slot T4 |

**Cartridge-present jumper wire (short loop):**

The cartridge-present wire is a simple jumper connecting two pins within the T5 housing. It does not route from a pump — it is a short wire loop (~30 mm) contained entirely within the T5 terminal slot area on the rear wall. No channel routing needed. The jumper is crimped to two female spade terminals and inserted into the T5 housing during assembly.

### 3.7 Wire channel cross-section

Floor-level channels carry 2 wires each (18-22 AWG, ~1.5 mm OD with insulation).

| Parameter | Value | Notes |
|-----------|-------|-------|
| Channel width (X) | 6.0 mm | 2 wires side by side (2 x 1.5 mm) + 3.0 mm clearance |
| Channel depth (into floor, Z) | 2.0 mm | Cut into floor from Z=3 surface downward to Z=1 |
| Channel length (Y) | ~115 mm | From Y=124 to Y=9 along the floor |

The channels leave 1.0 mm of floor material below them (floor is 3 mm thick, channel cuts 2 mm). Wires sit below the floor surface plane, protected from interference with tube routing channels (Sub-F) which run at the Z=3 surface level.

### 3.8 Wire pass-through holes in rear wall

Each motor wire passes through a small hole from the rear wall interior to the terminal slot on the exterior. Four holes total (2 per pump).

| Hole | Center X (mm) | Center Z (mm) | Diameter (mm) | Y span |
|------|---------------|---------------|---------------|--------|
| W1 (to T1) | 25.0 | 18.0 | 3.0 mm | Y = 0 to 8.5 (through full rear wall) |
| W2 (to T2) | 25.0 | 30.0 | 3.0 mm | Y = 0 to 8.5 |
| W3 (to T3) | 135.0 | 18.0 | 3.0 mm | Y = 0 to 8.5 |
| W4 (to T4) | 135.0 | 34.0 | 3.0 mm | Y = 0 to 8.5 |

The holes are concentric with the terminal slot centers. Wire enters from the interior face (Y = 8.5), passes through the wall, and the crimped spade terminal seats in the retention slot on the exterior face (Y = 0).

### 3.9 Interface specification

**Sub-J to Sub-A (rear wall exterior):**
- 5 terminal retention slots cut into the Y = 0 plane at positions per section 3.5
- 4 wire pass-through holes per section 3.8
- All cuts are within the rear wall body (Y = 0 to 8.5, X = 0..160, Z = 0..72)
- Mating feature: dock male blade tabs at corresponding (X, Z) positions, protruding in +Y

**Sub-J to Sub-A (interior floor):**
- 2 wire routing channels cut into the Z = 3 floor surface
- Left channel: X = 22..28, Y = 9..124, Z = 1..3 (2 mm deep cut in 3 mm floor)
- Right channel: X = 132..138, Y = 9..124, Z = 1..3
- These channels run parallel to and inboard of the tube routing channels (Sub-F)

**Sub-J to Sub-D (fitting bores, clearance):**
- All terminal slots and wire holes are outside the fitting exclusion envelope (X = 54.3..105.8, Z = 11.8..63.3)
- Minimum clearance between nearest terminal slot (T2 at X=25, Z=30) and nearest fitting funnel edge (X=54.3): 25.3 mm in X
- Minimum clearance between T5 (Z=8.0) and nearest funnel edge (Z=11.8): 0.3 mm. This is tight but acceptable since T5 is a shallow slot (3 mm deep) and the fitting funnel is a countersink from the same face — they do not interfere volumetrically because T5 is at X=80 (directly below the fitting grid center) and the nearest funnel center is at (70, 27.5), with the funnel edge at Z = 27.5 - 15.5/2 = 19.75. The funnel at Z=19.75 is 11.75 mm above T5 at Z=8.0. Clearance is adequate.

**Sub-J to dock (mating interface):**
- Dock provides 5 male blade positions matching (X, Z) coordinates of T1-T5
- Dock blades protrude in +Y, length ~8-10 mm
- Engagement begins at ~5 mm before end-of-travel (blade tip enters spade)
- Full seating at end-of-travel (spring detent click)

---

## 4. Transform Summary

```
Part frame = Tray frame (identity transform, no rotation, no translation)

Verification:
- T1 center (25.0, 0.0, 18.0) in part frame = (25.0, 0.0, 18.0) in tray frame ✓
- T3 center (135.0, 0.0, 18.0) in part frame = (135.0, 0.0, 18.0) in tray frame ✓
- T5 center (80.0, 0.0, 8.0) in part frame = (80.0, 0.0, 8.0) in tray frame ✓
- T1 and T3 are symmetric about X=80: |80-25| = |135-80| = 55 ✓
- T2 Z (30.0) - T1 Z (18.0) = 12.0 mm (Pump 1 spacing) ✓
- T4 Z (34.0) - T3 Z (18.0) = 16.0 mm (Pump 2 spacing, different from Pump 1) ✓
```

All correct by identity.

---

## 5. Dimension Summary Table

All values in tray frame.

| Dimension | Value | Axis | Notes |
|-----------|-------|------|-------|
| Hosting surface | Y = 0 plane (rear wall exterior) | Y | Blade engagement along Y |
| T1 position (P1+) | X=25.0, Z=18.0 | XZ | 6.3 mm blade |
| T2 position (P1-) | X=25.0, Z=30.0 | XZ | 6.3 mm blade |
| T3 position (P2+) | X=135.0, Z=18.0 | XZ | 6.3 mm blade |
| T4 position (P2-) | X=135.0, Z=34.0 | XZ | 6.3 mm blade |
| T5 position (cart present) | X=80.0, Z=8.0 | XZ | 4.8 mm blade, 2-pin |
| Pump 1 pair Z spacing | 12.0 mm | Z | T1-to-T2 center-to-center |
| Pump 2 pair Z spacing | 16.0 mm | Z | T3-to-T4 center-to-center |
| Keying delta | 4.0 mm | Z | Difference in pair spacing |
| Terminal slot depth (all) | 3.0 mm into wall from Y=0 | Y | Leaves 5.5 mm rear wall behind |
| Motor terminal slot size | 8.0 x 8.5 mm (X x Z) | XZ | For 6.3 mm blade housing |
| Cart-present slot size | 18.0 x 7.0 mm (X x Z) | XZ | For 2-pin 4.8 mm housing |
| Wire pass-through diameter | 3.0 mm | - | 4 holes, concentric with T1-T4 |
| Wire channel width | 6.0 mm | X | Floor channels for 2x 22AWG |
| Wire channel depth | 2.0 mm | Z | Cut into 3 mm floor from Z=3 to Z=1 |
| Left wire channel X range | 22..28 mm | X | Pump 1 wires |
| Right wire channel X range | 132..138 mm | X | Pump 2 wires |
| Wire channel Y range | 9..124 mm | Y | From rear wall interior to pump motor zone |
