# Rear Wall Plate — Decomposition (Step 4d)

## Decision: Pass Through — No Decomposition Needed

This part is a single geometric paradigm. No decomposition needed.

The rear wall plate is a flat rectangular plate with cylindrical bores and simple prismatic surface features. Every feature is an extrude-and-cut or extrude-and-union operation on a single base plate:

- **Base body:** Rectangular plate — a single box extrusion
- **4x JG fitting pockets:** Cylindrical bores (stepped profile with chamfers) — revolved cuts into the plate
- **Pogo contact pads:** Flat rectangular recesses or bosses on one face — box unions or cuts
- **2x guide pin bores:** Simple cylindrical press-fit holes — cylinder cuts
- **2x link rod pass-through holes:** Simple cylindrical clearance holes — cylinder cuts
- **4x corner snap tabs:** Small rectangular prisms with chamfered lead-ins — box unions with chamfer cuts

All features share a single base plane (the plate body) and are either perpendicular bores through the plate thickness or surface features on one of its two faces. No feature requires sweeps, lofts, revolves of complex profiles, or any operation beyond basic extrude-and-cut / extrude-and-union on the plate body. The stepped JG fitting bores use a revolved axial profile, but this is a standard bore technique within the prismatic paradigm (the bore axis is perpendicular to the plate face, same as all other holes).

A single CadQuery agent handles this as one script with no geometric complexity concerns.
