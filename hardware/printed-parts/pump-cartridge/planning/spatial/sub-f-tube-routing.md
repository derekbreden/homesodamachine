# Sub-F: Tube Routing Channels — Spatial Resolution

## 1. System-Level Placement

```
Mechanism: Tube Routing Channels (4x U-channels with snap clips)
Parent: Tray (Sub-A box shell), interior floor surface
Position: Floor zone between pump barbs (Y~35) and fitting ports (Y~22)
Orientation: Aligned with tray frame (no rotation)
Reference frame: Tray frame — origin at rear-left-bottom corner
  X = width (0..160), left-to-right
  Y = depth (0=dock/rear, 155=user/front), rear-to-front
  Z = height (0..72), bottom-to-top
  Floor inner surface at Z = 3
```

The tube routing channels occupy the floor zone between the pump heads and the rear wall. Four 1/4" OD (6.35mm) silicone tubes route from pump barb exits to John Guest fitting ports. The tubes descend from barb height to the floor, run along U-channels on the floor, and rise to the fitting port height at the rear wall.

---

## 2. Reference Frame

Sub-F features are specified directly in the tray reference frame. No sub-component-local frame is needed — all channels are prismatic features (extrusions or cuts along Z) applied to the floor surface, and all positions are given as (X, Y, Z) in the tray frame.

```
Sub-F reference frame = Tray reference frame
  Origin: rear-left-bottom corner of tray outer envelope
  X: 0..160 (width, left to right)
  Y: 0..155 (depth, dock to user)
  Z: 0..72 (height, bottom to top)
  Floor inner surface: Z = 3
  Left wall inner face: X = 5
  Right wall inner face: X = 155
  Rear wall inner face: Y = 8.5
```

---

## 3. Derived Geometry

### 3a. Tube Start Points — Pump Barb Exit Positions

**Source:** Sub-C spatial resolution, section 3f.

Each pump has two barbed tube connectors on the pump head front face, which faces rearward (toward Y=0). The pump tube-connector face is at Y = 35.00.

| Barb ID | X (mm) | Y (mm) | Z (mm) | Confidence | Notes |
|---------|--------|--------|--------|------------|-------|
| P1-lower | 43.20 | 35.00 | ~25 | **LOW** | Pump 1, lower barb. Z estimated — not caliper-verified. |
| P1-upper | 43.20 | 35.00 | ~44 | **LOW** | Pump 1, upper barb. Z estimated — not caliper-verified. |
| P2-lower | 116.80 | 35.00 | ~25 | **LOW** | Pump 2, lower barb. Z estimated — not caliper-verified. |
| P2-upper | 116.80 | 35.00 | ~44 | **LOW** | Pump 2, upper barb. Z estimated — not caliper-verified. |

**What is known with confidence:**
- X positions are HIGH confidence: barbs are approximately centered on the pump head, which is centered on the pump mounting bracket. Pump centerlines at X = 43.20 and 116.80 (from Sub-C).
- Y position is HIGH confidence: barbs exit from the pump tube-connector face at Y = 35.00 (from Sub-C).
- Z positions are LOW confidence: the geometry description doc lists tube connector exit positions as "Remaining Unknowns." The ~25mm and ~44mm estimates assume the barbs are offset symmetrically above and below the pump center axis (Z = 34.30) by approximately 9mm. This is a rough estimate from visual inspection of the pump photos.

**Impact of LOW-confidence barb Z positions on channel design:** The 1/4" silicone tubing is flexible. The short vertical run from barb to floor (~22mm for the lower barb, ~41mm for the upper barb) is unconstrained by the channel geometry — the tube simply drops from the barb and enters the channel at floor level. The barb Z uncertainty affects the vertical drop length but not the floor channel positions.

### 3b. Tube End Points — Fitting Port Positions

**Source:** Sub-D fitting bore array geometry (from decomposition and decision docs).

The John Guest PP0408W fittings are mounted in the tray rear wall in a 2x2 grid at 20mm center-to-center, centered on the rear wall. The user-facing (interior) port faces are where tubes connect.

**Fitting bore centers (in the rear wall):**

