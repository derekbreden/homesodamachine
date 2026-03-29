# Sub-C: Pump Mounting Bosses — Spatial Resolution

## 1. System-Level Placement

```
Mechanism: Pump Mounting Bosses + Motor Cradles
Parent: Tray (Sub-A box shell)
Position: Interior floor of the tray, mid-depth zone
Orientation: Aligned with tray frame (no rotation)
Reference frame: Tray frame — origin at rear-left-bottom corner
  X = width (0..160), left-to-right
  Y = depth (0=dock/rear, 155=user/front), rear-to-front
  Z = height (0..72), bottom-to-top
  Floor inner surface at Z = 3
```

The two pumps sit side by side across X, motors pointing forward (toward user, +Y direction), tube barbs pointing rearward (toward dock, -Y direction). The mounting bracket at the head/motor junction is the fastening plane.

---

## 2. Reference Frame

Sub-C features are specified directly in the tray reference frame. No sub-component-local frame is needed — all bosses and cradles are prismatic extrusions along Z from the floor plane, and all positions are given as (X, Y, Z) in the tray frame.

```
Sub-C reference frame = Tray reference frame
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

### 3a. Pump Placement — Side-by-Side Layout

**Design constraints:**
- Tray inner width: 150mm (X = 5 to X = 155)
- Each pump bracket width: 68.6mm
- Inter-pump gap: 5mm (bracket edge to bracket edge)
- Combined footprint: 68.6 + 5 + 68.6 = 142.2mm
- Remaining wall clearance: (150 - 142.2) / 2 = 3.9mm per side

**Pump centerlines (X):**

| Pump | Centerline X | Left bracket edge X | Right bracket edge X |
|------|-------------|---------------------|----------------------|
| Pump 1 (left) | 43.20 | 8.90 | 77.50 |
| Pump 2 (right) | 116.80 | 82.50 | 151.10 |

Derivation:
- Pair centered at X = 80.0 (tray centerline)
- Pump 1 center: 80.0 - 5/2 - 68.6/2 = 80.0 - 2.5 - 34.3 = **43.20mm**
- Pump 2 center: 80.0 + 5/2 + 68.6/2 = 80.0 + 2.5 + 34.3 = **116.80mm**

**Wall clearances:**
- Pump 1 left bracket edge to left wall: 8.90 - 5.00 = **3.90mm**
- Pump 2 right bracket edge to right wall: 155.00 - 151.10 = **3.90mm**
- Inter-pump bracket gap: 82.50 - 77.50 = **5.00mm**

**Pump head envelope clearances:**
- Pump head width: 62.6mm, centered on pump centerline
- Pump 1 head: X = 43.20 - 31.3 = 11.90 to X = 43.20 + 31.3 = 74.50
- Pump 2 head: X = 116.80 - 31.3 = 85.50 to X = 116.80 + 31.3 = 148.10
- Head-to-head gap: 85.50 - 74.50 = **11.00mm**
- Head to left wall: 11.90 - 5.00 = **6.90mm**
- Head to right wall: 155.00 - 148.10 = **6.90mm**

### 3b. Pump Depth Positioning (Y Axis)

**Pump orientation:** Tube barbs face rear (toward Y=0 / dock). Motor faces front (toward Y=155 / user).

**Key Y stations along the pump, measured from the pump's tube-connector face:**

| Station | Offset from tube face | Tray Y coordinate |
|---------|----------------------|-------------------|
| Tube connector face | 0mm | Y = 35.00 |
| Pump head rear face | 48mm | Y = 83.00 |
| Mounting bracket | ~48mm | Y = 83.00 |
| Motor adapter plate | ~48–52mm | Y = 83–87 |
| Motor body start | ~52mm | Y = 87.00 |
| Motor end cap (no nub) | ~111.4mm | Y = 146.43 |
| Motor shaft nub tip | ~116.5mm | Y = 151.48 |

**Derivation:** Pump tube-connector face placed at Y = 35.00mm. This provides:
- ~26.5mm routing distance from tube barbs back to rear wall interior (Y=8.5)
- Motor nub tip at Y = 151.48, giving **3.52mm clearance** to tray front edge (Y=155)
- Motor end cap at Y = 146.43, giving **8.57mm clearance** to front edge (adequate for terminal wiring)

**Bracket (mounting) plane: Y = 83.00mm**

### 3c. Pump Vertical Positioning (Z Axis)

**Constraint:** The pump head (62.6mm tall) must fit within the tray interior height.
- Tray inner height: Z = 3 (floor) to Z = 72 (top edge) = 69mm available
- Pump head height: 62.6mm
- Remaining vertical budget: 69 - 62.6 = 6.4mm

**Solution:** Pump head bottom rests on the floor surface. This maximizes stability and minimizes boss height.

| Datum | Z coordinate |
|-------|-------------|
| Floor inner surface | Z = 3.00 |
| Pump head bottom | Z = 3.00 |
| Pump / motor center axis | Z = 3.00 + 31.3 = **34.30** |
| Pump head top | Z = 3.00 + 62.6 = **65.60** |
| Top clearance to tray wall | 72.00 - 65.60 = **6.40mm** |

**Mounting bracket hole center height: Z = 34.30mm**

The bracket holes are centered on the pump body (the ears are at the same height as the pump center axis). Therefore the bosses must rise from the floor (Z=3) to Z=34.30.

### 3d. Mounting Boss Positions — All 4 Bosses

All bosses are at the bracket plane Y = 83.00mm, and at the bracket hole height Z = 34.30mm.

| Boss ID | X (mm) | Y (mm) | Z (hole center) | Notes |
|---------|--------|--------|-----------------|-------|
| P1-L | 18.48 | 83.00 | 34.30 | Pump 1, left ear |
| P1-R | 67.93 | 83.00 | 34.30 | Pump 1, right ear |
| P2-L | 92.08 | 83.00 | 34.30 | Pump 2, left ear |
| P2-R | 141.53 | 83.00 | 34.30 | Pump 2, right ear |

**Derivation of X positions:**
- P1-L: 43.20 - 49.45/2 = 43.20 - 24.725 = **18.475 -> 18.48mm**
- P1-R: 43.20 + 49.45/2 = 43.20 + 24.725 = **67.925 -> 67.93mm**
- P2-L: 116.80 - 49.45/2 = 116.80 - 24.725 = **92.075 -> 92.08mm**
- P2-R: 116.80 + 49.45/2 = 116.80 + 24.725 = **141.525 -> 141.53mm**

**Boss geometry:**
- Base: on floor at Z = 3.00
- Top face (bracket bearing surface): Z = 34.30 (where the bracket rests)
- Height above floor: 34.30 - 3.00 = **31.30mm**
- Pilot hole for M3 x 5.7mm heat-set insert: 4.0mm diameter, bored into top face

**Note on boss height:** The 31.3mm boss height is substantially taller than the decomposition's initial "5-8mm" rough estimate. This is correct — the bracket holes are centered on the 62.6mm pump head, so the hole center is 31.3mm above the pump head bottom, which sits on the floor. At this height, plain cylindrical bosses (8mm OD) will be slender columns. The specification agent should consider reinforcing ribs or conical tapers for print stability and stiffness.

### 3e. Motor Cradle Positions and Geometry

The motor body is a ~35mm diameter cylinder, coaxial with the pump center axis at Z = 34.30mm. It extends from approximately Y = 87 (adapter plate) to Y = 146 (end cap).

**Cradle placement (Y):** One cradle per pump, positioned at the midpoint of the motor body length.
- Motor body Y span: 87 to 146, midpoint at Y = **116.50mm**

**Cradle center (X):** Aligned with each pump centerline.

| Cradle | Center X | Center Z | Y position |
|--------|----------|----------|------------|
| Cradle 1 (Pump 1) | 43.20 | 34.30 | 116.50 |
| Cradle 2 (Pump 2) | 116.80 | 34.30 | 116.50 |

**Cradle profile (cross-section in XZ plane):**
The cradle is a semicircular rib supporting the motor from below. The motor center is at Z = 34.30mm, well above the floor.

```
Cradle inner profile (semicircle, bottom half):
  Center: (pump_centerline_X, 34.30)
  Inner radius: 17.75mm (for ~35.5mm ID, providing 0.25mm diametral clearance on ~35mm motor)
  Arc: 180°, from 9 o'clock to 3 o'clock (open at top)
  Inner surface lowest point: Z = 34.30 - 17.75 = 16.55mm
