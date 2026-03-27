# Valve Rack Parts Catalog

Structured parts list for the 5x2 valve rack assembly. Every dimension and interface is stated explicitly for downstream CAD geometry generation.

**Coordinate system:** Rack-local origin at the front-bottom-left corner of the rack frame. X = width (positive rightward). Y = depth (positive rearward, toward bags). Z = height (positive upward). In enclosure coordinates, the rack origin is approximately at (X=16, Y=169, Z=4) -- see `../../../planning/spatial-layout.md`.

See `architecture.md` for design rationale and layout decisions.

For detailed geometry of the Beduan solenoid valve (the component held by this rack), see `../../../off-the-shelf-parts/beduan-solenoid/extracted-results/geometry-description.md`.

For engineering drawing standards, see `../../../planning/drawing-standards.md`.

---

## 3D Printed Parts

### Part: Valve Rack Frame

- **Type:** 3D printed
- **Material:** PETG or ABS
- **Envelope:** 181W x 55D x 116H mm (rack-local coordinates)
- **Features:**
  - Holds 10 Beduan solenoid valves in a 5-wide x 2-high grid
  - **Grid layout:**
    - Valve pitch in X: 37mm center-to-center (32.71mm body + 4.29mm gap)
    - 5 valves per row: span = 4 × 37 + 32.71 = 180.71mm ≈ 181mm
    - Row 1 (bottom): Z = 0 to 56mm
    - Row 2 (top): Z = 60 to 116mm (4mm gap between rows)
    - Valve centers in X: 16.36, 53.36, 90.36, 127.36, 164.36 mm (rack-local)
    - Valve centers in Z: 28mm (row 1), 88mm (row 2) (rack-local)
  - **Cradle profile (per valve slot):**
    - T-shaped cross-section matching the Beduan valve's T-shaped profile
    - Horizontal saddle: supports white valve body (32.71W x ~19.4H mm) from below and on sides
    - Vertical slot above saddle: clears solenoid coil housing (31.41mm wide), open at top
    - Saddle inner width: ~33.5mm (32.71mm body + ~0.4mm clearance per side)
    - Saddle depth (Y): full 55mm rack depth, open at both Y ends for tube port access
    - Saddle wall height: ~12mm (enough to grip white body sides without interfering with coil mounting flange)
  - **Retention clips:**
    - 2 snap-over clips per valve, positioned at Y ≈ 12mm and Y ≈ 43mm (spaced along valve length)
    - Clips span across the top of the white valve body, gripping sides
    - Clip must clear the centered solenoid coil -- bridge shape with cutout for coil pass-through
    - Snap-fit: deflect outward during valve insertion, click over body shoulders
  - **Cable routing:**
    - Channels along left and right edges (X = 0 and X = 181) for solenoid wires
    - Cross-channel in the 4mm gap between row 1 and row 2 (Z = 56-60mm)
    - Wire exits at top-rear for routing to electronics zone
  - **Mounting flanges:**
    - Bottom face: 4x M3 heat-set insert bosses for floor mounting (2 per side, at Y ≈ 10mm and Y ≈ 45mm)
    - Optional side flanges for wall mounting
- **Interfaces:**
  - Mounts to enclosure floor (Z=4 in enclosure coordinates) via M3 screws
  - Valve QC fittings protrude from both Y faces of the rack -- front ports face dock back wall, rear ports face bags/back panel
  - Rack centered in enclosure width: enclosure X = 16 to 197 (centered in 212mm interior)
  - Spade connectors at top of each valve, accessible from front or rear (Y direction)
- **Quantity:** 1

---

## Purchased Parts (Mounted in Rack)

### Part: Beduan Solenoid Valve (2-Way NC, 1/4" QC)

- **Type:** Purchased
- **Source:** Beduan B07NWCQJK9 (~$9 each)
- **Quantity:** 10
- **Detailed geometry:** See `../../../off-the-shelf-parts/beduan-solenoid/extracted-results/geometry-description.md`

**Key dimensions for rack design (caliper-verified):**

| Dimension | Value | Notes |
|-----------|-------|-------|
| White body width (X) | 32.71 mm | Controls rack slot width and X-pitch |
| White body depth (Y, port-to-port) | 50.84 mm | Controls rack depth |
| White body height (Z) | ~19.4 mm | Derived: 56.00 - 36.63 |
| Metal coil width (X) | 31.41 mm | Narrower than body, centered -- controls slot opening width |
| Metal-to-spade-tip height (Z) | 36.63 mm | Coil + connector housing height above white body |
| Total height (Z) | 56.00 mm | Bottom of body to top of spade tips -- controls row pitch |
| Total depth with QC fittings (Y) | ~68 mm | Body + QC stub protrusion on both ends |
| Weight | 113 g | 10 valves = 1.13 kg total |

**Assembly shape:** T-shaped profile in the X-Z plane. The white valve body is the wide horizontal bar; the metal solenoid coil rises vertically from its center. Not a rectangular block -- the rack cradle must match this T-profile.

**Spade connector orientation (critical for wiring access):**
- Two 1/4" male spade tabs protrude from the top of the solenoid coil
- Flat faces of both blades are **parallel to the X-Z plane** (blade width spans X)
- Female connectors slide on/off **along Y** (tube flow direction)
- Tabs do NOT extend in X -- the 37mm X-pitch does not need extra spade clearance
- Tab spacing: ~8-10mm center-to-center in X (visual estimate, needs caliper verification)

**QC fitting orientation:**
- Both 1/4" quick-connect tube ports extend along **Y** (front-back)
- Blue collet ring on inlet side, plain white on outlet side
- Port stub protrusion beyond white body: not yet measured

---

## Assembly Notes

### Valve Installation
1. Slide valve into cradle from above (coil-first into the vertical slot)
2. Press white body down into horizontal saddle until retention clips snap over
3. Repeat for all 10 positions

### Tube Connection Order
1. Mount all 10 valves in rack
2. Mount rack in enclosure
3. Connect front-facing QC ports (valve inlets, toward dock)
4. Connect rear-facing QC ports (valve outlets, toward bags/back panel)
5. Attach spade connectors to solenoid terminals from front or rear

### Valve Assignment to Grid Positions

Grid position numbering (rack-local, viewed from front):

```
Row 2 (top):    v6    v7    v8    v9    v10
                [0,1] [1,1] [2,1] [3,1] [4,1]

Row 1 (bottom): v1    v2    v3    v4    v5
                [0,0] [1,0] [2,0] [3,0] [4,0]
```

See `../../../planning/research/valve-architecture.md` for valve function assignments (v1=dispense line 1, v2=dispense line 2, etc.) and operating mode truth table.