| Fitting ID | X (mm) | Y_bore_center (mm) | Z (mm) | Grid position |
|------------|--------|---------------------|--------|---------------|
| F-LL | 70.00 | 4.25 | 26.00 | Lower-left |
| F-UL | 70.00 | 4.25 | 46.00 | Upper-left |
| F-LR | 90.00 | 4.25 | 26.00 | Lower-right |
| F-UR | 90.00 | 4.25 | 46.00 | Upper-right |

**Derivation of bore centers:**
- X: Grid centered on rear wall width. Wall X = 0..160, center = 80. Two columns at 80 - 10 = 70 and 80 + 10 = 90.
- Z: Grid centered on rear wall height. Wall Z = 0..72, center = 36. Two rows at 36 - 10 = 26 and 36 + 10 = 46.
- Y: Bore is a through-hole in the 8.5mm rear wall. Bore midplane at Y = 8.5/2 = 4.25.

**User-facing port face positions:**

The fitting center body (12.16mm long) is longer than the 8.5mm rear wall. It protrudes symmetrically on both sides: (12.16 - 8.5) / 2 = 1.83mm per side. The user-facing body end section (12.08mm long) extends inward from the inner shoulder.

| Fitting ID | Port face X (mm) | Port face Y (mm) | Port face Z (mm) | Confidence |
|------------|------------------|-------------------|-------------------|------------|
| F-LL | 70.00 | 22.41 | 26.00 | HIGH |
| F-UL | 70.00 | 22.41 | 46.00 | HIGH |
| F-LR | 90.00 | 22.41 | 26.00 | HIGH |
| F-UR | 90.00 | 22.41 | 46.00 | HIGH |

**Derivation of port face Y:**
- Rear wall interior face: Y = 8.50
- Center body protrusion into interior: 1.83mm (shoulder at Y = 8.50 + 1.83 = 10.33)
- Body end section length: 12.08mm
- Port face: Y = 10.33 + 12.08 = **22.41mm**

The tube inserts ~16mm into the port. The tube end inside the fitting is at Y ~ 22.41 - 16 = 6.41 (inside the fitting body). The external tube begins at the port face, Y = 22.41.

### 3c. Tube-to-Fitting Assignment

Each pump connects to the nearest fitting column to minimize lateral routing distance:

| Tube ID | From (barb) | To (fitting) | Description |
|---------|-------------|--------------|-------------|
| Tube A | P1-lower | F-LL | Pump 1 lower barb → lower-left fitting |
| Tube B | P1-upper | F-UL | Pump 1 upper barb → upper-left fitting |
| Tube C | P2-lower | F-LR | Pump 2 lower barb → lower-right fitting |
| Tube D | P2-upper | F-UR | Pump 2 upper barb → upper-right fitting |

**Rationale:** Pump 1 (X = 43.20) is closer to the left fitting column (X = 70) — 26.8mm lateral offset. Pump 2 (X = 116.80) is closer to the right fitting column (X = 90) — 26.8mm lateral offset. Both pump pairs converge toward the tray center.

**Note on inlet vs. outlet assignment:** Which barb is "inlet" and which is "outlet" determines fluid flow direction. The specific assignment (lower barb = inlet, upper = outlet) is a placeholder. The physical barb assignment should be confirmed during prototyping. The tube routing geometry is the same regardless of which barb is inlet or outlet — the channel positions and paths do not change.

### 3d. Direct Barb-to-Fitting Distances

| Tube | Delta X | Delta Y | Delta Z | Straight-line (mm) |
|------|---------|---------|---------|---------------------|
| A | +26.80 | -12.59 | +1.00 | 29.62 |
| B | +26.80 | -12.59 | +2.00 | 29.66 |
| C | -26.80 | -12.59 | +1.00 | 29.62 |
| D | -26.80 | -12.59 | +2.00 | 29.66 |

The straight-line distances are very short (~30mm). The actual tube paths are longer because the tubes descend from barb height to the floor, run along the floor, then rise to the fitting port height. Estimated tube length per line: 50-70mm (accounting for vertical drops and rises plus the floor routing path).

### 3e. Channel Cross-Section Dimensions

All four channels share identical cross-section geometry:

```
Channel cross-section (looking along the channel centerline):

        10.00mm
    ├──────────────┤
    ┌──────────────┐ ─┬─
    │              │  │
    │   ○ tube     │  │ 10.00mm depth
    │   6.35mm OD  │  │
    │              │  │
────┴──────────────┴──┴── Floor surface (Z = 3)
```

