# Cartridge Pump Tray

See `../../../planning/cartridge-architecture.md` for cartridge system design rationale.

**Coordinate system:** Shared with cartridge shell — origin at exterior front-bottom-left corner. Tray sits at Z=4 inside shell.

---

## 3D Printed Part: Pump Tray

- **Type:** 3D printed
- **Material:** PETG
- **Envelope:** 138W x 120D x 6H mm (fits inside 140mm interior with 1mm clearance per side)
- **Features:**
  - Flat plate, prints horizontally for maximum screw boss strength
  - 4x M3 heat-set insert bosses for pump bracket mounting (boss OD: 8mm, boss height: 6mm, pilot hole: 4.0mm) — 2 per pump
  - Mounting hole pattern per pump: 49.45mm center-to-center, one axis (caliper-verified), 3.13mm hole diameter. Bracket has 2x M3 through-holes (one per ear).
  - 4x printed C-clips for BPT tubing strain relief (clip ID: 8.3mm for 8.0mm OD BPT tube, clip opening: 6.5mm for snap-in)
  - 4x printed C-clips for 1/4" hard tubing strain relief (clip ID: 6.65mm for 6.35mm OD tube, clip opening: 4.85mm for snap-in)
  - Wire routing channel along one edge: 5mm wide x 3mm deep U-channel
  - 4x M3 through-holes at corners for mounting tray to shell (clearance holes: 3.4mm)
  - Tray edge locating tabs that key into shell wall slots
- **Interfaces:**
  - Pump brackets bolt to tray via M3 screws into heat-set inserts
  - Tray bolts to shell ledges via 4x M3 screws
  - Locating tabs engage shell wall slots for lateral alignment
- **Quantity:** 1
- **Open:** Perpendicular axis mounting hole spacing (if bracket has 2x2 pattern). Whether rubber grommet isolators are needed.

---

## Purchased Parts Mounted on Tray

### Kamoer KPHM400-SW3B25 Peristaltic Pump (x2)

Full geometry: `../../../off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md`

- **Envelope:** Pump head 62.6mm square (caliper-verified), bracket ears bring width to 68.6mm. Total length 116.48mm with motor shaft nub (caliper-verified).
- **Weight:** 306g each
- **Mounting:** Metal bracket with 2x M3 through-holes, 49.45mm center-to-center (caliper-verified)
- **Tube exits:** From pump head face (front), inlet and outlet on same face
- **Motor leads:** Exit from rear of motor housing

### M3 x 8mm Socket Head Cap Screws (x8)

- 4 for pump brackets to tray, 4 for tray to shell

### M3 x 5mm Brass Heat-Set Inserts (x8)

- 4 in tray bosses (pump brackets), 4 in shell ledges (tray mounting)
- Install at 245C with soldering iron

### Rubber Grommet Isolators (x4, optional)

- ~6-8mm OD, ~3mm ID, ~2mm thick
- Between pump bracket and tray — try rigid mount first

---

## Related Documents

- **Drawing standards:** `../../../planning/drawing-standards.md`
- **Pump geometry:** `../../../off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md`
- **Pump mounting research:** `research/pump-mounting.md`
- **Shell interface:** `../../cartridge-shell/planning/parts.md`
