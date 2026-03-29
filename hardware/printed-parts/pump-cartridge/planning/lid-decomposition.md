# Lid — Sub-Component Decomposition

## Decision: Pass-Through

This part is a single geometric paradigm. No decomposition needed.

The lid is a flat rectangular panel (~160 x 155 x ~4 mm) with snap tabs along both long edges and tab pockets on the front edge. Every feature is prismatic extrude-and-cut:

- **Plate body:** rectangular box extrusion
- **Snap tabs (8 total, 4 per long edge):** small cantilever tab extrusions along the left and right edges, engaging the tray's detent ridges (tray Sub-H)
- **Bezel tab pockets:** small rectangular recesses cut into the front edge where the front bezel's lid-edge snap tab attaches
- **Stiffening ribs (if needed):** straight rectangular extrusions on the underside, running between the long edges

No feature requires revolves, sweeps, or lofts. No feature is geometrically independent enough to justify a separate sub-component -- the snap tabs are integral to the plate edges, and the pockets are simple cuts into those same edges. The total feature count is low. A single CadQuery agent handles the entire lid as one extrude-and-cut script.

---

## Feature Inventory (for downstream steps)

All features from the concept, accounted for:

| Feature | Paradigm | Notes |
|---------|----------|-------|
| Flat rectangular plate body | Box extrusion | ~160 x 155 x ~4 mm, the base solid |
| Snap tabs, left edge (x4) | Extruded cantilever tabs | Engage tray Sub-H detent ridges on left side wall interior |
| Snap tabs, right edge (x4) | Extruded cantilever tabs | Engage tray Sub-H detent ridges on right side wall interior |
| Bezel tab pocket(s), front edge | Rectangular pocket cuts | Receiving features for front bezel's lid-edge snap tab |
| Stiffening ribs (underside, optional) | Extruded ribs | Straight ribs spanning the underside to close the torsion box and stiffen the panel |

No feature is orphaned. Every feature described in the concept for Part #2 (Lid) appears in exactly one row above.

---

## Interface Summary

| Interface | Mating Part | Geometry | Description |
|-----------|-------------|----------|-------------|
| Snap tabs to tray detent ridges | Tray (Sub-H) | 8 cantilever tabs engaging 8 small ridges on tray side wall interiors near top edge | Lid seats flat on tray top edges; tabs deflect during insertion and click over ridges |
| Bezel tab pocket(s) | Front bezel | Rectangular recess(es) on lid front edge | Bezel's lid-edge snap tab engages this pocket for retention |
| Lid underside to tray top edges | Tray (Sub-A) | Flat rectangular bearing surfaces along both long edges and rear edge | Lid rests on the top edges of the tray walls, closing the open top |