| Parameter | Value (mm) | Rationale |
|-----------|------------|-----------|
| Channel width | 10.00 | 6.35mm tube OD + 3.65mm clearance (1.82mm per side) |
| Channel depth | 10.00 | Full tube containment + clip space above |
| Wall thickness between adjacent channels | 2.00 | Minimum printable wall for PETG at FDM resolution |
| Tube centerline height in channel | Z = 8.18 | Z = 3 (floor) + 10/2 (half-depth) + tube sag ≈ 3 + 5 = 8 |
| Channel floor | Z = 3.00 | The tray floor inner surface |
| Channel wall tops | Z = 13.00 | Z = 3 + 10 (channel depth) |
| Snap clip clearance above tube | 13.00 - (8.18 + 3.18) = 1.64 | Clip tab sits above tube crown |

**Channel implementation:** Raised walls on the floor surface, forming U-shaped troughs. Each channel is bounded by two parallel walls (2mm thick, 10mm tall) separated by 10mm gap. This is a UNION operation: walls are extruded upward from the floor.

### 3f. Floor Routing Paths (XY Projections)

The tubes route along the tray floor between the pump zone (Y~35) and the fitting zone (Y~22). Each tube's floor path is defined by waypoints in (X, Y) at the tube centerline height (Z ~ 8).

**Channel pair layout:** Each pump's two tubes run as a parallel pair, with 12mm center-to-center channel spacing (10mm channel + 2mm wall). The channels within each pair are labeled "inner" (closer to tray center X = 80) and "outer" (farther from center).

**Pump 1 pair (Tubes A & B), left side of tray:**

Tube A (inner channel): routes from near X = 43.2 to X = 64 (fitting X = 70, minus half channel pair width)
Tube B (outer channel): routes from near X = 43.2 to X = 76 (inner + 12mm)

Wait — the fitting column is at X = 70, and the two tubes from Pump 1 both connect to fittings at X = 70. They need to arrive at the same X but different Z (26 and 46). On the floor, both tubes can run in adjacent channels at the same X at the rear wall, then each rises to its respective fitting port height.

**Revised channel pair strategy at fitting end:** Both channels from one pump converge to a pair straddling the fitting column X. At X = 70: inner channel at X = 64, outer channel at X = 76. Similarly at X = 90: inner channel at X = 84, outer channel at X = 96.

Gap between the two pairs at the fitting end: 84 - 76 = 8mm (sufficient for a structural wall).

**Routing waypoints — Tube A (P1-lower → F-LL):**

| Waypoint | X (mm) | Y (mm) | Description |
|----------|--------|--------|-------------|
| W-A1 | 37.20 | 33.00 | Channel entry: tube descends from barb, enters channel. X offset from pump center to accommodate pair spacing. |
| W-A2 | 37.20 | 28.00 | Short straight run toward rear wall |
| W-A3 | 64.00 | 16.00 | Channel end near fitting column. Diagonal run with gentle curve. |

- Start-to-end XY distance: delta X = 26.8mm, delta Y = 17mm, path length ~32mm
- Tube at W-A3 rises from floor to fitting F-LL port at (70, 22.41, 26)

**Routing waypoints — Tube B (P1-upper → F-UL):**

| Waypoint | X (mm) | Y (mm) | Description |
|----------|--------|--------|-------------|
| W-B1 | 49.20 | 33.00 | Channel entry: parallel to Tube A, 12mm further right |
| W-B2 | 49.20 | 28.00 | Short straight run toward rear wall |
| W-B3 | 76.00 | 16.00 | Channel end near fitting column |

**Routing waypoints — Tube C (P2-lower → F-LR):**

| Waypoint | X (mm) | Y (mm) | Description |
|----------|--------|--------|-------------|
| W-C1 | 122.80 | 33.00 | Channel entry (mirror of Tube A about X = 80) |
| W-C2 | 122.80 | 28.00 | Short straight run |
| W-C3 | 96.00 | 16.00 | Channel end near fitting column |

**Routing waypoints — Tube D (P2-upper → F-UR):**

| Waypoint | X (mm) | Y (mm) | Description |
|----------|--------|--------|-------------|
| W-D1 | 110.80 | 33.00 | Channel entry (mirror of Tube B about X = 80) |
| W-D2 | 110.80 | 28.00 | Short straight run |
| W-D3 | 84.00 | 16.00 | Channel end near fitting column |