```

**Cradle wall thickness:** 3mm (per decomposition estimate)
- Outer radius: 17.75 + 3 = 20.75mm

**Cradle Z extent:**
- Solid support rib from floor (Z=3) up to the cradle arc start (Z=16.55)
- Rib height: 16.55 - 3.00 = 13.55mm
- Semicircular arc from Z=16.55 up to Z=34.30 on each side (half-pipe walls)
- Cradle arm tops at Z = 34.30 + 17.75 + 3 = 55.05mm (outer radius top)

**Cradle X extent (footprint):**
- Cradle 1: X = 43.20 - 20.75 = 22.45 to X = 43.20 + 20.75 = 63.95
- Cradle 2: X = 116.80 - 20.75 = 96.05 to X = 116.80 + 20.75 = 137.55

**Cradle-to-wall clearance:**
- Cradle 1 left edge to left wall: 22.45 - 5.00 = **17.45mm** (ample)
- Cradle 2 right edge to right wall: 155.00 - 137.55 = **17.45mm** (ample)
- Inter-cradle gap: 96.05 - 63.95 = **32.10mm** (ample)

**Cradle depth (Y extent):** ~15mm thick rib centered at Y=116.50 (Y = 109.00 to 124.00). This provides adequate bearing length without over-constraining motor thermal expansion.

### 3f. Tube Barb Exit Positions (Reference for Sub-F Routing)

Each pump has two tube barbs exiting the front face (which faces toward Y=0, the dock/rear). The exact X/Z offsets of the barbs on the pump face are not caliper-verified (listed as unknown in the geometry document). However, the following is known:

- Barbs exit at Y = 35.00 (pump tube-connector face)
- Barbs are approximately centered on the 62.6mm pump face, offset symmetrically above and below center
- Estimated barb positions (pending verification):

| Barb | X (mm) | Y (mm) | Z (mm) | Notes |
|------|--------|--------|--------|-------|
| P1-inlet | ~43.2 | 35.00 | ~25 | Pump 1, lower barb (estimated) |
| P1-outlet | ~43.2 | 35.00 | ~44 | Pump 1, upper barb (estimated) |
| P2-inlet | ~116.8 | 35.00 | ~25 | Pump 2, lower barb (estimated) |
| P2-outlet | ~116.8 | 35.00 | ~44 | Pump 2, upper barb (estimated) |

**These positions are estimates.** The tube routing channels (Sub-F) must accommodate flexible tubing from these approximate exit points to the rear wall fittings. The flexibility of the silicone tubing provides tolerance for the imprecise barb positions.

---

## 4. Interface Boundary Summary

### Interface: Bosses to Floor (Sub-A)

All 4 bosses bond to the interior floor surface at Z = 3.00mm.

| Boss | Floor contact center (X, Y) | Contact OD |
|------|---------------------------|------------|
| P1-L | (18.48, 83.00) | ~8mm circle |
| P1-R | (67.93, 83.00) | ~8mm circle |
| P2-L | (92.08, 83.00) | ~8mm circle |
| P2-R | (141.53, 83.00) | ~8mm circle |

Mating feature: interior floor surface of Sub-A box shell, Z = 3.00.

### Interface: Cradles to Floor (Sub-A)

Both cradles bond to the interior floor surface at Z = 3.00mm via a solid rib base.

| Cradle | Floor contact footprint (X range, Y range) |
|--------|-------------------------------------------|
| Cradle 1 | X: 22.45..63.95, Y: 109.00..124.00 |
| Cradle 2 | X: 96.05..137.55, Y: 109.00..124.00 |

Mating feature: interior floor surface of Sub-A box shell, Z = 3.00.

### Interface: Bosses to Pump Bracket (off-the-shelf part)

Each boss top face at Z = 34.30 receives the pump mounting bracket. The bracket ear sits on the boss top face and is secured with an M3 x 8mm SHCS threading into the heat-set insert.

| Boss | Top face center (X, Y, Z) | Accepts |
|------|--------------------------|---------|
| P1-L | (18.48, 83.00, 34.30) | M3 x 5.7mm heat-set insert |
| P1-R | (67.93, 83.00, 34.30) | M3 x 5.7mm heat-set insert |
| P2-L | (92.08, 83.00, 34.30) | M3 x 5.7mm heat-set insert |
| P2-R | (141.53, 83.00, 34.30) | M3 x 5.7mm heat-set insert |

Mating feature: Kamoer KPHM400 mounting bracket, M3 through-holes at 49.45mm c-c.

### Interface: Cradles to Motor Body (off-the-shelf part)

Each cradle semicircular inner surface receives the motor cylinder (~35mm OD).

| Cradle | Arc center (X, Z) at Y=116.50 | ID |
|--------|-------------------------------|-----|
| Cradle 1 | (43.20, 34.30) | 35.50mm |
| Cradle 2 | (116.80, 34.30) | 35.50mm |

Mating feature: Kamoer KPHM400 motor body, ~35mm cylindrical OD.

### Interface: Sub-C to Sub-F (tube routing channels)

Tube barb exits at approximately Y = 35.00, near pump centerlines (X = 43.20 and 116.80). The tube routing channels (Sub-F) must originate near these points and route rearward to the fitting bore array (Sub-D) at the rear wall. The channels must pass around the boss positions at Y = 83.00 — routing laterally to avoid the boss footprints.

---

## 5. Transform Summary

```
Sub-C frame = Tray frame (identity transform, no rotation or translation)

