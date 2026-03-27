# Valve Rack Architecture

The valve rack holds 10 Beduan 2-way NC solenoid valves in a 5-wide x 2-high grid, mounted directly behind the cartridge dock back wall. It is the physical mounting structure for the valve subsystem defined in `../../../planning/research/valve-architecture.md` (flow routing, operating modes, valve truth table).

---

## 1. Why 5x2 Grid

10 valves must fit within the 212mm interior width of the enclosure. The valves are T-shaped (32.71mm wide), so a single row of 10 would need ~370mm -- far too wide. Two rows of 5:

- Row width: 4 × 37mm pitch + 32.71mm body = 180.71mm, centered in 212mm (15.6mm margin per side)
- Row height: 56mm per valve × 2 rows + 4mm gap = 116mm
- Fits behind the 148mm-wide cartridge dock with room for mounting flanges on either side

A 2x5 layout (2 wide, 5 high) was rejected: 2 valves wide = only 69mm span (wastes width), and 5 high = 284mm (exceeds available height between dock ceiling at Z=84 and bag cradle).

---

## 2. Valve Orientation

Each valve is oriented with:
- **Long axis (port-to-port, 50.84mm) along Y** (depth) -- tube ports face front (toward dock) and rear (toward bags/back panel)
- **Solenoid coil on top (+Z)** -- spade connectors accessible from above
- **Width (32.71mm) along X** -- valves tile side-by-side across the enclosure width

This orientation was chosen because:
1. Tube ports face the same direction as all other fluid connections (dock back wall forward, bags/back panel rearward)
2. The narrow 32.71mm body width enables tight X-pitch (37mm c-t-c) for 5 across
3. Spade connectors extend along Y (parallel to tubes), so wiring access is from front/rear -- NOT requiring extra X clearance between valves

---

## 3. Position in Enclosure

The rack sits in the depth stack between the dock back wall and the tube routing zone:

| Y range | Zone |
|---------|------|
| 4-134 | Cartridge dock |
| 134-169 | Dock back wall (tube stubs, pogo mount) |
| 169-224 | **Valve rack** (55mm depth: 50.84mm valve + clearance) |
| 224-296 | Tube routing to bags / back panel |

The rack frame spans X=16 to X=197 (181mm, centered) and Z=4 to Z=120 (116mm, sitting on enclosure floor). The top of the rack (Z=120) extends above the cartridge slot (Z=84), so the rack is behind and above the dock back wall -- no interference.

See `../../../planning/spatial-layout.md` for full coordinate table.

---

## 4. Mounting and Retention

The Beduan valve has **no built-in mounting features** (no tabs, flanges, ears, or screw holes). The rack must provide all retention:

- **Cradle saddle:** T-shaped profile matching the valve's T-shape. The horizontal cradle supports the white valve body (32.71W × ~19.4H mm) from below and on the sides. A vertical slot above the saddle clears the centered solenoid coil (31.41mm wide).
- **Snap-over retention clips:** 2 per valve, spaced along the Y axis, gripping the white valve body sides. Spring past the body's 32.71mm width and click into place.
- **No screws per valve** -- snap-fit only for tool-free valve replacement.

The rack frame itself mounts to the enclosure floor and/or walls via M3 screws into heat-set inserts.

---

## 5. Wiring

20 wires total (12V + GND per valve). Solenoid spade connectors are at the top of each valve, extending along Y. Female spade crimp connectors slide on/off along Y (front-to-back direction).

Cable routing channels run along the rack sides (X edges) and between rows (Z gap). Wires route up to the electronics zone (Z=326-396, Y=200-296) above and behind the bags.

---

## 6. Related Documents

- **Valve geometry:** `../../../off-the-shelf-parts/beduan-solenoid/extracted-results/geometry-description.md` -- complete physical geometry of the Beduan valve with ASCII art views, caliper measurements, and mounting considerations
- **Valve research:** `research/beduan-valve-geometry.md` -- spade connector orientation analysis, QC fitting direction, wiring implications
- **Flow routing:** `../../../planning/research/valve-architecture.md` -- the 10-valve fluid schematic, operating modes, valve truth table
- **Rack parts:** `parts.md` -- structured BOM for the rack frame (custom 3D printed) and valve (purchased)
- **Enclosure context:** `../../../planning/spatial-layout.md` -- master coordinate table showing rack position in enclosure