**Bend radius verification:**

The diagonal segment from W2 to W3 for each tube spans:
- Tube A: delta X = 64 - 37.2 = 26.8mm, delta Y = 28 - 16 = 12mm
- Path angle from Y axis: arctan(26.8 / 12) = 65.9 degrees
- The tube transitions from a Y-parallel segment (W1-W2) to this diagonal. The bend at W2 turns 65.9 degrees.
- Required bend radius: 25mm minimum for 1/4" silicone tubing.
- Arc length for a 25mm radius, 65.9-degree turn: 25 * (65.9 * pi/180) = 28.8mm
- Available path length from W1 to W3: ~32mm

The 25mm bend radius arc nearly consumes the entire available path length. This means the W1-to-W3 path should be modeled as a single smooth arc rather than a straight-diagonal segment. The channel walls should follow a smooth curve with no sharp corners.

**Revised approach — smooth arc routing:**

Rather than piecewise-linear waypoints, each channel follows a single smooth curve from its entry point to its end point near the fitting column. The curve maintains a minimum 25mm radius throughout.

**Tube A arc (representative — other tubes mirror or parallel this):**

```
Arc from (37.2, 33.0) to (64.0, 16.0):
  Chord length: sqrt(26.8^2 + 17^2) = 31.7mm
  Chord angle from X axis: arctan(17/26.8) = 32.4 degrees below horizontal
  For a circular arc with R = 30mm (above minimum):
    Arc subtended angle: 2 * arcsin(chord / (2*R)) = 2 * arcsin(31.7/60) = 63.6 degrees
    Arc length: 30 * (63.6 * pi/180) = 33.3mm
```

A 30mm radius arc (above the 25mm minimum) fits the available space and produces a smooth, printable channel wall.

**XY path table — Tube A channel centerline, sampled at 5mm Y intervals:**

| Y (mm) | X (mm) | Notes |
|--------|--------|-------|
| 33.0 | 37.2 | Channel entry (near pump barb drop zone) |
| 28.0 | 42.5 | Curving toward center |
| 23.0 | 50.0 | Mid-route |
| 18.0 | 57.5 | Approaching fitting column |
| 16.0 | 64.0 | Channel end (tube rises to fitting port) |

**XY path table — Tube B channel centerline (parallel to A, +12mm X offset):**

| Y (mm) | X (mm) | Notes |
|--------|--------|-------|
| 33.0 | 49.2 | Channel entry |
| 28.0 | 54.5 | Curving toward center |
| 23.0 | 62.0 | Mid-route |
| 18.0 | 69.5 | Approaching fitting column |
| 16.0 | 76.0 | Channel end |

**XY path table — Tube C channel centerline (mirror of A about X = 80):**

| Y (mm) | X (mm) | Notes |
|--------|--------|-------|
| 33.0 | 122.8 | Channel entry |
| 28.0 | 117.5 | Curving toward center |
| 23.0 | 110.0 | Mid-route |
| 18.0 | 102.5 | Approaching fitting column |
| 16.0 | 96.0 | Channel end |

**XY path table — Tube D channel centerline (mirror of B about X = 80):**

| Y (mm) | X (mm) | Notes |
|--------|--------|-------|
| 33.0 | 110.8 | Channel entry |
| 28.0 | 105.5 | Curving toward center |
| 23.0 | 98.0 | Mid-route |
| 18.0 | 90.5 | Approaching fitting column |
| 16.0 | 84.0 | Channel end |

### 3g. Vertical Transition Zones

At each end of a floor channel, the tube transitions from the floor plane to a higher connection point. These transitions are not constrained by printed channels — the silicone tubing is flexible and self-supporting over these short vertical runs. The channels simply terminate with open ends.

**Pump-side vertical drop (all 4 tubes):**

| Tube | Drop from Z (barb) | To Z (channel) | Drop height (mm) | Notes |
|------|-------------------|-----------------|-------------------|-------|
| A | ~25 | 8 | ~17 | Short gentle bend, LOW confidence on start Z |
| B | ~44 | 8 | ~36 | Longer drop, LOW confidence on start Z |
| C | ~25 | 8 | ~17 | Mirror of A |
| D | ~44 | 8 | ~36 | Mirror of B |

