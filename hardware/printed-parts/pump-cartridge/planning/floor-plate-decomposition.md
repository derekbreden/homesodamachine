# Floor Plate — Sub-Component Decomposition

## Decision: Pass-Through

This part is a single geometric paradigm. No decomposition needed.

The floor plate is a simple flat rectangular panel (~80 x 60 x 4 mm) with two M3 counterbore holes. Every feature is prismatic extrude-and-cut:

- **Plate body:** rectangular box extrusion
- **M3 counterbore holes (x2):** cylindrical through-holes with counterbore pockets on the underside for M3 SHCS heads, positioned to align with heat-set inserts in the tray's floor ribs

No feature requires revolves, sweeps, or lofts. The entire part is two cuts into a flat box. This is the simplest part in the cartridge and the lowest possible feature count — a single CadQuery agent handles it trivially as one extrude-and-cut script. Decomposing this part would be over-engineering that adds pipeline complexity with zero benefit.

---

## Feature Inventory (for downstream steps)

All features from the concept, accounted for:

| Feature | Paradigm | Notes |
|---------|----------|-------|
| Flat rectangular plate body | Box extrusion | ~80 x 60 x 4 mm, the base solid |
| M3 counterbore hole #1 | Cylindrical bore + counterbore cut | M3 clearance through-hole (3.4 mm) with counterbore for SHCS head (5.5 mm dia x 3.0 mm deep). Screws into heat-set insert in tray floor rib. |
| M3 counterbore hole #2 | Cylindrical bore + counterbore cut | Identical to hole #1, second attachment point |
| Bottom-edge chamfers (optional) | 45-degree chamfer cuts | 0.3 mm x 45-degree chamfers on bottom edges to mitigate elephant's foot on the mating surface (per requirements.md) |

No feature is orphaned. Every feature described in the concept for Part #5 (Floor Plate) appears in exactly one row above.

---

## Interface Summary

| Interface | Mating Part | Geometry | Description |
|-----------|-------------|----------|-------------|
| M3 screw holes to tray floor rib inserts | Tray | 2x M3 counterbore through-holes aligning with 2x M3 x 5.7 mm heat-set inserts in tray floor ribs | Screws pass through floor plate and thread into inserts. Infrequent access — only removed for pump installation from below. |
| Top face bearing surface to tray floor ribs | Tray | Flat rectangular bearing surfaces where floor plate top face contacts the underside of tray floor ribs | Floor plate sits flush against tray floor ribs, closing the pump zone from below |