Verification points:
  P1-L boss at tray (18.48, 83.00, 34.30) — 13.48mm from left wall inner, 74.50mm from rear wall inner ✓
  P2-R boss at tray (141.53, 83.00, 34.30) — 13.47mm from right wall inner, 74.50mm from rear wall inner ✓
  Pump center axis at Z=34.30 — 31.30mm above floor (= half of 62.6mm pump head) ✓
  Pump pair symmetric about X=80.0 — (43.20 + 116.80) / 2 = 80.00 ✓
  Mounting hole spacing per pump — 67.93 - 18.48 = 49.45mm, 141.53 - 92.08 = 49.45mm ✓
```

---

## 6. Dimensional Summary Table

All values in tray reference frame (mm).

| Parameter | Value | Source |
|-----------|-------|--------|
| Pump 1 centerline X | 43.20 | Derived: centered pair with 5mm gap |
| Pump 2 centerline X | 116.80 | Derived: centered pair with 5mm gap |
| Bracket plane Y | 83.00 | Derived: pump front at Y=35 + 48mm head depth |
| Bracket hole center Z | 34.30 | Derived: floor + half pump head height |
| Boss P1-L (X, Y) | (18.48, 83.00) | Derived: centerline - 24.725 |
| Boss P1-R (X, Y) | (67.93, 83.00) | Derived: centerline + 24.725 |
| Boss P2-L (X, Y) | (92.08, 83.00) | Derived: centerline - 24.725 |
| Boss P2-R (X, Y) | (141.53, 83.00) | Derived: centerline + 24.725 |
| Boss height (floor to top) | 31.30 | Derived: Z_hole - Z_floor |
| Motor cradle Y | 116.50 | Derived: midpoint of motor body |
| Motor cradle ID | 35.50 | Design: ~35mm motor + 0.5mm clearance |
| Motor cradle wall | 3.00 | Per decomposition |
| Motor cradle arc center Z | 34.30 | Same as pump center axis |
| Pump head bottom Z | 3.00 | Rests on floor |
| Pump head top Z | 65.60 | 3.00 + 62.6 |
| Top clearance (to Z=72) | 6.40 | Lid space |
| Wall clearance (each side) | 3.90 | Bracket edge to wall inner |
| Inter-pump bracket gap | 5.00 | Design choice |
| Motor nub tip Y | 151.48 | 35.00 + 116.48 |
| Front edge clearance | 3.52 | 155.00 - 151.48 |