The tube exits the barb horizontally (toward -Y) and bends downward to enter the floor channel. With 25mm minimum bend radius, the vertical-to-horizontal transition requires approximately 25mm of Y travel. This is accounted for in the channel entry positions (Y = 33, which is 2mm behind the barb face at Y = 35).

**Fitting-side vertical rise (all 4 tubes):**

| Tube | Rise from Z (channel) | To Z (fitting port) | Rise height (mm) | Y at channel end | Y at fitting port |
|------|----------------------|---------------------|-------------------|-----------------|-------------------|
| A | 8 | 26 | 18 | 16.0 | 22.41 |
| B | 8 | 46 | 38 | 16.0 | 22.41 |
| C | 8 | 26 | 18 | 16.0 | 22.41 |
| D | 8 | 46 | 38 | 16.0 | 22.41 |

The tube exits the floor channel end and curves upward and rearward (-Y) to enter the fitting port. The fitting port faces toward +Y (into the cartridge interior). The tube must make a ~90-degree bend from floor-horizontal to fitting-horizontal. With a 25mm bend radius, this 90-degree curve spans 25mm vertically and 25mm in Y. The available space from channel end (Y = 16) to rear wall interior (Y = 8.5) is 7.5mm — insufficient for a floor-level 90-degree bend.

**Resolution:** The tubes do not stay at floor level all the way to the rear wall. The channel ends at Y = 16, and the tube curves upward and backward simultaneously in a smooth 3D arc. The vertical rise and Y-direction travel happen together. From the channel end at (X, 16, 8), the tube sweeps up and back to reach the port at (fitting_X, 22.41, fitting_Z). This is a diagonal 3D curve, not a pure vertical rise.

For Tube A: from (64, 16, 8) to (70, 22.41, 26). Distance = sqrt(6^2 + 6.41^2 + 18^2) = sqrt(36 + 41.1 + 324) = sqrt(401.1) = 20mm. This is well within the silicone tube's flexibility for a smooth curve without a printed channel guide.

For Tube B: from (76, 16, 8) to (70, 22.41, 46). Distance = sqrt(6^2 + 6.41^2 + 38^2) = sqrt(36 + 41.1 + 1444) = sqrt(1521.1) = 39mm. Also achievable as a free-form tube curve.

### 3h. Snap Clip Positions

Snap clips retain the tube in the U-channel. Each clip is a pair of small overhanging tabs on opposite channel walls that flex outward when the tube is pressed in and snap back to hold it.

Given the short channel lengths (~18-33mm of floor routing per tube), one clip per channel is sufficient. Two clips would over-constrain the short run.

**Clip positions (1 per channel, at the midpoint of each channel's floor run):**

| Channel | Clip X (mm) | Clip Y (mm) | Notes |
|---------|------------|------------|-------|
| Tube A | 50.0 | 23.0 | Midpoint of A's floor path |
| Tube B | 62.0 | 23.0 | Midpoint of B's floor path |
| Tube C | 110.0 | 23.0 | Midpoint of C's floor path (mirror of A) |
| Tube D | 98.0 | 23.0 | Midpoint of D's floor path (mirror of B) |

**Clip geometry (all clips identical):**

| Parameter | Value (mm) | Notes |
|-----------|------------|-------|
| Tab length along channel | 5.00 | Along the channel run direction |
| Tab overhang into channel | 2.00 | From each wall, total gap = 10 - 2*2 = 6mm (tube OD = 6.35 snaps past) |
| Tab thickness | 1.00 | Thin enough to flex for tube insertion |
| Tab height (Z position) | Z = 10 to Z = 13 | Upper portion of channel wall |
| Undercut below tab | 0.50 | Small relief so tab can deflect outward |

The 6mm gap between opposing tabs is slightly less than the 6.35mm tube OD, creating a snap engagement of ~0.175mm per side. PETG flex allows the 1mm-thick tab to deflect the needed 0.175mm without permanent deformation.

### 3i. Channel Envelope and Interference Check

**Total channel zone footprint on the floor:**

```
Floor plan (Z = 3 to Z = 13), looking down:

Y=33  ┌─A─┐     ┌─B─┐                   ┌─D─┐     ┌─C─┐
      │   │     │   │                   │   │     │   │
Y=23  │  ╲│     │╱  │                   │  ╲│     │╱  │
      │   ╲     ╱   │                   │   ╲     ╱   │
Y=16  └───┘     └───┘                   └───┘     └───┘
     X:35  47  47  59                  X:99  111 111  125
              ↓                                ↓
     (converges to X=64..76)          (converges to X=84..96)

Channel walls at widest point (Y=33):
  A outer wall: X = 37.2 - 5 = 32.2 to X = 37.2 + 5 = 42.2
  B outer wall: X = 49.2 - 5 = 44.2 to X = 49.2 + 5 = 54.2
  Shared wall between A and B: X = 42.2 to X = 44.2 (2mm wall)

  C outer wall: X = 122.8 - 5 = 117.8 to X = 122.8 + 5 = 127.8
  D outer wall: X = 110.8 - 5 = 105.8 to X = 110.8 + 5 = 115.8
  Shared wall between D and C: X = 115.8 to X = 117.8 (2mm wall)
```

**Interference with Sub-C pump mounting bosses:**
- Boss positions: (18.48, 83.00), (67.93, 83.00), (92.08, 83.00), (141.53, 83.00)
- Channel zone: Y = 16 to 33
- Boss zone: Y ~ 83 (point features)
- **No interference.** The channels and bosses do not overlap in Y. Channels occupy Y = 16..33; bosses are at Y = 83.

**Interference with Sub-C motor cradles:**
- Cradle footprints: X = 22.45..63.95, Y = 109..124 (Cradle 1); X = 96.05..137.55, Y = 109..124 (Cradle 2)
- **No interference.** Cradles are at Y = 109..124; channels are at Y = 16..33.

**Clearance between channel pairs at fitting end:**
- Pump 1 pair right edge at fitting end: X = 76 + 5 = 81 (outer wall of Tube B channel)
- Pump 2 pair left edge at fitting end: X = 84 - 5 = 79 (outer wall of Tube D channel)
- **Overlap: 81 - 79 = 2mm.** The inner walls of the two pairs meet at X ~ 80, which is acceptable — they share a single 2mm wall at the tray centerline.

**Clearance to tray side walls:**
- Tube A channel left wall at entry: X = 32.2. Left wall inner face: X = 5.0. Clearance: **27.2mm** (ample).
- Tube C channel right wall at entry: X = 127.8. Right wall inner face: X = 155.0. Clearance: **27.2mm** (ample).

---

## 4. Interface Boundary Summary

### Interface: Channels to Floor (Sub-A)

All channel walls bond to the interior floor surface at Z = 3.00mm. The channel walls are extruded upward (UNION operation) from Z = 3 to Z = 13 (10mm tall).

| Channel pair | Floor contact zone (X range at Y=33, widest) | Y range |
|-------------|----------------------------------------------|---------|
| Pump 1 pair (A+B) | X: 32.2 to 54.2 (entry) → 59 to 81 (end) | Y: 16 to 33 |
| Pump 2 pair (C+D) | X: 105.8 to 127.8 (entry) → 79 to 101 (end) | Y: 16 to 33 |

Mating feature: interior floor surface of Sub-A box shell, Z = 3.00.

### Interface: Channel entries to pump barb zone (Sub-C)

Channels open at Y = 33 toward the pump zone. Tubes drop from barb height to channel level and enter the open channel ends. No printed connection between channel and pump — the tube is the flexible link.

| Channel | Entry opening center (X, Y) | Receives tube from barb at |
|---------|----------------------------|---------------------------|
| A | (37.2, 33.0) | P1-lower at (~43.2, 35.0, ~25) |
| B | (49.2, 33.0) | P1-upper at (~43.2, 35.0, ~44) |
| C | (122.8, 33.0) | P2-lower at (~116.8, 35.0, ~25) |
| D | (110.8, 33.0) | P2-upper at (~116.8, 35.0, ~44) |

### Interface: Channel ends to fitting zone (Sub-D)

Channels open at Y = 16 toward the rear wall. Tubes exit the open channel ends and curve upward/rearward to reach the fitting ports.

| Channel | Exit opening center (X, Y) | Tube routes to fitting port at |
|---------|---------------------------|-------------------------------|
| A | (64.0, 16.0) | F-LL at (70.0, 22.41, 26.0) |
| B | (76.0, 16.0) | F-UL at (70.0, 22.41, 46.0) |
| C | (96.0, 16.0) | F-LR at (90.0, 22.41, 26.0) |
| D | (84.0, 16.0) | F-UR at (90.0, 22.41, 46.0) |

---

## 5. Transform Summary

```
Sub-F frame = Tray frame (identity transform, no rotation or translation)

Verification points:
  Channel A entry at tray (37.2, 33.0, 8) — 32.2mm from left wall, 24.5mm from rear wall ✓
  Channel C entry at tray (122.8, 33.0, 8) — mirror of A: 155 - 122.8 = 32.2mm from right wall ✓
  Pump 1 pair center X at entry: (37.2 + 49.2) / 2 = 43.2 = pump 1 centerline ✓
  Pump 2 pair center X at entry: (122.8 + 110.8) / 2 = 116.8 = pump 2 centerline ✓
  Channel pair symmetry about X = 80: A_entry_X = 37.2, C_entry_X = 122.8, (37.2 + 122.8)/2 = 80.0 ✓
  Shared center wall at fitting end: B_end_X = 76, D_end_X = 84, midpoint = 80 = tray center ✓
```

---

## 6. Confidence Summary

| Dimension | Confidence | Blocking? | Notes |
|-----------|------------|-----------|-------|
| Fitting bore positions (X, Z) | HIGH | No | Derived from centered 2x2 grid at 20mm c-c, per decision doc |
| Fitting port face Y | HIGH | No | Derived from caliper-verified John Guest dimensions |
| Pump centerline X | HIGH | No | From Sub-C, well-constrained by bracket width |
| Pump barb face Y | HIGH | No | From Sub-C, Y = 35.00 |
| Pump barb Z offsets | **LOW** | **No** | Not caliper-verified. Tube flexibility absorbs uncertainty. |
| Channel cross-section | HIGH | No | Standard 10x10mm for 1/4" tubing, per decomposition |
| Bend radius (25mm min) | HIGH | No | Standard for 1/4" silicone tubing |
| Fitting grid center Z = 36 | MEDIUM | No | "Centered on rear wall" could mean centered on wall height (Z=36) or centered on interior height (Z=37.5). Using Z=36. |

**LOW-confidence items do not block channel design.** The pump barb Z positions affect only the unconstrained vertical tube drops, not the printed channel geometry. The floor channels are robust to barb position uncertainty because the flexible tube bridges the gap between the barb and the channel entry.

---

## 7. Dimensional Summary Table

All values in tray reference frame (mm).

| Parameter | Value | Source |
|-----------|-------|--------|
| Tube OD (silicone) | 6.35 | 1/4" nominal |
| Channel width | 10.00 | Decomposition (6.35 + clearance) |
| Channel depth | 10.00 | Decomposition |
| Channel wall thickness | 2.00 | Minimum printable PETG wall |
| Channel wall height | Z = 3 to Z = 13 | Floor + 10mm depth |
| Inter-channel spacing (center-to-center, same pair) | 12.00 | 10mm channel + 2mm wall |
| Minimum bend radius | 25.00 | 1/4" silicone tubing spec |
| Design bend radius (floor paths) | 30.00 | Above minimum, fits available space |
| Floor routing zone Y range | 16.0 to 33.0 | Between fitting zone and pump zone |
| Floor routing zone Y length | 17.0 | Channel length along Y |
| Pump 1 pair X range at entry | 32.2 to 54.2 | Centered on pump 1 X = 43.2 |
| Pump 2 pair X range at entry | 105.8 to 127.8 | Centered on pump 2 X = 116.8 |
| Pump 1 pair X range at exit | 59.0 to 81.0 | Approaching fitting column X = 70 |
| Pump 2 pair X range at exit | 79.0 to 101.0 | Approaching fitting column X = 90 |
| Snap clips per channel | 1 | Short channel length (~18-33mm) |
| Clip overhang per side | 2.00 | Creates 6mm snap gap for 6.35mm tube |
| Clip tab thickness | 1.00 | PETG flex allows 0.175mm deflection |
| Clip tab length along channel | 5.00 | Adequate retention surface |
| Fitting port face Y | 22.41 | Caliper-verified JG dimensions |
| Fitting bore X positions | 70.0, 90.0 | Centered 2x2 grid |
| Fitting bore Z positions | 26.0, 46.0 | Centered 2x2 grid |
